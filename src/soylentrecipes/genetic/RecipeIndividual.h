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
#include <soylentrecipes/genetic/FoodGenotype.h>
#include <iostream>

/**
 * An individual who is a Recipe
 *
 * Invariant: genotypes are sorted
 */
class RecipeIndividual : public Beagle::Individual
{
public:
    typedef Beagle::AllocatorT<RecipeIndividual, Beagle::Individual::Alloc> Alloc;
    typedef Beagle::PointerT<RecipeIndividual, Beagle::Individual::Handle> Handle;
    typedef Beagle::ContainerT<RecipeIndividual, Beagle::Individual::Bag> Bag;

public:
    RecipeIndividual();

    /**
     * Add a random food to an individual (that isn't already present in that individual)
     */
    void addFood(Beagle::Context& context);

    /**
     * Add given food
     */
    void addFood(FoodGenotype::Handle genotype);

    /**
     * Remove a random food
     */
    void removeFood(Beagle::Context& context);

    /**
     * Swap geno1 of this individual with geno2 of indiv2
     */
    void swapFood(Object::Handle geno1, Individual& indiv2, Object::Handle geno2);

    /**
     * Compare 2 food genotypes
     *
     * geno1 < geno2
     */
    static bool compare(Object::Handle h1, Object::Handle h2);
};

