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
#include <vector>

class NutrientProfile;

class RecipeEvalOp : public Beagle::EvaluationOp 
{
public:
  typedef Beagle::AllocatorT<RecipeEvalOp, Beagle::EvaluationOp::Alloc> Alloc;
  typedef Beagle::PointerT<RecipeEvalOp, Beagle::EvaluationOp::Handle> Handle;
  typedef Beagle::ContainerT<RecipeEvalOp, Beagle::EvaluationOp::Bag> Bag;

public:
  RecipeEvalOp(const NutrientProfile& profile);

  Beagle::Fitness::Handle evaluate(Beagle::Individual&, Beagle::Context&);

private:
  const NutrientProfile& _profile;
};
