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

#include <beagle/GA.hpp>
#include <soylentrecipes/genetic/FoodGenotype.h>
#include <soylentrecipes/domain/Food.h>
#include <soylentrecipes/genetic/Foods.h>
#include <soylentrecipes/genetic/FoodGenotype.h>
#include <assert.h>
#include "RecipeIndividual.h"

using namespace std;
using namespace Beagle;

RecipeIndividual::RecipeIndividual()
:   Individual(new FoodGenotype::Alloc, new FitnessSimple::Alloc)
{
}

void RecipeIndividual::addFood(Foods& foods, Context& context) {
    const Food* next;
    bool alreadyHasFood;
    do {
        next = foods.get_random(context.getSystem().getRandomizer());

        alreadyHasFood = false;
        for (int i=0; i < size(); i++) {
            if (castHandleT<FoodGenotype>(at(i))->getFood() == next) {
                alreadyHasFood = true;
                break;
            }
        }
    } while (alreadyHasFood);

    resize(size()+1);
    FoodGenotype::Handle& genotype = castHandleT<FoodGenotype>(at(size()-1));
    genotype->setFood(next);
}

void RecipeIndividual::removeFood(Context& context) {
    assert(size() > 1);
    unsigned long index = context.getSystem().getRandomizer().rollInteger(0, size()-1);

    erase(begin()+index);
}
