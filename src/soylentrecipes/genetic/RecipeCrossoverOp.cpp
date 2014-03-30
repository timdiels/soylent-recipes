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

#include "RecipeCrossoverOp.h"
#include <assert.h>
#include <algorithm>
#include <soylentrecipes/genetic/FoodGenotype.h>
#include <soylentrecipes/genetic/RecipeIndividual.h>

using namespace std;
using namespace Beagle;

RecipeCrossoverOp::RecipeCrossoverOp()
:   CrossoverOp("ec.cx.prob", "RecipeCrossoverOp")
{
}

bool RecipeCrossoverOp::mate(Individual& indiv1, Context& context1, Individual& indiv2, Context& context2) {
    assert(indiv1.size() >= 1);
    assert(indiv2.size() >= 1);

    assert(is_sorted(indiv1.begin(), indiv1.end(), RecipeIndividual::compare));
    assert(is_sorted(indiv2.begin(), indiv2.end(), RecipeIndividual::compare));

    vector<Object::Handle> diff1; // present in first, not in second
    vector<Object::Handle> diff2; // present in second, not in first
    
    set_difference(indiv1.begin(), indiv1.end(), indiv2.begin(), indiv2.end(), back_inserter(diff1), RecipeIndividual::compare);
    set_difference(indiv2.begin(), indiv2.end(), indiv1.begin(), indiv1.end(), back_inserter(diff2), RecipeIndividual::compare);

    if (diff1.size() == 0 || diff2.size() == 0)
        return false;

    unsigned long index1 = context1.getSystem().getRandomizer().rollInteger(0, diff1.size()-1);
    unsigned long index2 = context2.getSystem().getRandomizer().rollInteger(0, diff2.size()-1);

    auto& geno1 = diff1.at(index1);
    auto& geno2 = diff2.at(index2);

    reinterpret_cast<RecipeIndividual&>(indiv1).swapFood(geno1, indiv2, geno2);

    return true;
}
