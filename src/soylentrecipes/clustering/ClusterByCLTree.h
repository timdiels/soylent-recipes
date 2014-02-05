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
 * Cluster by variant of CLTree algorithm
 *
 * ftp://ftp.cse.buffalo.edu/users/azhang/disc/disc01/cd1/out/papers/cikm/p20.pdf
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
    size_t dimension_count;

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

using namespace std;

// TODO make class private (not its fields ^^)
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

////////////////////////////////////////////////

void ClusterByDecisionTree::cluster(FoodDatabase& db) {
    dimension_count = db.nutrient_count();

    // load items
    vector<Item> items;
    db.get_foods(boost::make_function_output_iterator([&items](FoodRecord& r) {
        valarray<double> values(r.nutrient_values.size());
        copy(r.nutrient_values.begin(), r.nutrient_values.end(), begin(values));
        items.emplace_back(r.id, values);
    }));

    // construct value_matrix
    vector<vector<pair<Item*, double>>> value_matrix(dimension_count); // matrix[dimension][item_row]
    copy(items.begin(), items.end(), boost::make_function_output_iterator([&value_matrix](Item& item) {
        for (int i=0; i < dimension_count; i++) {
            value_matrix.at(i).push_back(make_pair(&item, item.values[i]));
        }
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

    // start splitting
    auto pointer_to = [](Item& item) -> Item* {
        return &item;
    };
    vector<Item*> ptrs;
    auto ptrs_begin = boost::make_transform_iterator(items.begin(), pointer_to);
    auto ptrs_end = boost::make_transform_iterator(items.end(), pointer_to);
    CALLGRIND_START_INSTRUMENTATION;
    split(ptrs_begin, ptrs_end);
    CALLGRIND_STOP_INSTRUMENTATION;
    CALLGRIND_DUMP_STATS;
    cout << endl << "Average error: " << this->total_error / distance(items.begin(), items.end()) << endl;
}

// TODO might also want to rerun later with L2 norm instead of L1 norm for distance
/**
 * ForwardIterator: iter to pointer of item
 */
template <class ForwardIterator>
void ClusterByDecisionTree::split(ForwardIterator items_begin, ForwardIterator items_end) {
    cout << "!";
    if (items_begin == items_end) return;

    auto deref_begin = boost::make_indirect_iterator(items_begin);
    auto deref_end = boost::make_indirect_iterator(items_end);

    // check split stop criterium
    double total_error = get_total_error(deref_begin, deref_end);
    double average_error = total_error / distance(deref_begin, deref_end); // note: = average distance to centroid

    //cout << average_error << " ";
    if (average_error <= max_average_error) {
        cout << distance(items_begin, items_end) << ": ";
        cout << average_error << endl;
        this->total_error += total_error;
        // TODO cout cluster for debugging info
        return;  // stop splitting
    }

    // pick best split: split on average
    valarray<double> centroid = get_centroid(deref_begin, deref_end);
    //copy(begin(centroid), end(centroid), ostream_iterator<double>(cout, ","));
    //cout << endl;
    size_t dimension_count = centroid.size();
    double smallest_error = INFINITY;
    vector<Item*> items(items_begin, items_end);
    vector<Item*> items1;
    vector<Item*> items2;
    if (true) { // split on each value of each item
        for (auto item_ : items) {
            for (int i=0; i < dimension_count; i++) {
                auto predicate = [&item_, i] (const Item* item) -> bool {
                    return item_->values[i] <= item->values[i];
                };
                auto separator = partition(items.begin(), items.end(), predicate);
                double total_error = 0;
                //double total_error = get_total_error(boost::make_indirect_iterator(items.begin()), boost::make_indirect_iterator(separator));
                //total_error += get_total_error(boost::make_indirect_iterator(separator), boost::make_indirect_iterator(items.end()));

                if (total_error < smallest_error) {
                    smallest_error = total_error;
                    items1.assign(items.begin(), separator);
                    items2.assign(separator, items.end());
                }
            }
            cout << ".";
            cout.flush();
        }
    } else { // split on average
        for (int i=0; i < dimension_count; i++) {
            auto ge_centroid = [&centroid, i] (const Item* item) -> bool {
                return centroid[i] <= item->values[i];
            };
            auto separator = partition(items.begin(), items.end(), ge_centroid);
            double total_error = get_total_error(boost::make_indirect_iterator(items.begin()), boost::make_indirect_iterator(separator));
            total_error += get_total_error(boost::make_indirect_iterator(separator), boost::make_indirect_iterator(items.end()));

            if (total_error < smallest_error) {
                smallest_error = total_error;
                items1.assign(items.begin(), separator);
                items2.assign(separator, items.end());
            }
        }
    }

    split(items1.begin(), items1.end());
    split(items2.begin(), items2.end());
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
