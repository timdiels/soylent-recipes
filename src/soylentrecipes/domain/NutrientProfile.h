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

#include <vector>
#include <libalglib/linalg.h>
#include "Nutrient.h"

/**
 * A list of constrained nutrients
 */
class NutrientProfile
{
public:
    NutrientProfile(const std::vector<Nutrient>& nutrients, const alglib::real_1d_array& targets, const alglib::real_1d_array& maxima);

    const std::vector<Nutrient>& get_nutrients() const;
    const alglib::real_1d_array& get_targets() const;
    const alglib::real_1d_array& get_maxima() const;

private:
    const std::vector<Nutrient> nutrients;
    alglib::real_1d_array targets; // targets[i] = desired daily amount of nutrient i
    alglib::real_1d_array maxima; // maxima[i] = maximum daily amount of nutrient i
};

