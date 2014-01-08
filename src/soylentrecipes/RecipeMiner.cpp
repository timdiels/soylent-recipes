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
#include <valgrind/callgrind.h>
#include "RecipeMiner.h"
#include "RecipeProblem.h"

using namespace std;

RecipeMiner::RecipeMiner(const NutrientProfile& profile, Foods& foods, Recipes& recipes)
:   profile(profile), foods(foods), recipes(recipes)
{
}

void RecipeMiner::mine() {
    // TODO resume where we last left off
    vector<Food> foods;
    foods.reserve(max_combo_size);

    CALLGRIND_START_INSTRUMENTATION;
    mine(foods);
    CALLGRIND_STOP_INSTRUMENTATION;
    CALLGRIND_DUMP_STATS;
}

void RecipeMiner::mine(const vector<Food>& foods) {
    if (foods.size() < max_combo_size) {
        auto next_foods = foods;
        int id;
        if (foods.empty()) {
            id = 0;
        }
        else {
            id = foods.back().get_id();
        }

        for (; id < this->foods.count(); id++) {
            id++;
            Food next_food = this->foods.get(id);
            if (!are_orthogonal(foods, next_food)) {
                continue;
            }

            next_foods.push_back(next_food);
            mine(next_foods);
            next_foods.pop_back();
        }
    }

    if (!foods.empty()) {
        examine_recipe(foods);
    }
}

bool RecipeMiner::are_orthogonal(const vector<Food>& foods, const Food& food) {
    for (auto& food : foods) {
        if (food.get_similarity(food) > max_similarity) {
            return false;
        }
    }
    return true;
}

void RecipeMiner::examine_recipe(const vector<Food>& foods) {
    // solve recipe
    RecipeProblem problem(profile, foods);
    auto result = problem.solve();

    // calculate completeness number (ranges from 0.0 to 1.0)
    // note: nutrients aren't weighted in the completeness number
    double completeness = 0.0;
    for (int i=0; i < result.length(); ++i) {
        completeness += min(1.0, result[i] / profile.get_targets()[i]);
    }
    completeness /= result.length();

    // add recipe
    if (recipes.add_recipe(foods, completeness)) {
        for (int i=0; i < result.length(); ++i) {
            auto& food = foods.at(i);
            cout << food.get_description() << ": " << result[i] << endl;
        }
        cout << completeness << endl << endl;
    }
}

