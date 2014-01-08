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
#include <soylentrecipes/domain/Recipes.h>
#include <soylentrecipes/domain/Foods.h>
#include <soylentrecipes/domain/NutrientProfile.h>

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
    void mine();

private:
    /**
     * Examines combinations of 'foods' with other foods
     *
     * foods: ordered by id
     */
    void mine(const std::vector<Food>& foods);
    bool are_orthogonal(const std::vector<Food>& foods, const Food& food);
    void examine_recipe(const std::vector<Food>& foods);

private:
    const NutrientProfile& profile;
    Foods& foods;
    Recipes& recipes;

    const int max_combo_size = 12;
    const double max_similarity = 0.3;  // = cos theta, where theta is the minimum angle between 2 foods in a valid combination; 0.3 -> 72 degrees
};
