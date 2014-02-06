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

#include <algorithm>
#include <iostream>
#include <libalglib/dataanalysis.h>
#include <boost/function_output_iterator.hpp>
#include "Clustering.h"

using namespace std;
using namespace alglib;

double Clustering::evaluate(const real_2d_array& points, const integer_1d_array& row_to_cluster, const real_2d_array& centroids) {
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
    double cluster_average_error_sum = 0.0;
    for (int i=0; i < centroids.rows(); i++) {
        double average_error = total_errors.at(i) / counts.at(i);
        cout << average_error << endl;
        cluster_average_error_sum += average_error;
    }
    cout << endl;

    double average_cluster_average_error = cluster_average_error_sum / centroids.rows();
    cout << "Average cluster average error: " << average_cluster_average_error << endl;

    double total_error = accumulate(total_errors.begin(), total_errors.end(), 0.0);
    cout << "Total error: " << total_error << endl;
    double average_total_error = total_error / accumulate(counts.begin(), counts.end(), 0);
    cout << "Average total error: " << average_total_error << endl;

    return -(average_cluster_average_error + 2 * average_total_error);
}

void Clustering::ahc_clustering(const real_2d_array& points, int k, integer_1d_array& row_to_cluster, real_2d_array& centroids) {
    // TODO does it use unweighted average linkage?
    clusterizerstate s;
    ahcreport report;
    clusterizercreate(s);
    clusterizersetpoints(s, points, 2);
    clusterizerrunahc(s, report);

    integer_1d_array cz;
    clusterizergetkclusters(report, k, row_to_cluster, cz);
    
    // calculate centroids
    centroids.setlength(k, points.cols());
    for (int i=0; i < centroids.rows(); i++) {
        fill(&centroids[i][0], &centroids[i][points.cols()], 0.0); // Note: fill per row as 2d matrix isn't necessarily contiguous
    }

    vector<size_t> counts(k, 0);
    for (int i=0; i < row_to_cluster.length(); i++) {
        int ci = row_to_cluster[i];
        vadd(&centroids[ci][0], &points[i][0], points.cols());
        counts.at(ci)++;
    }

    for (int ci=0; ci < k; ci++) {
        vmul(&centroids[ci][0], centroids.cols(), 1.0 / counts.at(ci));
    }
}

void Clustering::kmeans_clustering(const real_2d_array& points, int k, integer_1d_array& row_to_cluster, real_2d_array& centroids) {
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

void Clustering::cluster(FoodDatabase& db) {
    // load and prepare data
    real_2d_array points;
    map<int, int> row_to_id;

    load_data(db, points, row_to_id);
    Normalizer normalizer(points);

    // run algorithms
    const int k = 50; // note: lower values seem to do alright as well, strangely

    cout << "ahc clustering" << endl;
    integer_1d_array cidx2;
    real_2d_array c2;
    ahc_clustering(points, k, cidx2, c2);
    double score2 = evaluate(points, cidx2, c2);
    cout << endl;

    cout << "k-means clustering" << endl;
    integer_1d_array cidx;
    real_2d_array c;
    kmeans_clustering(points, k, cidx, c);
    double score1 = evaluate(points, cidx, c);

    // pick best clustering
    if (score2 > score1) {
        swap(cidx2, cidx);
        swap(c2, c);
    }

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

void Clustering::load_data(FoodDatabase& db, real_2d_array& points, map<int, int>& row_to_id) {
    points.setlength(db.food_count(),  db.nutrient_count());
    int current_row = 0;

    db.get_foods(boost::make_function_output_iterator([&points,&current_row,&row_to_id](FoodRecord r) {
        row_to_id[current_row] = r.id;
        copy(r.nutrient_values.begin(), r.nutrient_values.end(), &points[current_row][0]);
        current_row++;
    }));
}

/////// Normalizer ////////

Clustering::Normalizer::Normalizer(real_2d_array& points) {
    // get minmax
    min_value.resize(points.cols(), INFINITY);
    max_value.resize(points.cols(), -INFINITY);
    for (int i=0; i < points.rows(); i++) {
        for (int j=0; j<points.cols(); j++) {
            min_value.at(j) = min(points[i][j], min_value.at(j));
            max_value.at(j) = max(points[i][j], max_value.at(j));
        }
    }

    // normalise nutrient values to [0, 1]
    for (int i=0; i < points.rows(); i++) {
        for (int j=0; j<points.cols(); j++) {
            points[i][j] = (points[i][j] - min_value.at(j)) / max(max_value.at(j) - min_value.at(j), 1.0);
        }
    }
}

void Clustering::Normalizer::abnormalize(double* values) {
    for (int j=0; j<min_value.size(); j++) {
        values[j] = values[j] * max(max_value.at(j) - min_value.at(j), 1.0) + min_value.at(j);
    }
}

