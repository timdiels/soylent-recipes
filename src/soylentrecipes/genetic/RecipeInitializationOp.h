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

#include <beagle/GA.hpp>

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
    RecipeInitializationOp(Beagle::string name = "InitRecipeOp");

    void initIndividual(Beagle::Individual& individual, Beagle::Context& context);

private:
    int _recipe_size; // TODO register settable 
};

