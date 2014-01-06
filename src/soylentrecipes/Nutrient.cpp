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

#include "Nutrient.h"

using namespace std;

Nutrient::Nutrient(int id, string description, string unit, double target, double max_)
:   id(id), description(description), unit(unit), target(target), max_(max_)
{
}

string Nutrient::get_description() const {
    return description;
}

string Nutrient::get_unit() const {
    return unit;
}

double Nutrient::get_target() const {
    return target;
}

double Nutrient::get_max() const {
    return max_;
}

