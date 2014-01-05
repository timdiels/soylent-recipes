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
#include <stdexcept>
#include <algorithm>

//using namespace SOYLENT;
using namespace std;
using namespace alglib;

class Nutrient
{
public:
    Nutrient(int id, string description, string unit, double target, double max_)
    :   id(id), description(description), unit(unit), target(target), max_(max_)
    {
    }

    string get_description() const {
        return description;
    }

    string get_unit() const {
        return unit;
    }

    double get_target() const {
        return target;
    }

    double get_max() const {
        return max_;
    }

private:
    int id;
    string description;
    string unit; // e.g. "mg", "ml", "kCal"

    double target; // desired daily amount
    double max_; // maximum daily amount
};

/**
 * A list of constrained nutrients
 */
class NutrientProfile
{
public:
    NutrientProfile()
    {
        // TODO don't hardcode
        nutrients.push_back(Nutrient(0, "Calories", "kcal", 2500, INFINITY));
        nutrients.push_back(Nutrient(1, "Carbohydrates", "g", 400, INFINITY));
        nutrients.push_back(Nutrient(2, "Protein", "g", 120, INFINITY));
        nutrients.push_back(Nutrient(3, "Total Fat", "g", 65, INFINITY));
        nutrients.push_back(Nutrient(4, "Omega-3 Fatty Acids", "g", 0.75, 3.0));

                /*
Omega-6 Fatty Acids (g)	1.5	17
Total Fiber (g)	40	
Cholesterol (mg)	0	300
Vitamin A (IU)	5000	10000
Vitamin B6 (mg)	2	100
Vitamin B12 (ug)	6	
Vitamin C (mg)	60	2000
Vitamin D (IU)	400	4000
Vitamin E (IU)	30	1500
Vitamin K (ug)	80	
Thiamin (mg)	1.5	
Riboflavin (mg)	1.7	
Niacin (mg)	20	35
Folate (ug)	400	1000
Pantothenic Acid (mg)	10	
Biotin (ug)	300	
Choline (mg)	550	3500
Calcium (g)	1	2.5
Chloride (g)	3.4	
Chromium (ug)	120	600
Copper (mg)	2	10
Iodine (ug)	150	1100
Iron (mg)	18	45
Magnesium (mg)	400	
Manganese (mg)	2	11
Molybdenum (ug)	75	2000
Phosphorus (g)	1	4
Potassium (g)	3.5	6
Selenium (ug)	70	400
Sodium (g)	2.4	2.4
Sulfur (g)	2	
Zinc (mg)	15	40
*/
    }

    const vector<Nutrient>& get_nutrients() const {
        return nutrients;
    }

private:
    vector<Nutrient> nutrients;
};

/**
 * A food (e.g. bread)
 */
class Food
{
public:
    string get_description() const {
        return description;
    }

    const vector<double>& get_nutrient_values() const {
        return nutrient_values;
    }

private:
public: // TODO
    string description;
    vector<double> nutrient_values;
};

/**
 * The problem of balancing the amounts of ingredients in a soylent recipe
 */
class RecipeProblem
{
public:
    RecipeProblem(const NutrientProfile& profile, const vector<Food>& foods) {
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

    real_1d_array solve() {
        minbleicsetcond(solver, 0, 0, 0, 1000); // 1000 its max

        minbleicoptimize(solver, RecipeProblem::f, nullptr, this);

        minbleicreport report;
        real_1d_array x;
        x.setlength(a.cols());
        minbleicresults(solver, x, report);

        cout << report.terminationtype << endl;  // http://www.alglib.net/translator/man/manual.cpp.html#sub_minbleicresults
        return x;
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

private:
    real_2d_array a;
    real_1d_array y;

    minbleicstate solver;
};

int main(int argc, char** argv) {
    try {
        NutrientProfile nutrient_profile;

        vector<Food> foods;
        Food f;

        Food food;
        food.nutrient_values.push_back(0.0);
        food.nutrient_values.push_back(0.0);
        food.nutrient_values.push_back(0.0);
        food.nutrient_values.push_back(0.0);
        food.nutrient_values.push_back(0.0);

        f = food;
        f.description = "f0";
        f.nutrient_values[0] = 1.0;
        assert(f.nutrient_values.size() == nutrient_profile.get_nutrients().size());
        foods.push_back(f);

        f = food;
        f.description = "f04";
        f.nutrient_values[0] = 1.0;
        f.nutrient_values[4] = 1.0;
        assert(f.nutrient_values.size() == nutrient_profile.get_nutrients().size());
        foods.push_back(f);

        f = food;
        f.description = "f123";
        f.nutrient_values[1] = 2.0;
        f.nutrient_values[2] = 1.0;
        f.nutrient_values[3] = 1.0;
        cout << f.nutrient_values.at(0) << endl;
        assert(f.nutrient_values.size() == nutrient_profile.get_nutrients().size());
        foods.push_back(f);

        RecipeProblem problem(nutrient_profile, foods);
        auto result = problem.solve();
        for (int i=0; i < result.length(); ++i) {
            auto& food = foods.at(i);
            cout << food.get_description() << ": " << result[i] << endl;
        }
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
