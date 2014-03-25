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
#include <soylentrecipes/genetic/RecipeIndividual.h>
#include "RecipeInitializationOp.h"

using namespace std;
using namespace Beagle;

RecipeInitializationOp::RecipeInitializationOp(Foods& foods, Beagle::string name)
:   InitializationOp("ec.repro.prob", name), _foods(foods), _recipe_size(4)
{
}

void RecipeInitializationOp::initIndividual(Beagle::Individual& individual, Beagle::Context& context) {
    while (individual.size() < _recipe_size) {
        reinterpret_cast<RecipeIndividual&>(individual).addFood(_foods, context);
    }
}

