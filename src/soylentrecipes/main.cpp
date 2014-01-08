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
#include <signal.h>
#include <assert.h>
#include <stdexcept>
#include "domain/NutrientProfiles.h"
#include "domain/Foods.h"
#include "domain/Recipes.h"
#include "RecipeMiner.h"

//using namespace SOYLENT;
using namespace std;

static RecipeMiner* miner = nullptr;

static void signal_callback(int signum) {
    miner->stop();
}

int main(int argc, char** argv) {
    signal(SIGTERM, signal_callback);
    signal(SIGINT, signal_callback);

    try {
        Database db;
        NutrientProfiles profiles(db);
        NutrientProfile profile = profiles.get(1);

        Foods foods(db, profile);
        Recipes recipes(db);

        miner = new RecipeMiner(profile, foods, recipes);
        miner->mine();
        delete miner;
    }
    catch (const alglib::ap_error& e) {
        // TODO delete miner and stuff
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
