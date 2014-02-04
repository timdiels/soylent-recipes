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
#include <vector>
#include <libalglib/linalg.h>

/**
 * A food (e.g. bread)
 */
class Food
{
public:
    Food(int id, std::string description, const alglib::real_1d_array& nutrient_values);
    Food(Food&&) = default;

    int get_id() const;
    std::string get_description() const;
    const alglib::real_1d_array& as_matrix() const;
    size_t nutrient_count() const;

    /**
     * Return how non-orthogonal this and the other vector are to each other
     *
     * Ranges from 0.0 (orthogonal) to 1.0 (linear) = cos theta, where theta is angle between this and other food
     */
    double get_similarity(const Food& other) const;

private:
    Food(const Food& food) = delete;

private:
    int id;
    std::string description;
    alglib::real_1d_array nutrient_values;  // nutrient_values[i] = value associated with nutrient{id=i}
    alglib::real_1d_array normalised_nutrient_values;
};

typedef std::vector<Food>::const_iterator FoodIt;

