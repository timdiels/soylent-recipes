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
#include "FoodNotFoundException.h"
#include "Food.h"

class NutrientProfile;

class Foods
{
public:
    Foods(Database& db, const NutrientProfile& profile);

    // These iterators are promised not to invalidate
    FoodIt begin();
    FoodIt end();

private:
    Database& db;
    std::vector<Food> foods;
};

