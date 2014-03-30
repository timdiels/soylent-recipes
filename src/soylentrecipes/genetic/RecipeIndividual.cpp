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

#include "RecipeIndividual.h"
#include <beagle/GA.hpp>
#include <soylentrecipes/domain/Food.h>
#include <soylentrecipes/genetic/Foods.h>
#include <soylentrecipes/genetic/RecipeContext.h>
#include <soylentrecipes/genetic/RecipeFitness.h>
#include <assert.h>

using namespace std;
using namespace Beagle;

RecipeIndividual::RecipeIndividual()
:   Individual(new FoodGenotype::Alloc, new RecipeFitness::Alloc)
{
}

bool RecipeIndividual::compare(Object::Handle h1, Object::Handle h2) {
    return castHandleT<FoodGenotype>(h1)->getFood()->get_id() < castHandleT<FoodGenotype>(h2)->getFood()->get_id();
};

void RecipeIndividual::addFood(Context& context) {
    auto& foods = reinterpret_cast<RecipeContext&>(context).getFoods();
    Object::Handle geno;
    std::vector<Object::Handle, std::allocator<Object::Handle> >::iterator it;
    do {
        geno = new FoodGenotype(foods.get_random(context.getSystem().getRandomizer()));
        it = lower_bound(begin(), end(), geno, compare);

    } while (it != end() && **it == *geno);

    insert(it, geno);
}

void RecipeIndividual::removeFood(Context& context) {
    assert(size() > 1);
    unsigned long index = context.getSystem().getRandomizer().rollInteger(0, size()-1);

    erase(begin()+index);
}

void RecipeIndividual::swapFood(Object::Handle geno1, Individual& indiv2, Object::Handle geno2) {
    iterator it1 = lower_bound(begin(), end(), geno1, compare);
    iterator it2 = lower_bound(indiv2.begin(), indiv2.end(), geno2, compare);
    assert(**it1 == *geno1);
    assert(**it2 == *geno2);

    erase(it1);
    indiv2.erase(it2);

    iterator it = lower_bound(begin(), end(), geno2, compare);
    insert(it, geno2);

    it = lower_bound(indiv2.begin(), indiv2.end(), geno1, compare);
    indiv2.insert(it, geno1);
}

