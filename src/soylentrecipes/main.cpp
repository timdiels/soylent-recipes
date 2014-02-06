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
#include <stdexcept>
#include <memory>
#include <boost/function_output_iterator.hpp>
#include "data_access/FoodDatabase.h"
#include "domain/Recipes.h"
#include "clustering/Clustering.h"
#include "mining/RecipeMiner.h"

//using namespace SOYLENT;
using namespace std;
using namespace alglib;

static RecipeMiner<FoodIt>* miner = nullptr;

static void signal_callback(int signum) {
    miner->stop();
}

void cluster(FoodDatabase& db) {
    // The idea is to reduce the amount of foods to something manageable in this step TODO note in readme
    Clustering alg;
    alg.cluster(db);
}

void mine(FoodDatabase& db) {
    Recipes recipes(db);

    NutrientProfile profile = db.get_profile(1);

    // load clusters into 'pseudo' foods
    std::vector<Food> foods;
    auto emplace_food = [&foods](const ClusterRecord& r) {
        stringstream str;
        str << "Cluster " << r.id;

        real_1d_array values;
        values.setlength(r.values.size());
        copy(r.values.begin(), r.values.end(), &values[0]);

        foods.emplace_back(r.id, str.str(), values);
    };
    db.get_clusters(boost::make_function_output_iterator(emplace_food));

    unique_ptr<RecipeMiner<FoodIt>> miner_(new RecipeMiner<FoodIt>(profile, foods.begin(), foods.end(), recipes));
    miner = miner_.get();
    miner->mine();
}

int main(int argc, char** argv) {
    signal(SIGTERM, signal_callback);
    signal(SIGINT, signal_callback);

    try {
        Database db_;
        FoodDatabase db(db_);

        if (db.cluster_count() == 0) {
            cluster(db);
        }

        if (db.recipe_count() > 0) {
            cout << "Resuming previous mine operation not supported (though it may already have finished)" << endl;
            cout << "Press enter to wipe recipe table and commence mining" << endl;
            cout << "Press C-c to exit without wiping" << endl;
            char c;
            cin >> c;
            db.delete_recipes();
        }
        mine(db);
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
