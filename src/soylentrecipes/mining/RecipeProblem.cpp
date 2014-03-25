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

using namespace std;
using namespace alglib;

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
        gradient[i] = 2.0 * vdotproduct(&v[0], 1, &a[0][i], a.getstride(), v.length());
        // TODO check gradient is correct
    }
}

