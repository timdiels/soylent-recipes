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

#include <libalglib/stdafx.h>
#include <libalglib/optimization.h>
#include <soylentrecipes/domain/NutrientProfile.h>
#include <soylentrecipes/domain/Food.h>
#include <vector>

/**
 * The problem of balancing the amounts of ingredients in a soylent recipe
 */
class RecipeProblem
{
public:
    RecipeProblem(const NutrientProfile& profile, const std::vector<Food>& foods);

    alglib::real_1d_array solve();

    /**
     * Function for optimizer, func_value = l2_norm(a*x-y)^2
     */
    static void f(const alglib::real_1d_array& x, double& func_value, alglib::real_1d_array& gradient, void* data);

private:
    void _f(const alglib::real_1d_array& x, double& func_value, alglib::real_1d_array& gradient);

private:
    alglib::real_2d_array a;
    alglib::real_1d_array y;

    alglib::minbleicstate solver;
};

