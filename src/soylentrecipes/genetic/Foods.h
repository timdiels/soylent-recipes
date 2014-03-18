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

#include <vector>
#include <soylentrecipes/domain/Food.h>
#include <boost/function_output_iterator.hpp>
#include <beagle/GA.hpp>

using namespace alglib; // TODO only in cpp

/**
 * Collection of Food
 */
class Foods
{
public:
    Foods(FoodDatabase& db) 
    {
        auto emplace_food = [this](const FoodRecord& r) {
            real_1d_array values;
            values.setlength(r.values.size());
            copy(r.values.begin(), r.values.end(), &values[0]);

            _foods.emplace_back(r.id, r.description, values);
        };
        db.get_foods(boost::make_function_output_iterator(emplace_food));
    }

    /**
     * Get a random food
     */
    const Food* get_random(Beagle::Randomizer& randomizer) const {
        return &_foods.at(randomizer.rollInteger(0, get_size()-1));
    }

    int get_size() const {
        return _foods.size();
    }

private:
    Foods(const Foods& food) = delete;

private:
    std::vector<Food> _foods;
};

