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

#include <string>
#include <libalglib/stdafx.h>
#include <libalglib/linalg.h>

/**
 * A food (e.g. bread)
 */
class Food
{
public:
    Food(int id, std::string description, const alglib::real_1d_array& nutrient_values);

    int get_id() const;
    std::string get_description() const;
    double get_nutrient_value(int id) const;
    const alglib::real_1d_array& as_matrix() const;

private:
    int id;
    std::string description;
    alglib::real_1d_array nutrient_values;  // nutrient_values[i] = value associated with nutrient{id=i}
};
