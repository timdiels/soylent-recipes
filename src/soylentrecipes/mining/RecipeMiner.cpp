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

#include "RecipeMiner.h"
#include <iostream>
#include <exception>
#include <valgrind/callgrind.h>
#include <ctime>
#include <soylentrecipes/genetic/RecipeInitializationOp.h>
#include <soylentrecipes/genetic/RecipeCrossoverOp.h>
#include <soylentrecipes/genetic/RecipeMutationOp.h>
#include <soylentrecipes/genetic/RecipeEvalOp.h>
#include <soylentrecipes/genetic/RecipeIndividual.h>
#include <soylentrecipes/genetic/RecipeContext.h>
#include <soylentrecipes/mining/RecipeProblem.h>
#include <beagle/GA.hpp>

using namespace std;
using namespace Beagle;

RecipeMiner::RecipeMiner(int argc, char** argv)
:   _argc(argc), _argv(argv)
{
}

void RecipeMiner::mine() {
    // mine
    CALLGRIND_START_INSTRUMENTATION;
    clock_t start_time = clock();
    mine_();
    clock_t end_time = clock();
    CALLGRIND_STOP_INSTRUMENTATION;
    CALLGRIND_DUMP_STATS;

    // print stats
    double elapsed_time = (end_time - start_time) / static_cast<double>(CLOCKS_PER_SEC);
    long food_count = 8000; // TODO don't hardcode
    RecipeProblem::print_stats(elapsed_time, food_count);
}

void RecipeMiner::mine_() {
    RecipeContext::Alloc::Handle context_alloc = new RecipeContext::Alloc;
    System::Handle system = new System(context_alloc);

    RecipeIndividual::Alloc::Handle individual_allocator = new RecipeIndividual::Alloc;

    GA::EvolverES::Handle evolver = new GA::EvolverES;
    Deme::Alloc::Handle deme_alloc = new Deme::Alloc(individual_allocator);
    Vivarium::Handle vivarium = new Vivarium(deme_alloc);

    RecipeInitializationOp::Handle init_recipe_op = new RecipeInitializationOp();
    evolver->addOperator(init_recipe_op);

    RecipeEvalOp::Handle recipe_eval_op = new RecipeEvalOp;
    evolver->addOperator(recipe_eval_op);

    RecipeCrossoverOp::Handle cross_over_op = new RecipeCrossoverOp;
    evolver->addOperator(cross_over_op);

    RecipeMutationOp::Handle mutation_op = new RecipeMutationOp();
    evolver->addOperator(mutation_op);

    evolver->initialize(system, _argc, _argv);
    evolver->evolve(vivarium);
}

