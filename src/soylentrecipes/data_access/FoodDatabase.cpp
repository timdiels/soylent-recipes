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

#include <stdexcept>
#include "FoodDatabase.h"

using namespace std;
using namespace alglib;

FoodDatabase::FoodDatabase(Database& db)
:   db(db)
{
    // Fill attr_to_index map
    // Note: we assume attribute table doesn't change throughout the execution
    int last_index = -1;
    Query attr_stmt(db, "SELECT id FROM nutrient");
    while (attr_stmt.step()) {
        attr_to_index[attr_stmt.get_int(0)] = ++last_index;
    }

    // Construct inverse
    for (auto item : attr_to_index) {
        index_to_attr[item.second] = item.first;
    }

    // Cache attribute_count
    Query qry(db, "SELECT COUNT(*) FROM nutrient");
    if (!qry.step()) {
        throw runtime_error("Wtf can't count");
    }
    attribute_count = qry.get_int(0);
}

NutrientProfile FoodDatabase::get_profile(int id) {
    // targets, maxima
    Query profile_qry(db, "SELECT pa.attribute_id, pa.target_value, pa.max_value FROM profile p INNER JOIN profile_attribute pa ON p.id = pa.profile_id WHERE id = ?");
    profile_qry.bind_int(1, id);

    real_1d_array targets;
    real_1d_array maxima;
    targets.setlength(nutrient_count());
    maxima.setlength(nutrient_count());

    while (profile_qry.step()) {
        auto index = attr_to_index[profile_qry.get_int(0)];
        targets[index] = profile_qry.get_double(1);
        maxima[index] = profile_qry.get_double(2);
    }

    return NutrientProfile(targets, maxima);
}

size_t FoodDatabase::nutrient_count() {
    return attribute_count;
}

size_t FoodDatabase::cluster_count() {
    return count("cluster_");
}

size_t FoodDatabase::food_count() {
    return count("food");
}

size_t FoodDatabase::count(string table) {
    Query qry(db, "SELECT COUNT(*) FROM " + table);
    if (!qry.step()) {
        throw runtime_error("Wtf can't count");
    }
    return qry.get_int(0);
}

void FoodDatabase::begin_transaction() {
    static Query stmt(db, "BEGIN");
    stmt.step();
    stmt.reset();
}

void FoodDatabase::end_transaction() {
    static Query stmt(db, "END");
    stmt.step();
    stmt.reset();
}

