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

#include <map>
#include <vector>
#include <libalglib/ap.h>
#include <soylentrecipes/data_access/FoodDatabase.h>

/**
 * Cluster using k-means, and ahc
 *
 * Data is normalised before-hand (to prevent accidental weighting of features).
 */
class Clustering
{
public:
    void cluster(FoodDatabase&);

private:
    class Normalizer;

    /**
     * Evaluate clustering
     *
     * Returns some kind of score (higher is better)
     */
    double evaluate(const alglib::real_2d_array& points, const alglib::integer_1d_array& row_to_cluster, const alglib::real_2d_array& centroids);

    /**
     * Cluster using agglomerative hierarchical clustering
     *
     * http://www.alglib.net/dataanalysis/clustering.php#header0
     * Using L2 norm, unweighted average linkage. 
     */
    void ahc_clustering(const alglib::real_2d_array& points, int k, alglib::integer_1d_array& row_to_cluster, alglib::real_2d_array& centroids);

    /**
     * Cluster using k-means
     *
     * http://www.alglib.net/dataanalysis/clustering.php#header6
     */
    void kmeans_clustering(const alglib::real_2d_array& points, int k, alglib::integer_1d_array& row_to_cluster, alglib::real_2d_array& centroids);

    /**
     * Load data points
     */
    void load_data(FoodDatabase& db, alglib::real_2d_array& points, std::map<int, int>& row_to_id);
};

class Clustering::Normalizer
{
public:
    Normalizer(alglib::real_2d_array& points);

    void abnormalize(double* values);

private:
    std::vector<double> min_value;
    std::vector<double> max_value;
};


