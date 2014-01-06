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

//using namespace SOYLENT;
using namespace std;

// data storage classes
#include "Nutrient.h"
#include "NutrientProfile.h"
#include "Food.h"

// data retrieval classes
#include <sqlite3.h>

class Sqlite3Db {
public:
    Sqlite3Db()
    {
        if (sqlite3_open("soylentrecipes.sqlite", &connection) != SQLITE_OK) {
            runtime_error("Failed to open sqlite db");
        }
    }

    ~Sqlite3Db()
    {
        sqlite3_close(connection);
    }

    sqlite3_stmt* prepare(string sql) {
        sqlite3_stmt* stmt;
        if (sqlite3_prepare_v2(connection, sql.c_str(), -1, &stmt, nullptr) != SQLITE_OK) {
            runtime_error("Failed to prepare statement");
        }
        return stmt;
    }

    int step(sqlite3_stmt* stmt) {
        auto ret = sqlite3_step(stmt);
        if (ret != SQLITE_ROW && ret != SQLITE_DONE) {
            runtime_error("Failed to step statement");
        }
        return ret;
    }

    void finalize(sqlite3_stmt* stmt) {
        if (sqlite3_finalize(stmt) != SQLITE_OK) {
            runtime_error("Failed to destroy statement");
        }
    }

    // throw_sqlite() { http://www.sqlite.org/c3ref/errcode.html }

private:
    sqlite3* connection;
};

class NutrientProfiles
{
public:
    NutrientProfiles(const Sqlite3Db& db)
    :   db(db)
    {
    }

    NutrientProfile get(int id) {
        vector<Nutrient> nutrients;

        sqlite3_stmt* profile_qry = db.prepare("SELECT * FROM profile WHERE id = ?");
        sqlite3_bind_int(profile_qry, 1, id);
        db.step(profile_qry);

        sqlite3_stmt* nutrient_qry = db.prepare("SELECT * FROM nutrient ORDER BY id");
        while (db.step(nutrient_qry) == SQLITE_ROW) {
            int id = sqlite3_column_int(nutrient_qry, 0);
            Nutrient nutrient(id, 
                    reinterpret_cast<const char*>(sqlite3_column_text(nutrient_qry, 1)),
                    reinterpret_cast<const char*>(sqlite3_column_text(nutrient_qry, 2)), 
                    sqlite3_column_double(profile_qry, 2 + id * 2),
                    sqlite3_column_double(profile_qry, 2 + id * 2 + 1)
            );
            nutrients.push_back(nutrient);
        }
        db.finalize(nutrient_qry);

        db.finalize(profile_qry);

        return NutrientProfile(nutrients);
    }

private:
    Sqlite3Db db;
};

// math
#include "RecipeProblem.h"

int main(int argc, char** argv) {
    try {
        Sqlite3Db db;
        NutrientProfiles profiles(db);
        NutrientProfile nutrient_profile = profiles.get(1);

        vector<Food> foods;
        //food.nutrient_values.push_back(0.0);

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
