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

#include <soylentrecipes/domain/Food.h>
#include <beagle/GA.hpp>

class FoodGenotype : public Beagle::Genotype
{
public:
    typedef Beagle::AllocatorT<FoodGenotype, Beagle::Genotype::Alloc> Alloc;
    typedef Beagle::PointerT<FoodGenotype, Beagle::Genotype::Handle> Handle;
    typedef Beagle::ContainerT<FoodGenotype, Beagle::Genotype::Bag> Bag;

public:
    bool isEqual(const Object& obj) const;
    const Food* getFood() const;
    void setFood(const Food* food);
    void write(PACC::XML::Streamer& ioStreamer, bool inIndent) const;
    void readWithContext(PACC::XML::ConstIterator inIter, Beagle::Context& context);

private:
    const Food* _food;
};

