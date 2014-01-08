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

#include <vector>
#include <stdexcept>
#include <soylentrecipes/data_access/Database.h>
#include <soylentrecipes/data_access/Query.h>
#include <soylentrecipes/domain/Food.h>
#include "Recipes.h"

using namespace std;

Recipes::Recipes(Database& db) 
:   db(db), insert_recipe_stmt(db, "INSERT INTO recipe (foods, food_count, completeness) VALUES (?, ?, ?);")
{
    Query stmt(db, "SELECT max(completeness) FROM recipe;");
    if (!stmt.step()) {
        throw runtime_error("Unexpected query result");
    }
    best_completeness = stmt.get_double(0, 0.0);
}

bool Recipes::is_useful(double completeness) {
    double error_margin = 0.95;
    return completeness >= best_completeness * error_margin;
}
void Recipes::add_recipe(const vector<FoodIt>& foods, double completeness) {
    best_completeness = max(completeness, best_completeness);
    // TODO put in db
}

