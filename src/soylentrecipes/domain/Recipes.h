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

#include <soylentrecipes/data_access/FoodDatabase.h>

class Recipes
{
public:
    Recipes(FoodDatabase&, std::string recipe_type);

    /**
     * Returns true if it's useful to add a recipe with these properties
     */
    bool is_useful(double completeness);

    template <class InputIterator>
    void add_recipe(InputIterator ids_begin, InputIterator ids_end, double completeness);

private:
    double best_completeness; // best completeness found in recipes
    FoodDatabase& db;
    std::string recipe_type;
};


///////////////////////////
// hpp
///////////////////////////

template <class InputIterator>
void Recipes::add_recipe(InputIterator ids_begin, InputIterator ids_end, double completeness) {
    best_completeness = std::max(completeness, best_completeness);
    db.add_recipe(recipe_type, ids_begin, ids_end, completeness);
}
