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

class RecipeFitness : public Beagle::FitnessSimple
{
public:
    typedef Beagle::AllocatorT<RecipeFitness, Beagle::FitnessSimple::Alloc> Alloc;
    typedef Beagle::PointerT<RecipeFitness, Beagle::FitnessSimple::Handle> Handle;
    typedef Beagle::ContainerT<RecipeFitness, Beagle::FitnessSimple::Bag> Bag;

public:
    RecipeFitness() : FitnessSimple()
    {
    }

    RecipeFitness(double completeness, double simplicity) 
    :   FitnessSimple(
            1.0 * completeness + 
            0.1 * simplicity),
        _completeness(completeness)
    {
    }

    void write(PACC::XML::Streamer& ioStreamer, bool inIndent) const {
        ioStreamer.openTag("Fitness", false);
        ioStreamer.insertAttribute("type", "simple");
        ioStreamer.insertAttribute("completeness", _completeness);
        if (isValid()) {
            ioStreamer.insertStringContent(Beagle::dbl2str(mFitness).c_str());
        }
        else {
            ioStreamer.insertAttribute("valid", "no");
        }
        ioStreamer.closeTag();
    }

private:
    double _completeness;
};

