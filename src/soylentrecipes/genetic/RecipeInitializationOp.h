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

#include <algorithm>
#include <vector>
#include <iostream>
#include <beagle/GA.hpp>
#include <soylentrecipes/genetic/FoodGenotype.h>

/**
 * Initializes individuals consisting of food
 *
 * Individuals need to be of FoodGenotype
 */
class RecipeInitializationOp : public Beagle::InitializationOp
{
public:
    typedef Beagle::AllocatorT<RecipeInitializationOp, Beagle::InitializationOp::Alloc> Alloc;
    typedef Beagle::PointerT<RecipeInitializationOp, Beagle::InitializationOp::Handle> Handle;
    typedef Beagle::ContainerT<RecipeInitializationOp, Beagle::InitializationOp::Bag> Bag;

public:
    RecipeInitializationOp(Foods& foods, Beagle::string name = "InitRecipeOp")
    :   InitializationOp("ec.repro.prob", name), _foods(foods), _recipe_size(4)
    {
    }

    void initIndividual(Beagle::Individual& individual, Beagle::Context& context)
    {
        using namespace std;
        using namespace Beagle;

        individual.resize(_recipe_size);
        vector<const Food*> used_foods;

        for (int i=0;; i++) {
            const Food* next;
            do {
                next = _foods.get_random(context.getSystem().getRandomizer());
            } while (find(used_foods.begin(), used_foods.end(), next) != used_foods.end());

            used_foods.push_back(next);

            FoodGenotype::Handle& genotype = castHandleT<FoodGenotype>(individual.at(i));
            genotype->setFood(next);

            if (individual.at(i) == individual.back()) {
                break;
            }
        }
    }

private:
    Foods& _foods;
    int _recipe_size; // TODO register settable 
};

