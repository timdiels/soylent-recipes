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

#include "RecipeProblem.h"
#include <iostream>
#include <sstream>
#include <cmath>
#include <algorithm>

using namespace std;
using namespace alglib;

RecipeProblem::RecipeProblem(const NutrientProfile& profile, const vector<FoodIt>& foods) {
    // generate A
    a.setlength(profile.get_nutrients().size(), foods.size());
    for (int j=0; j < a.cols(); ++j) {
        // This acted as if the source stride was 2, for some reason: vmove(&a[0][j], a.getstride(), &foods.at(j)->as_matrix()[0], 1, a.rows());
        for (int i=0; i < a.rows(); ++i) {
            a[i][j] = foods.at(j)->as_matrix()[i];
        }
    }

    // generate Y
    y = profile.get_targets(); // TODO unnecessary copy, use it directly

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

real_1d_array RecipeProblem::solve() {
    //const int max_iterations = 10000;
    //minbleicsetcond(solver, 0, 0, 0, max_iterations);

    minbleicoptimize(solver, RecipeProblem::f, nullptr, this);

    minbleicreport report;
    real_1d_array x;
    x.setlength(a.cols());
    minbleicresults(solver, x, report);

    if (report.terminationtype < 0 || report.terminationtype == 5) {
        // http://www.alglib.net/translator/man/manual.cpp.html#sub_minbleicresults
        // Something unexpected happened
        ostringstream str;
        str << "Failed to solve problem: term type " << report.terminationtype;
        throw runtime_error(str.str());
    }

    return x;
}

void RecipeProblem::f(const real_1d_array& x, double& func_value, real_1d_array& gradient, void* data) {
    reinterpret_cast<RecipeProblem*>(data)->_f(x, func_value, gradient);
}

void RecipeProblem::_f(const real_1d_array& x, double& func_value, real_1d_array& gradient) {
    // func_value
    real_1d_array v;
    v.setlength(a.rows());
    rmatrixmv(a.rows(), a.cols(), a, 0, 0, 0, x, 0, v, 0); // v = a*x
    vsub(&v[0], &y[0], y.length()); // v = a*x - y
    func_value = vdotproduct(&v[0], &v[0], v.length());

    // gradient
    for (int i = 0; i < x.length(); ++i) {
        gradient[i] = 0.0;
        for (int j=0; j < a.rows(); ++j) {
            gradient[i] += 2.0 * v[j] * a[j][i];
        }
    }
}

