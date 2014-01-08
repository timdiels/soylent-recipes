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

#include "Food.h"

using namespace std;

Food::Food(int id, std::string description, const alglib::real_1d_array& nutrient_values)
:   id(id), description(description), nutrient_values(nutrient_values)
{
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

const alglib::real_1d_array& Food::as_matrix() const {
    return nutrient_values;
}

