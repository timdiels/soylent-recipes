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
#include <iostream>

using namespace std;
using namespace Beagle;

RecipeCrossoverOp::RecipeCrossoverOp()
:   CrossoverOp("ec.cx.prob", "RecipeCrossoverOp")
{
}

bool RecipeCrossoverOp::mate(Individual& indiv1, Context& context1, Individual& indiv2, Context& context2) {
    // TODO our mutation op should prevent removing from size 1 individuals
    cout << "yay" << endl;
    assert(indiv1.size() >= 1);
    assert(indiv2.size() >= 1);
    unsigned long index1 = context1.getSystem().getRandomizer().rollInteger(0, indiv1.size()-1);
    unsigned long index2 = context2.getSystem().getRandomizer().rollInteger(0, indiv2.size()-1);
    swap(indiv1.at(index1), indiv2.at(index2));
    return true;
}
