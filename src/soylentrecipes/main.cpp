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

#include <libalglib/stdafx.h>
#include <libalglib/optimization.h>
#include <iostream>
#include <vector>
#include <assert.h>
#include <cmath>

//using namespace SOYLENT;
using namespace std;
using namespace alglib;

/**
 * The problem of balancing the amounts of ingredients in a soylent recipe
 */
class RecipeProblem
{
public:
    RecipeProblem() {
        a = real_2d_array("[[1,0,0],[0,1,0],[1,0,-1]]");
        y = real_1d_array("[0,2,0]");
        assert(a.cols() == y.length());
    }

    /**
     * Function for optimizer, func_value = l2_norm(a*x-y)^2
     */
    static void f(const real_1d_array& x, double& func_value, real_1d_array& gradient, void* data) {
        reinterpret_cast<RecipeProblem*>(data)->_f(x, func_value, gradient);
    }

private:
    void _f(const real_1d_array& x, double& func_value, real_1d_array& gradient) {
        // func_value
        real_1d_array v;
        v.setlength(a.rows());
        rmatrixmv(a.rows(), a.cols(), a, 0, 0, 0, x, 0, v, 0); // v = a*x
        vsub(&v[0], &y[0], y.length()); // v = a*x - y
        func_value = vdotproduct(&v[0], &v[0], v.length());

        cout << "x " << x.tostring(2) << endl;
        cout << func_value << endl;

        // gradient
        for (int i = 0; i < x.length(); ++i) {
            gradient[i] = 0.0;
            for (int j=0; j < a.rows(); ++j) {
                gradient[i] += 2.0 * v[j] * a[j][i]; // TODO store a double_a = 2*a
            }
        }
    }

private:
    real_2d_array a;
    real_1d_array y;
};

int main(int argc, char** argv) {
    try {
        RecipeProblem problem;

        int n = 3; // TODO hardcoded
        vector<double> infs(n, INFINITY);
        vector<double> zeros(n, 0.0);

        real_1d_array x("[0,0,0]");

        real_1d_array lower_bounds;
        lower_bounds.setcontent(n, zeros.data());

        real_1d_array upper_bounds;
        upper_bounds.setcontent(n, infs.data());

        minbleicstate state;
        minbleicreport report;

        minbleiccreate(x, state);

        real_2d_array constraints("[[1, 2, 3, 2]]");
        vector<double> negatives(constraints.rows(), -1);
        real_1d_array constraint_types;
        constraint_types.setcontent(constraints.rows(), negatives.data()); // all constraints are: A[i] * X <= num

        minbleicsetbc(state, lower_bounds, upper_bounds);
        minbleicsetcond(state, 0, 0, 0, 1000); // 1000 its max
        alglib::minbleicoptimize(state, problem.f, nullptr, &problem);
        minbleicresults(state, x, report);

        cout << report.terminationtype << endl;  // http://www.alglib.net/translator/man/manual.cpp.html#sub_minbleicresults
        cout << x.tostring(2).c_str() << endl;
    }
    catch (const alglib::ap_error& e) {
        cerr << e.msg << endl;
        return 1;
    }
    catch (const exception& e) {
        cerr << e.what() << endl;
        return 1;
    }
    /*catch (...) {
        http://en.cppreference.com/w/cpp/error/current_exception  exit(1)
    }*/
    return 0;
}
