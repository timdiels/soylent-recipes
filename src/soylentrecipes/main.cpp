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

#include <iostream>
#include <vector>
#include <assert.h>
#include <stdexcept>
#include "domain/NutrientProfiles.h"
#include "domain/Foods.h"
#include "RecipeProblem.h"

//using namespace SOYLENT;
using namespace std;

int main(int argc, char** argv) {
    try {
        Database db;
        NutrientProfiles profiles(db);
        NutrientProfile profile = profiles.get(1);

        Foods foods(db);
        vector<Food> foods_;
        foods_.push_back(foods.get(1, profile));
        foods_.push_back(foods.get(300, profile));
        foods_.push_back(foods.get(500, profile));
        foods_.push_back(foods.get(1000, profile));
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
