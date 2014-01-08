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

// cpp
#include <vector>
#include "RecipeProblem.h"
#include <soylentrecipes/domain/Recipes.h>
#include <soylentrecipes/domain/Foods.h>
#include <soylentrecipes/domain/NutrientProfile.h>

using namespace std;

/**
 * Mines a food database for good recipes
 */
class RecipeMiner
{
public:
    RecipeMiner(const NutrientProfile& profile, Foods& foods, Recipes&);

    /**
     * Depth-first search on all seemingly-useful combinations of foods
     *
     * Note: depth-first because of memory use
     * Note: there is a max on the size of a combination
     * Note: When the foods of a combination aren't sufficiently inter-orthogonal, the combination is considered useless
     */
    void mine() {
        // TODO resume where we last left off
        vector<Food> foods;
        mine(foods);
    }

private:
    /**
     * Examines combinations of 'foods' with other foods
     *
     * foods: ordered by id
     */
    void mine(const vector<Food>& foods) {
        if (foods.size() < max_combo_size) {
            auto next_foods = foods;
            //try {
                for (int id = foods.back().get_id();; id++) {
                    next_foods.push_back(this->foods.get(id, profile));
                    mine(next_foods);
                    next_foods.pop_back();
                }
            /*}
            catch (const FoodNotFoundException&) {
            } TODO*/
        }

        if (!foods.empty()) {
            examine_recipe(foods);
        }
    }

    void examine_recipe(const vector<Food>& foods) {
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
        recipes.add_recipe(foods, completeness);
    }

private:
    NutrientProfile& profile;
    Foods& foods;
    Recipes& recipes;

    const int max_combo_size = 12;
    const double min_orthogonality = 0.7;
};

