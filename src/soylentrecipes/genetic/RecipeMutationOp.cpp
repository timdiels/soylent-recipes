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

#include "RecipeMutationOp.h"
#include <iostream>
#include <soylentrecipes/genetic/RecipeIndividual.h>

using namespace std;
using namespace Beagle;

RecipeMutationOp::RecipeMutationOp()
:   MutationOp("ec.mut.prob", "RecipeMutationOp")
{
}

bool RecipeMutationOp::mutate(Individual& individual, Context& context) {
    cout << "mut" << endl;

    RecipeIndividual& indiv = reinterpret_cast<RecipeIndividual&>(individual);

    // Note: adding food is slightly favored
    if (indiv.size() == 1 || context.getSystem().getRandomizer().rollUniform() <= 0.5) {
        // add a food
        cout << "add" << endl;
        indiv.addFood(context);
    }
    else {
        // remove a food
        cout << "remove" << endl;
        indiv.removeFood(context);
    }

    return true;
}
