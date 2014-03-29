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

#include "FoodGenotype.h"
#include <soylentrecipes/genetic/RecipeContext.h>
#include <iostream>
#include <sstream>
#include <assert.h>

using namespace std;
using namespace Beagle;

bool FoodGenotype::isEqual(const Object& obj) const {
    auto& other = castObjectT<const FoodGenotype&>(obj);
    return *other._food == *_food;
}

const Food* FoodGenotype::getFood() const {
    assert(_food);
    return _food;
}

void FoodGenotype::setFood(const Food* food) {
    _food = food;
}

void FoodGenotype::write(PACC::XML::Streamer& ioStreamer, bool inIndent) const {
    ioStreamer.openTag("Genotype", inIndent);
    ioStreamer.insertAttribute("id", getFood()->get_id());
    ioStreamer.insertStringContent(getFood()->get_description());
    ioStreamer.closeTag();
}

void FoodGenotype::readWithContext(PACC::XML::ConstIterator inIter, Context& context)
{
    if((inIter->getType() != PACC::XML::eData) || (inIter->getValue() != "Genotype"))
        throw Beagle_IOExceptionNodeM(*inIter, "tag <Genotype> expected!");

    auto& foods = reinterpret_cast<RecipeContext&>(context).getFoods();
    istringstream conv(inIter->getAttribute("id"));
    int id;
    conv >> id;
    _food = foods.get(id);
}

