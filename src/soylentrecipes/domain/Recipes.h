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
#include <soylentrecipes/data_access/Database.h>
#include <soylentrecipes/data_access/Query.h>
#include <soylentrecipes/domain/Food.h>

class Recipes
{
public:
    Recipes(Database& db);

    /**
     * Add recipe
     *
     * Note: not all recipes are added, only those deemed useful given current
     * knowledge. E.g. too incomplete ones are discarded.
     */
    void add_recipe(const std::vector<Food>& foods, double completeness) {
        //double allowed_error = 1e-2;
        /*if (completeness >= get_best_completeness(foods.size()) - allowed_error) {
            for (int i=0; i < result.length(); ++i) {
                auto& food = foods.at(i);
                cout << food.get_description() << ": " << result[i] << endl;
            }
            cout << completeness << endl;
        }TODO*/
    }

private:
    Database& db;
    Query insert_recipe_stmt;
};

