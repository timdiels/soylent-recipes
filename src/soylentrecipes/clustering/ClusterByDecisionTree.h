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

#pragma once

#include <valarray>
#include "util.h"

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
        // TODO we're not normalising the points!
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

