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
#include <libalglib/stdafx.h>
#include <libalglib/linalg.h>
#include <soylentrecipes/data_access/Query.h>
#include "Foods.h"
#include "NutrientProfile.h"

using namespace std;
using namespace alglib;

Foods::Foods(Database& db)
:   db(db)
{
}

Food Foods::get(int id, const NutrientProfile& profile) {
    string description;
    real_1d_array nutrient_values;
    nutrient_values.setlength(profile.get_nutrients().size());

    Query stmt(db, "SELECT * FROM food WHERE id = ?");
    stmt.bind_int(1, id);

    if (stmt.step()) {
        runtime_error("Food not found");
    }

    for (int i=0; i < nutrient_values.length(); i++) {
        nutrient_values[i] = stmt.get_double(4 + i, 0.0);
    }

    Food food(stmt.get_int(0), 
            stmt.get_string(1),
            nutrient_values
    );

    return food;
}

