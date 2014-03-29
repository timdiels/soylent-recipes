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
#include <soylentrecipes/domain/NutrientProfile.h>
#include <soylentrecipes/domain/Food.h>
#include <soylentrecipes/mining/RecipeProblem.h>
#include <soylentrecipes/genetic/RecipeContext.h>
#include <assert.h>
#include "FoodGenotype.h"
#include "RecipeEvalOp.h"

using namespace std;
using namespace Beagle;

RecipeEvalOp::RecipeEvalOp() 
:   EvaluationOp("RecipeEvalOp")
{
}

Fitness::Handle RecipeEvalOp::evaluate(Individual& individual, Context& context)
{
    auto& profile = reinterpret_cast<RecipeContext&>(context).getProfile();

    assert(individual.size() > 0);

    vector<const Food*> foods;
    for (int i=0;; i++) {
        auto genotype = castHandleT<FoodGenotype>(individual.at(i));

        foods.push_back(genotype->getFood());

        if (individual.at(i) == individual.back())
            break;
    }

    // solve recipe
    RecipeProblem problem(profile, foods.begin(), foods.end());
    auto result = problem.solve();

    // calculate completeness number (ranges from 0.0 to 1.0)
    // note: nutrients aren't weighted in the completeness number
    double completeness = 0.0;
    for (int i=0; i < result.length(); ++i) {
        completeness += min(1.0, result[i] / profile.get_targets()[i]);
    }
    completeness /= result.length();

    // how simple to make is it: value in [0.0, 1.0]
    // (TODO could take into account some attributes added by people on the foods)
    double simplicity = 1.0/individual.size();

    // TODO take into account price

    // combine subscores
    double fitness = 
        + 1.0 * completeness
        + 0.7 * simplicity
        ;
    return new FitnessSimple(fitness);
}
