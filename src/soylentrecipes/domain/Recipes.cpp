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

#include "Recipes.h"

using namespace std;

Recipes::Recipes(FoodDatabase& db, std::string recipe_type)
:   best_completeness(0.0), db(db), recipe_type(recipe_type)
{
}

bool Recipes::is_useful(double completeness) {
    double error_margin = 0.95;
    return completeness >= best_completeness * error_margin;
}

