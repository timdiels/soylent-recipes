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
#include <ctime>
#include <soylentrecipes/domain/Food.h>
#include <soylentrecipes/genetic/Foods.h>

/**
 * Mines a food database for good recipes
 */
class RecipeMiner
{
public:
    RecipeMiner(FoodDatabase& db, int argc, char** argv);

    /**
     * Depth-first search on all seemingly-useful combinations of foods
     *
     * Note: depth-first because of memory use
     * Note: there is a max on the size of a combination
     */
    void mine();

private:
    void mine(const std::vector<FoodIt>& foods); // TODO old leftover stuff is quite left over
    void examine_recipe(const std::vector<FoodIt>& foods);
    double get_total_recipes(size_t food_count, int combo_size);

private:
    FoodDatabase& _db;
    Foods _foods;

    int _argc; // Note: with naming conventions consistency is key, good thing this project is small
    char** _argv;

    // stats
    long examine_total = 0;  // how many food combos were offered for solving
    long problem_size_sum = 0;  // sum of len(foods) of recipe problems that were solved
};


/////////////////////////////////////
// hpp
/////////////////////////////////////

#include <iostream>
#include <exception>
#include <valgrind/callgrind.h>
#include <soylentrecipes/genetic/Foods.h>
#include <soylentrecipes/genetic/RecipeInitializationOp.h>
#include <soylentrecipes/genetic/RecipeCrossoverOp.h>
#include <soylentrecipes/genetic/RecipeMutationOp.h>
#include <soylentrecipes/genetic/RecipeEvalOp.h>
#include <soylentrecipes/genetic/RecipeIndividual.h>
#include <beagle/GA.hpp>

using namespace std; // TODO shouldn't do this

RecipeMiner::RecipeMiner(FoodDatabase& db, int argc, char** argv)
:   _db(db), _foods(db), _argc(argc), _argv(argv)
{
}

void RecipeMiner::mine() {
    vector<FoodIt> foods;

    // mine
    CALLGRIND_START_INSTRUMENTATION;
    clock_t start_time = clock();
    mine(foods);
    clock_t end_time = clock();
    CALLGRIND_STOP_INSTRUMENTATION;
    CALLGRIND_DUMP_STATS;

    // print stats
    double elapsed_time = (end_time - start_time) / static_cast<double>(CLOCKS_PER_SEC);
    long total_calculated = examine_total;
    double time_per_problem = elapsed_time * 1000.0 / total_calculated; // in ms
    long food_count = -1; // TODO distance(foods_begin, foods_end);

    cout << endl;
    cout << "Time spent per problem: " << time_per_problem << " ms" << endl;
    cout << "Processor time used since program start: " << elapsed_time / 60.0 << " minutes" << endl;
    cout << "Average problem size: " << problem_size_sum / static_cast<double>(total_calculated) << " foods" << endl;
    cout << "Food count: " << food_count << endl;
}

void RecipeMiner::mine(const vector<FoodIt>& foods) {
    using namespace Beagle;

    System::Handle system = new System;

    RecipeIndividual::Alloc::Handle individual_allocator = new RecipeIndividual::Alloc;

    GA::EvolverES::Handle evolver = new GA::EvolverES;
    Deme::Alloc::Handle deme_alloc = new Deme::Alloc(individual_allocator);
    Vivarium::Handle vivarium = new Vivarium(deme_alloc);

    RecipeInitializationOp::Handle init_recipe_op = new RecipeInitializationOp(_foods);
    evolver->addOperator(init_recipe_op);

    NutrientProfile profile = _db.get_profile(1);
    RecipeEvalOp::Handle recipe_eval_op = new RecipeEvalOp(profile);
    evolver->addOperator(recipe_eval_op);

    RecipeCrossoverOp::Handle cross_over_op = new RecipeCrossoverOp;
    evolver->addOperator(cross_over_op);

    RecipeMutationOp::Handle mutation_op = new RecipeMutationOp(_foods);
    evolver->addOperator(mutation_op);

    evolver->initialize(system, _argc, _argv);
    evolver->evolve(vivarium);

    //vivarium.getHallOfFame();
    //writePopulation
}

// TODO use this in fitness stuff
void RecipeMiner::examine_recipe(const vector<FoodIt>& foods) {
    examine_total++;
    problem_size_sum += foods.size();

    
}

