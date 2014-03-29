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
#include <algorithm>
#include <soylentrecipes/genetic/FoodGenotype.h>

using namespace std;
using namespace Beagle;

RecipeCrossoverOp::RecipeCrossoverOp()
:   CrossoverOp("ec.cx.prob", "RecipeCrossoverOp")
{
}

bool RecipeCrossoverOp::mate(Individual& indiv1, Context& context1, Individual& indiv2, Context& context2) {
    cout << "cross" << endl;
    assert(indiv1.size() >= 1);
    assert(indiv2.size() >= 1);

    auto compare = [](Object::Handle h1, Object::Handle h2) {
        return castHandleT<FoodGenotype>(h1)->getFood()->get_id() < castHandleT<FoodGenotype>(h2)->getFood()->get_id();
    };

    sort(indiv1.begin(), indiv1.end(), compare);
    sort(indiv2.begin(), indiv2.end(), compare);

    vector<Object::Handle> diff1; // present in first, not in second
    vector<Object::Handle> diff2; // present in second, not in first
    
    set_difference(indiv1.begin(), indiv1.end(), indiv2.begin(), indiv2.end(), back_inserter(diff1), compare);
    set_difference(indiv2.begin(), indiv2.end(), indiv1.begin(), indiv1.end(), back_inserter(diff2), compare);

    if (diff1.size() == 0 || diff2.size() == 0)
        return false;

    unsigned long index1 = context1.getSystem().getRandomizer().rollInteger(0, diff1.size()-1);
    unsigned long index2 = context2.getSystem().getRandomizer().rollInteger(0, diff2.size()-1);

    auto it1 = find(indiv1.begin(), indiv1.end(), diff1.at(index1));
    auto it2 = find(indiv2.begin(), indiv2.end(), diff2.at(index2));

    swap(*it1, *it2);

    return true;
}
