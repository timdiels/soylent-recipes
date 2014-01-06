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

#include <string>

class Nutrient
{
public:
    Nutrient(int id, std::string description, std::string unit, double target, double max_);

    std::string get_description() const;
    std::string get_unit() const;
    double get_target() const;
    double get_max() const;

private:
    int id;
    std::string description;
    std::string unit; // e.g. "mg", "ml", "kCal"

    double target; // desired daily amount
    double max_; // maximum daily amount
};
