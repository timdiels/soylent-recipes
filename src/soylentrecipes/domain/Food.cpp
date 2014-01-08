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

#include <iostream>
#include <assert.h>
#include "Food.h"

using namespace std;
using namespace alglib;

Food::Food(int id, std::string description, const alglib::real_1d_array& nutrient_values)
:   id(id), description(description), nutrient_values(nutrient_values), normalised_nutrient_values(nutrient_values)
{
    double length = sqrt(vdotproduct(&nutrient_values[0], &nutrient_values[0], nutrient_values.length()));
    assert(length > 0.0);  // a food with no nutritional value is weird, and useless to us
    for (int i=0; i < normalised_nutrient_values.length(); i++) {
        normalised_nutrient_values[i] /= length;
    }
}

int Food::get_id() const {
    return id;
}

string Food::get_description() const {
    return description;
}

double Food::get_nutrient_value(int id) const {
    return nutrient_values[id];
}

const real_1d_array& Food::as_matrix() const {
    return nutrient_values;
}

#include <iostream>
double Food::get_similarity(const Food& other) const {
    double dotprod = fabs(vdotproduct(&normalised_nutrient_values[0], &other.normalised_nutrient_values[0], normalised_nutrient_values.length()));
    assert(dotprod < 1 + 1e-6);
    return dotprod;
}
