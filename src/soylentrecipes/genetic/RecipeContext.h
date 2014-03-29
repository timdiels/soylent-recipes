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

#include <beagle/GA.hpp>
#include <memory>
#include <soylentrecipes/data_access/FoodDatabase.h>
#include <soylentrecipes/genetic/Foods.h>

/**
 * Cross over of 2 individuals by swapping 2 of their genotypes
 */
class RecipeContext : public Beagle::Context
{
public:
    typedef Beagle::AllocatorT<RecipeContext, Beagle::Context::Alloc> Alloc;
    typedef Beagle::PointerT<RecipeContext, Beagle::Context::Handle> Handle;
    typedef Beagle::ContainerT<RecipeContext, Beagle::Context::Bag> Bag;

public:
    RecipeContext();
    ~RecipeContext();

    Foods& getFoods();
    NutrientProfile& getProfile();

    RecipeContext& operator=(const RecipeContext&);

private:
    std::shared_ptr<Database> _basic_db;
    std::shared_ptr<FoodDatabase> _db;
    std::shared_ptr<Foods> _foods;
    std::shared_ptr<NutrientProfile> _profile;
};
