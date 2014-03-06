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

#include <map>
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
    void get_foods(OutputIterator food_record_it);

    NutrientProfile get_profile(int id);

    void delete_recipes();

    size_t nutrient_count();
    size_t food_count();
    size_t recipe_count();

    template <class InputIterator>
    void add_recipe(std::string type, InputIterator ids_begin, InputIterator ids_end, double completeness);

    FoodDatabase(const FoodDatabase&) = delete;

private:
    void execute(std::string sql);
    size_t count(std::string table);
    void begin_transaction();
    void end_transaction();

private:
    Database& db;

    // cached values
    std::map<int, int> attr_to_index; // attribute ids might not be consecutive, so we need a map to map them to consecutive indices when representing them as an ordered sequence
    std::map<int, int> index_to_attr;
    size_t attribute_count;
};


/////////////////////////////////////
// hpp
/////////////////////////////////////

#include <soylentrecipes/data_access/Query.h>
#include <vector>
#include <iostream>
#include <sstream>

class FoodRecord {
public:
    int id;
    std::string description;
    std::vector<double> values;
};

template <class OutputIterator>
void FoodDatabase::get_foods(OutputIterator food_tuple_it) {
    // Require: food table contains at least 1 record
    using namespace std;
    FoodRecord record;

    Query stmt(db, "SELECT f.id, f.name, fa.attribute_id, fa.value FROM food f INNER JOIN food_attribute fa ON f.id = fa.food_id ORDER BY f.id");
    record.id = -1;
    record.values.resize(nutrient_count());

    while (stmt.step()) {
        auto id = stmt.get_int(0);
        if (id != record.id) {
            if (record.id != -1) {
                *food_tuple_it++ = record;
            }
            record.id = stmt.get_int(0);
            record.description = stmt.get_string(1);
            fill(record.values.begin(), record.values.end(), 0.0);
        }

        record.values.at(attr_to_index[stmt.get_int(2)]) = stmt.get_double(3);
    }
    *food_tuple_it++ = record;
}

template <class InputIterator>
void FoodDatabase::add_recipe(std::string type, InputIterator ids_begin, InputIterator ids_end, double completeness) {
    begin_transaction();

    // insert recipe
    Query insert_stmt(db, "INSERT INTO recipe (completeness) VALUES (?)");
    insert_stmt.bind_double(1, completeness);
    insert_stmt.step();

    auto recipe_id = insert_stmt.last_insert_id();

    // insert items/lines of recipe
    Query stmt(db, "INSERT INTO recipe_" + type + " VALUES (?, ?)");
    stmt.bind_int(1, recipe_id);
    for (auto it = ids_begin; it != ids_end; it++) {
        stmt.bind_int(2, *it);
        stmt.step();
        stmt.reset();
    }

    end_transaction();
}

