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
    void get_foods(OutputIterator food_tuple_it);

    NutrientProfile get_profile(int id);
    size_t nutrient_count();
    size_t food_count();

    template <class ForwardIterator, class InputIterator>
    void add_cluster(ForwardIterator centroid_begin, ForwardIterator centroid_end, InputIterator food_ids_begin, InputIterator food_ids_end);

private:
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
    int cluster_id;
    std::string description;
    std::vector<double> nutrient_values;
};

template <class OutputIterator>
void FoodDatabase::get_foods(OutputIterator food_tuple_it) {
    // Require: food table contains at least 1 record
    using namespace std;
    FoodRecord record;

    Query stmt(db, "SELECT f.id, f.name, fa.attribute_id, fa.value, f.cluster_id FROM food f INNER JOIN food_attribute fa ON f.id = fa.food_id ORDER BY f.id");
    record.id = -1;
    record.nutrient_values.resize(nutrient_count());

    while (stmt.step()) {
        auto id = stmt.get_int(0);
        if (id != record.id) {
            if (record.id != -1) {
                *food_tuple_it++ = record;
            }
            record.id = stmt.get_int(0);
            record.description = stmt.get_string(1);
            record.cluster_id = stmt.get_int(4, 0);
            fill(record.nutrient_values.begin(), record.nutrient_values.end(), 0.0);
        }

        record.nutrient_values.at(attr_to_index[stmt.get_int(2)]) = stmt.get_double(3);
    }
    *food_tuple_it++ = record;
}

template <class ForwardIterator, class InputIterator>
void FoodDatabase::add_cluster(ForwardIterator centroid_begin, ForwardIterator centroid_end, InputIterator food_ids_begin, InputIterator food_ids_end) {
    using namespace std;

    begin_transaction();

    // insert cluster
    Query insert_stmt(db, "INSERT INTO cluster_ VALUES(NULL)");
    insert_stmt.step();
    auto cluster_id = insert_stmt.last_insert_id();

    // insert cluster attributes
    Query attr_stmt(db, "INSERT INTO cluster_attribute VALUES(?, ?, ?)");
    
    attr_stmt.bind_int(1, cluster_id);
    for (auto it = centroid_begin; it!=centroid_end; it++) {
        attr_stmt.bind_int(2, index_to_attr[distance(centroid_begin, it)]);
        attr_stmt.bind_double(3, *it);
        attr_stmt.step();
        attr_stmt.reset();
    }

    // update foods to use cluster (note: mysql doesn't handle large amount of params well, so we use a stringstream to work around it)
    ostringstream qstr;
    qstr << "UPDATE food SET cluster_id = ? WHERE id IN ("
        << *food_ids_begin;
    for (auto it = food_ids_begin+1; it != food_ids_end; it++) {
        qstr << ", " << *it;
    }
    qstr << ")";
    Query update_stmt(db, qstr.str());
    update_stmt.bind_int(1, cluster_id);
    update_stmt.step();

    end_transaction();
}

