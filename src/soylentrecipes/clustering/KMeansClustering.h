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

#include "util.h"

/**
 * Cluster using k-means, and ahc
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

#include <map>
#include <vector>
#include <algorithm>
#include <libalglib/dataanalysis.h>

using namespace std;
using namespace alglib;

//typedef void clustering(const real_2d_array& points, int k, integer_1d_array& row_to_cluster, real_2d_array& centroids);

void evaluate(const real_2d_array& points, const integer_1d_array& row_to_cluster, const real_2d_array& centroids) {
    vector<double> total_errors(centroids.rows(), 0.0);
    vector<size_t> counts(centroids.rows(), 0);
    real_1d_array tmp;
    tmp.setlength(points.cols());
    for (int i=0; i < row_to_cluster.length(); i++) {
        int ci = row_to_cluster[i];

        vmove(&tmp[0], &points[i][0], tmp.length());
        vsub(&tmp[0], &centroids[ci][0], tmp.length());
        total_errors.at(ci) += vdotproduct(&tmp[0], &tmp[0], tmp.length());

        counts.at(ci)++;
    }

    cout << "Cluster average error: " << endl;
    for (int i=0; i < centroids.rows(); i++) {
        cout << total_errors.at(i) / counts.at(i) << endl;
    }
    cout << endl;

    double total_error = accumulate(total_errors.begin(), total_errors.end(), 0.0);
    cout << "Total error: " << total_error << endl;
    cout << "Average error: " << total_error / accumulate(counts.begin(), counts.end(), 0) << endl;
}

/**
 * Cluster using k-means
 *
 * http://www.alglib.net/dataanalysis/clustering.php#header6
 */
void kmeans_clustering(const real_2d_array& points, int k, integer_1d_array& row_to_cluster, real_2d_array& centroids) {
    clusterizerstate s;
    kmeansreport report;
    clusterizercreate(s);
    clusterizersetpoints(s, points, 2);
    clusterizersetkmeanslimits(s, 5, 0);
    clusterizerrunkmeans(s, k, report);

    if (report.terminationtype != 1) {
        throw runtime_error("Clustering failed");
    }

    row_to_cluster = report.cidx;
    centroids = report.c;
}

void KMeansClustering::cluster(FoodDatabase& db) {
    // load and prepare data
    real_2d_array points;
    map<int, int> row_to_id;

    load_data(db, points, row_to_id);
    Normalizer normalizer(points);

    // run algorithms
    integer_1d_array cidx;
    real_2d_array c;
    const int k = 5;//TODO k=100 or 50 or so
    kmeans_clustering(points, k, cidx, c);
    evaluate(points, cidx, c);

    //ahc_clustering(points, k, cidx, c);
    //evaluate(cidx2, c2);

    /*if (2 better than 1) {
        swap
    }*/

    // pick best result
    // TODO

    // store in db
    for (int i=0; i<k; i++) {
        normalizer.abnormalize(&c[i][0]);

        vector<int> ids;
        for (int j=0; j<points.rows(); j++) {
            if (cidx[j] == i) {
                ids.push_back(row_to_id[j]);
            }
        }
        db.add_cluster(&c[i][0], &c[i][points.cols()], ids.begin(), ids.end());
    }
}

