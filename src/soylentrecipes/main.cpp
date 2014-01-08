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

class Query;
class Database {
public:
    Database()
    {
        ensure(sqlite3_open("soylentrecipes.sqlite", &connection), "Failed to open sqlite db");
    }

    ~Database()
    {
        sqlite3_close(connection);
    }

    void ensure(int code, string msg) {
        if (code != SQLITE_OK && code != SQLITE_ROW && code != SQLITE_DONE) {
            throw_(msg);
        }
    }

    void throw_(string msg) {
        throw runtime_error(msg + ": " + sqlite3_errmsg(connection));
    }

private:
    Database(const Database&) = delete;

private:
    sqlite3* connection;

    friend Query;
};

class Query {
public:
    Query(Database& db, string sql)
    :   db(db)
    {
        db.ensure(sqlite3_prepare_v2(db.connection, sql.c_str(), -1, &stmt, nullptr), "Failed to prepare statement");
    }

    ~Query() {
        db.ensure(sqlite3_finalize(stmt), "Failed to destroy statement");
    }

    bool step() {
        auto ret = sqlite3_step(stmt);
        db.ensure(ret, "Failed to step statement");
        return ret == SQLITE_ROW;
    }

    bool is_null(int column) {
        assert(column < sqlite3_column_count(stmt));
        return sqlite3_column_type(stmt, column) == SQLITE_NULL;
    }

    int get_int(int column) {
        assert(column < sqlite3_column_count(stmt));
        assert(sqlite3_column_type(stmt, column) == SQLITE_INTEGER);
        return sqlite3_column_int(stmt, column);
    }

    string get_string(int column) {
        assert(column < sqlite3_column_count(stmt));
        assert(sqlite3_column_type(stmt, column) == SQLITE3_TEXT);
        return reinterpret_cast<const char*>(sqlite3_column_text(stmt, column));
    }

    double get_double(int column) {
        assert(column < sqlite3_column_count(stmt));
        assert(sqlite3_column_type(stmt, column) == SQLITE_FLOAT);
        return sqlite3_column_double(stmt, column);
    }

    double get_double(int column, double default_) {
        if (is_null(column)) {
            return default_;
        }

        assert(column < sqlite3_column_count(stmt));
        assert(sqlite3_column_type(stmt, column) == SQLITE_FLOAT);
        return sqlite3_column_double(stmt, column);
    }

    void bind_int(int index, int value) {
        db.ensure(sqlite3_bind_int(stmt, index, value), "Failed to bind");
    }

private:
    Query(const Query&) = delete;

private:
    Database& db;
    sqlite3_stmt* stmt;
};

class NutrientProfiles
{
public:
    NutrientProfiles(Database& db)
    :   db(db)
    {
    }

    NutrientProfile get(int id) {
        vector<Nutrient> nutrients;

        Query profile_qry(db, "SELECT * FROM profile WHERE id = ?");
        profile_qry.bind_int(1, id);
        if (!profile_qry.step()) {
            runtime_error("Profile not found");
        }

        Query nutrient_qry(db, "SELECT * FROM nutrient ORDER BY id");
        while (nutrient_qry.step()) {
            int id = nutrient_qry.get_int(0);
            Nutrient nutrient(id, 
                    nutrient_qry.get_string(1),
                    nutrient_qry.get_string(2), 
                    profile_qry.get_double(2 + id * 2),
                    profile_qry.get_double(2 + id * 2 + 1)
            );
            nutrients.push_back(nutrient);
        }

        return NutrientProfile(nutrients);
    }

private:
    Database& db;
};

class Foods
{
public:
    Foods(Database& db)
    :   db(db)
    {
    }

    Food get(int id, const NutrientProfile& profile) {
        string description;
        vector<double> nutrient_values;

        Query stmt(db, "SELECT * FROM food WHERE id = ?");
        stmt.bind_int(1, id);

        if (stmt.step()) {
            runtime_error("Food not found");
        }

        for (int i=0; i < profile.get_nutrients().size(); i++) {
            nutrient_values.push_back(stmt.get_double(4 + i, 0.0));
        }

        Food food(stmt.get_int(0), 
                stmt.get_string(1),
                nutrient_values
        );

        return food;
    }

private:
    Database& db;
};

// math
#include "RecipeProblem.h"

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

        RecipeProblem problem(profile, foods_);
        auto result = problem.solve();
        for (int i=0; i < result.length(); ++i) {
            auto& food = foods_.at(i);
            cout << food.get_description() << ": " << result[i] << endl;
        }

        // calculate completeness number (ranges from 0.0 to 1.0)
        // note: nutrients aren't weighted in the completeness number
        double completeness = 0.0;
        for (int i=0; i < result.length(); ++i) {
            auto& nutrient = profile.get_nutrients()[i];
            completeness += min(1.0, result[i] / nutrient.get_target());
        }
        completeness /= result.length();
        cout << completeness << endl;

        // TODO drop food combos with completeness < 50%
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
