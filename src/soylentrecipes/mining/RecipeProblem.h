/*
 * Copyright (C) 2014 by Tim Diels
 *
 * This file is part of soylent-recipes.
 * * soylent-recipes is free software: you can redistribute it and/or modify
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

// TODO add test of completeness score

#pragma once

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
    template <class ForwardIterator>
    RecipeProblem(const NutrientProfile& profile, ForwardIterator foods_begin, ForwardIterator foods_end);

    void solve();

    /**
     * The amounts one should take of each food
     */
    alglib::real_1d_array get_result();

    /**
     * Completeness number ranges from 0.0 to 1.0,
     *
     * Indicates how completely the profile was reached
     * without exceeding bounds
     */
    double get_completeness();

    /**
     * Function for optimizer, func_value = l2_norm(a*x-y)^2
     */
    static void f(const alglib::real_1d_array& x, double& func_value, alglib::real_1d_array& gradient, void* data);

    static void print_stats(double elapsed_time, long food_count);

private:
    void _f(const alglib::real_1d_array& x, double& func_value, alglib::real_1d_array& gradient);

private:
    alglib::real_2d_array a;
    const alglib::real_1d_array& y;
    alglib::real_1d_array x;
    alglib::minbleicstate solver;
    const NutrientProfile& _profile;

    // stats
    static long total_calculated;
    static long problem_size_sum;  // sum of len(foods) of recipe problems that were solved
};


//////////////////////////////
// hpp

#include <cmath>
#include <algorithm>

template <class ForwardIterator>
RecipeProblem::RecipeProblem(const NutrientProfile& profile, ForwardIterator foods_begin, ForwardIterator foods_end) 
:   y(profile.get_targets()), _profile(profile)
{
    using namespace std;
    using namespace alglib;

    // generate A
    a.setlength(profile.get_targets().length(), distance(foods_begin, foods_end));
    auto it = foods_begin;
    for (int j=0; j < a.cols(); ++j) {
        // This acted as if the source stride was 2, for some reason: vmove(&a[0][j], a.getstride(), &foods.at(j)->as_matrix()[0], 1, a.rows());
        for (int i=0; i < a.rows(); ++i) {
            a[i][j] = (*it)->as_matrix()[i];
        }
        it++;
    }


    // create solver
    {
    vector<double> zeros(a.cols(), 0.0);
    real_1d_array x;
    x.setcontent(zeros.size(), zeros.data());
    minbleiccreate(x, solver);
    }

    // set bounds on x
    {
    vector<double> infs(a.cols(), INFINITY);
    vector<double> zeros(a.cols(), 0.0);

    real_1d_array lower_bounds;
    lower_bounds.setcontent(zeros.size(), zeros.data());

    real_1d_array upper_bounds;
    upper_bounds.setcontent(infs.size(), infs.data());

    minbleicsetbc(solver, lower_bounds, upper_bounds);
    }

    // set inequality constraints
    {
    int constraint_count = 0;
    for (int i=0; i < profile.get_maxima().length(); i++) {
        if (profile.get_maxima()[i] != INFINITY) {
            constraint_count++;
        }
    }

    real_2d_array constraints;
    constraints.setlength(constraint_count, a.cols()+1);
    for (int k=0, i=0; i < a.rows(); ++i) {
        double max_ = profile.get_maxima()[i];
        if (max_ != INFINITY) {
            rmatrixcopy(1, a.cols(), a, i, 0, constraints, k, 0);
            constraints[k][a.cols()] = max_;
            k++;
        }
    }
    
    vector<ae_int_t> negatives(constraints.rows(), -1);
    integer_1d_array constraint_types;
    constraint_types.setcontent(constraints.rows(), negatives.data());

    minbleicsetlc(solver, constraints, constraint_types);
    }
}
