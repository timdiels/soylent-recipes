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
    size_t nutrient_count();
    size_t food_count();

    template <class ForwardIterator, class InputIterator>
    void add_cluster(ForwardIterator centroid_begin, ForwardIterator centroid_end, InputIterator food_ids_begin, InputIterator food_ids_end);

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
    FoodRecord record;

    Query stmt(db, "SELECT * FROM food");
    record.nutrient_values.resize(stmt.get_column_count() - 5);

    while (stmt.step()) {
        for (int i=0; i < record.nutrient_values.size(); i++) {
            record.nutrient_values.at(i) = stmt.get_double(5 + i, 0.0);
        }

        record.id = stmt.get_int(0);
        record.description = stmt.get_string(1);
        *food_tuple_it++ = record;
    }
}

template <class ForwardIterator, class InputIterator>
void FoodDatabase::add_cluster(ForwardIterator centroid_begin, ForwardIterator centroid_end, InputIterator food_ids_begin, InputIterator food_ids_end) {
    using namespace std;

    // insert cluster
    string qstr = "INSERT INTO cluster_ VALUES(NULL";
    for (auto it = centroid_begin; it!=centroid_end; it++) {
        qstr += ", ?";
    }
    qstr += ")";
    Query insert_stmt(db, qstr);
    for (auto it = centroid_begin; it!=centroid_end; it++) {
        insert_stmt.bind_double(distance(centroid_begin, it) + 1, *it);
    }
    insert_stmt.step();
    auto cluster_id = insert_stmt.last_insert_id();

    // update foods to use cluster
    Query update_stmt(db, "UPDATE food SET cluster_id = ? WHERE id = ?"); // TODO use id IN (...) to improve performance a plenty
    update_stmt.bind_int(1, cluster_id);
    for (auto it = food_ids_begin; it != food_ids_end; it++) {
        update_stmt.bind_int(2, *it);
        update_stmt.step();
        update_stmt.reset();
    }
}
