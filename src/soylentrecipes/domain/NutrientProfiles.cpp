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

#include <vector>
#include <stdexcept>
#include <soylentrecipes/data_access/Query.h>
#include "NutrientProfiles.h"
#include "Nutrient.h"
#include "NutrientProfile.h"

using namespace std;

NutrientProfiles::NutrientProfiles(Database& db)
:   db(db)
{
}

NutrientProfile NutrientProfiles::get(int id) {
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

