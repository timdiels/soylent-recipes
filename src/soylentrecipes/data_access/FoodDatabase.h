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

#pragma once

#include <soylentrecipes/data_access/Database.h>
#include <soylentrecipes/domain/NutrientProfile.h>

/**
 * Allows fetching food things from disk
 */
class FoodDatabase
{
public:
    FoodDatabase(Database& db);

    template <class OutputIterator>
    void get_foods(OutputIterator food_tuple_it);

    NutrientProfile get_profile(int id);

private:
    Database& db;
};


/////////////////////////////////////
// hpp
/////////////////////////////////////

#include <soylentrecipes/data_access/Query.h>
#include <vector>

class FoodRecord {
public:
    int id;
    std::string description;
    std::vector<double> nutrient_values;
};

template <class OutputIterator>
void FoodDatabase::get_foods(OutputIterator food_tuple_it) {
    using namespace std;
    using namespace alglib;
    FoodRecord record;

    Query stmt(db, "SELECT * FROM food");
    record.nutrient_values.resize(stmt.get_column_count() - 4);

    while (stmt.step()) {
        for (int i=0; i < record.nutrient_values.size(); i++) {
            record.nutrient_values.at(i) = stmt.get_double(4 + i, 0.0);
        }

        record.id = stmt.get_int(0);
        record.description = stmt.get_string(1);
        *food_tuple_it++ = record;
    }
}
