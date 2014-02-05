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
 * Cluster using k-means
 *
 * http://www.alglib.net/dataanalysis/clustering.php#header6
 *
 * k=100
 *
 * Data is normalised before-hand (to prevent accidental weighting of features).
 */
class KMeansClustering
{
public:
    void cluster(FoodDatabase&);
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
#include <libalglib/dataanalysis.h>

using namespace std;
using namespace alglib;

void KMeansClustering::cluster(FoodDatabase& db) {
    vector<Item> items;
    real_2d_array points;
    load_data(db, items, points);

    clusterizerstate s;
    kmeansreport report;
    clusterizercreate(s);
    clusterizersetpoints(s, points, 2);
    clusterizersetkmeanslimits(s, 5, 0);
    clusterizerrunkmeans(s, 50, report);

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

