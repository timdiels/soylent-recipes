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
#include <cmath>
#include <algorithm>

using namespace std;
using namespace alglib;

RecipeProblem::RecipeProblem(const NutrientProfile& profile, const vector<Food>& foods) {
    // generate A
    a.setlength(profile.get_nutrients().size(), foods.size());
    for (int i=0; i < a.rows(); ++i) {
        for (int j=0; j < a.cols(); ++j) {
            a[i][j] = foods.at(j).get_nutrient_values().at(i);
        }
    }
    cout << "a " << a.tostring(2) << endl;

    // generate Y
    y.setlength(a.rows());
    for (int i=0; i < y.length(); ++i) {
        y[i] = profile.get_nutrients().at(i).get_target();
    }
    cout << "y " << y.tostring(2) << endl;

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
    for (auto& nutrient : profile.get_nutrients()) {
        if (nutrient.get_max() != INFINITY) {
            constraint_count++;
        }
    }

    real_2d_array constraints;
    constraints.setlength(constraint_count, a.cols()+1);
    for (int k=0, i=0; i < a.rows(); ++i) {
        double max_ = profile.get_nutrients()[i].get_max();
        if (max_ != INFINITY) {
            for (int j=0; j < a.cols(); ++j) {
                constraints[k][j] = a[i][j];
            }
            constraints[k][a.cols()] = profile.get_nutrients().at(i).get_max();
            k++;
        }
    }
    
    vector<ae_int_t> negatives(constraints.rows(), -1);
    integer_1d_array constraint_types;
    constraint_types.setcontent(constraints.rows(), negatives.data());

    minbleicsetlc(solver, constraints, constraint_types);
    cout << "c " << constraints.tostring(2) << endl
        << constraint_types.tostring() << endl;
    }
}

real_1d_array RecipeProblem::solve() {
    const int max_iterations = 1000;
    minbleicsetcond(solver, 0, 0, 0, max_iterations);

    minbleicoptimize(solver, RecipeProblem::f, nullptr, this);

    minbleicreport report;
    real_1d_array x;
    x.setlength(a.cols());
    minbleicresults(solver, x, report);

    if (report.terminationtype < 0 || report.terminationtype == 5) {
        // http://www.alglib.net/translator/man/manual.cpp.html#sub_minbleicresults
        // Something unexpected happened
        throw runtime_error("Failed to solve problem");
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

    //cout << "x " << x.tostring(2) << endl;
    //cout << func_value << endl;

    // gradient
    for (int i = 0; i < x.length(); ++i) {
        gradient[i] = 0.0;
        for (int j=0; j < a.rows(); ++j) {
            gradient[i] += 2.0 * v[j] * a[j][i]; // TODO store a double_a = 2*a
        }
    }
}

