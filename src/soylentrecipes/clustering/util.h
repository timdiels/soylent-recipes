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

#include <vector>
#include <algorithm>
#include <boost/function_output_iterator.hpp>
#include <boost/iterator/transform_iterator.hpp>
//#include <libalglib/dataanalysis.h>
#include <libalglib/ap.h>

using namespace std;
using namespace alglib;

void load_data(FoodDatabase& db, real_2d_array& points, map<int, int>& row_to_id) {
    // load datapoints
    points.setlength(db.food_count(),  db.nutrient_count());
    int current_row = 0;

    db.get_foods(boost::make_function_output_iterator([&points,&current_row,&row_to_id](FoodRecord r) {
        row_to_id[current_row] = r.id;
        copy(r.nutrient_values.begin(), r.nutrient_values.end(), &points[current_row][0]);
        current_row++;
    }));
}

class Normalizer
{
public:
    Normalizer(real_2d_array& points);

    void abnormalize(double* values);

private:
    vector<double> min_value;
    vector<double> max_value;
};

Normalizer::Normalizer(real_2d_array& points) {
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

void Normalizer::abnormalize(double* values) {
    for (int j=0; j<min_value.size(); j++) {
        values[j] = values[j] * max(max_value.at(j) - min_value.at(j), 1.0) + min_value.at(j);
    }
}

