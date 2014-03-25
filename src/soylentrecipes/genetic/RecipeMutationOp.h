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
#include <soylentrecipes/genetic/Foods.h>

/**
 * Cross over of 2 individuals by swapping 2 of their genotypes
 */
class RecipeMutationOp : public Beagle::MutationOp 
{
public:
    typedef Beagle::AllocatorT<RecipeMutationOp, Beagle::MutationOp::Alloc> Alloc;
    typedef Beagle::PointerT<RecipeMutationOp, Beagle::MutationOp::Handle> Handle;
    typedef Beagle::ContainerT<RecipeMutationOp, Beagle::MutationOp::Bag> Bag;

public:
    RecipeMutationOp(Foods& foods);

    /**
     * @returns bool True if mutated succesfully, false otherwise
     */
    bool mutate(Beagle::Individual& ioIndividual, Beagle::Context& ioContext);

private:
    Foods& _foods;
};
