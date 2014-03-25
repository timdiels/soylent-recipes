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
#include <stdexcept>
#include <memory>
#include "data_access/FoodDatabase.h"
#include "mining/RecipeMiner.h"

using namespace std;

static RecipeMiner* miner = nullptr;

void mine(FoodDatabase& db, int argc, char** argv) {
    unique_ptr<RecipeMiner> miner_(new RecipeMiner(db, argc, argv));
    miner = miner_.get();
    miner->mine();
}

int main(int argc, char** argv) {
    try {
        Database db_;
        FoodDatabase db(db_);

        if (db.recipe_count() > 0) {
            cout << "Resuming previous mine operation not supported (though it may already have finished)" << endl;
            cout << "Wipe recipe table and commence mining? (y/n)" << endl;
            char c;
            cin >> c;
            if (c != 'y' && c != 'Y') return 0;
            db.delete_recipes();
        }
        mine(db, argc, argv);
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
