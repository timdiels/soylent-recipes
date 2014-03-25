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
#include <vector>

/**
 * Cross over of 2 individuals by swapping 2 of their genotypes
 */
class RecipeCrossoverOp : public Beagle::CrossoverOp 
{
public:
    typedef Beagle::AllocatorT<RecipeCrossoverOp, Beagle::CrossoverOp::Alloc> Alloc;
    typedef Beagle::PointerT<RecipeCrossoverOp, Beagle::CrossoverOp::Handle> Handle;
    typedef Beagle::ContainerT<RecipeCrossoverOp, Beagle::CrossoverOp::Bag> Bag;

    /**
     * @returns bool True if mated succesfully, false otherwise
     */
    bool mate(Beagle::Individual& indiv1, Beagle::Context& context1, Beagle::Individual& indiv2, Beagle::Context& context2);

public:
    RecipeCrossoverOp();

private:
};
