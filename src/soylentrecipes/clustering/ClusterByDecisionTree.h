/*
 * Copyright (C) 2014 by Tim Diels
 *
 * This file is part of soylent-recipes.
 *
 * soylent-recipes is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * soylent-recipes is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with soylent-recipes.  If not, see <http://www.gnu.org/licenses/>.
 */

#include <valarray>

/**
 * Cluster using a decision tree.
 */
class ClusterByDecisionTree
{
public:
    void cluster(FoodDatabase&);

private:
    void sort(std::vector<Food*>&, int dimension); // sort foods by dimension'th nutrition value

    template <class ForwardIterator>
    void split(ForwardIterator items_begin, ForwardIterator items_end);

    template <class ForwardIterator>
    std::valarray<double> get_centroid(ForwardIterator items_begin, ForwardIterator items_end);

    template <class ForwardIterator>
    double get_total_error(ForwardIterator items_begin, ForwardIterator items_end);

private:
    const double max_average_error = 0.1; // the max average member distance to a leaf cluster's centroid (a stop criterium for splitting) (L1 norm distance)

    // stats
    double total_error = 0.0;
};

//////
// cpp TODO
//////

#include <vector>
#include <algorithm>
#include <boost/function_output_iterator.hpp>
#include <boost/iterator/indirect_iterator.hpp>
#include <boost/iterator/transform_iterator.hpp>
#include <boost/iterator/filter_iterator.hpp>
#include <valgrind/callgrind.h>
#include <libalglib/dataanalysis.h>

using namespace std;
using namespace alglib;

class Item {
public:
    Item(int id, valarray<double> values);
    static valarray<double> get_values(const Item& item);

public:
    int id;
    valarray<double> values;
};

Item::Item(int id, valarray<double> values)
:   id(id), values(values)
{
}

valarray<double> Item::get_values(const Item& item) {
    return item.values;
}
void ClusterByDecisionTree::cluster(FoodDatabase& db) {
    vector<Item> items;

    // load datapoints
    real_2d_array points;
    points.setlength(db.food_count(),  db.nutrient_count());
    int current_row = 0;

    db.get_foods(boost::make_function_output_iterator([&items,&points,&current_row](FoodRecord r) {
        copy(r.nutrient_values.begin(), r.nutrient_values.end(), &points[current_row++][0]);

        valarray<double> values(r.nutrient_values.size());
        copy(r.nutrient_values.begin(), r.nutrient_values.end(), begin(values));
        items.emplace_back(r.id, values);
    }));

    // get minmax
    auto dimension_count = items.front().values.size();
    vector<double> min_value(dimension_count, INFINITY);
    vector<double> max_value(dimension_count, -INFINITY);
    for (auto& item : items) {
        for (int i=0; i<dimension_count; i++) {
            min_value.at(i) = min(item.values[i], min_value.at(i));
            max_value.at(i) = max(item.values[i], max_value.at(i));
        }
    }

    // normalise nutrient values to [0, 1]
    for (auto& item : items) {
        for (int i=0; i<dimension_count; i++) {
            item.values[i] = (item.values[i] - min_value.at(i)) / max(max_value.at(i) - min_value.at(i), 1.0);
        }
    }

    CALLGRIND_START_INSTRUMENTATION;

    clusterizerstate s;
    kmeansreport report;
    clusterizercreate(s);
    clusterizersetpoints(s, points, 2);
    clusterizersetkmeanslimits(s, 5, 0);
    clusterizerrunkmeans(s, 50, report);

    CALLGRIND_STOP_INSTRUMENTATION;
    CALLGRIND_DUMP_STATS;

    cout << report.terminationtype << endl;
    assert(report.terminationtype == 1);

    double total_error = 0.0;
    for (int i=0; i<report.k; i++) {
        vector<Item> cluster;
        for (int j=0; j<items.size(); j++) {
            if (report.cidx[j] == i) {
                cluster.push_back(items.at(j));
            }
        }
        total_error += get_total_error(cluster.begin(), cluster.end());
    }

    cout << endl;
    cout << "Total error: " << total_error << endl;
    cout << "Average error: " << total_error / distance(items.begin(), items.end()) << endl;
}

template <class ForwardIterator>
valarray<double> ClusterByDecisionTree::get_centroid(ForwardIterator items_begin, ForwardIterator items_end) {
    assert(items_begin != items_end);
    auto values_begin = boost::make_transform_iterator(items_begin, Item::get_values);
    auto values_end = boost::make_transform_iterator(items_end, Item::get_values);
    return accumulate(values_begin, values_end, valarray<double>(values_begin->size())) / static_cast<double>(distance(values_begin, values_end));
}

template <class ForwardIterator>
double ClusterByDecisionTree::get_total_error(ForwardIterator items_begin, ForwardIterator items_end) {
    if (items_begin == items_end) return 0.0;

    auto centroid = get_centroid(items_begin, items_end);

    auto l2_norm_squared = [&centroid](const Item& item) {
        valarray<double> diff = centroid - item.values;
        return inner_product(begin(diff), end(diff), begin(diff), 0.0);
    };

    auto distances_begin = boost::make_transform_iterator(items_begin, l2_norm_squared);
    auto distances_end = boost::make_transform_iterator(items_end, l2_norm_squared);
    return accumulate(distances_begin, distances_end, 0.0);
}
