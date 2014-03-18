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
#include <soylentrecipes/domain/Recipes.h>
#include <soylentrecipes/domain/Food.h>
#include <soylentrecipes/domain/NutrientProfile.h>
#include <soylentrecipes/genetic/Foods.h>

/**
 * Mines a food database for good recipes
 */
class RecipeMiner
{
public:
    RecipeMiner(const NutrientProfile& profile, FoodDatabase& db, int argc, char** argv);
    ~RecipeMiner();

    /**
     * Depth-first search on all seemingly-useful combinations of foods
     *
     * Note: depth-first because of memory use
     * Note: there is a max on the size of a combination
     */
    void mine();

    /**
     * Stop mining
     *
     * May be called asynchronously
     */
    void stop();

private:
    void mine(const std::vector<FoodIt>& foods);
    void examine_recipe(const std::vector<FoodIt>& foods);
    double get_total_recipes(size_t food_count, int combo_size);

private:
    const NutrientProfile& profile;
    Foods _foods;

    bool m_stop;

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
#include <soylentrecipes/genetic/FoodGenotype.h>
#include <beagle/GA.hpp>
#include "RecipeProblem.h"

using namespace std; // TODO shouldn't do this

/**
 * Thrown when mining needs to stop
 */
class TerminationException : public exception {
};

RecipeMiner::RecipeMiner(const NutrientProfile& profile, FoodDatabase& db, int argc, char** argv)
:   profile(profile), _foods(db), m_stop(false), _argc(argc), _argv(argv)
{
}

RecipeMiner::~RecipeMiner() {
}

void RecipeMiner::stop() {
    m_stop = true;
}

void RecipeMiner::mine() {
    vector<FoodIt> foods;

    // mine
    CALLGRIND_START_INSTRUMENTATION;
    clock_t start_time = clock();
    try {
        mine(foods);
    }
    catch (const TerminationException&) {
    }
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

    if (m_stop) {
        throw TerminationException(); // TODO this no longer gets a chance, probably the system class has a func to stop
    }

    // Run genetic algorithm
    System system;

    FoodGenotype::Alloc geno_allocator;
    FitnessMultiObj::Alloc fitness_allocator;// for now we could use FitnessSimple //TODO FitnessMultiObj // TODO need inherit? TODO place multiple objectives in it
    Individual::Alloc individual_allocator(&geno_allocator, &fitness_allocator);

    GA::EvolverES evolver;
    Stats::Alloc stats_alloc;
    HallOfFame::Alloc hall_of_fame_alloc;
    Deme::Alloc deme_alloc(&individual_allocator, &stats_alloc, &hall_of_fame_alloc);
    Vivarium vivarium(&deme_alloc, &stats_alloc, &hall_of_fame_alloc);

    RecipeInitializationOp initRecipeOp(_foods);
    evolver.addOperator(&initRecipeOp);

    evolver.initialize(&system, _argc, _argv);
    evolver.readEvolverFile("beagle.conf");
    evolver.evolve(&vivarium);


    // TODO do you see any mem leaks in this func? I sure do
}

// TODO use this in fitness stuff
void RecipeMiner::examine_recipe(const vector<FoodIt>& foods) {
    examine_total++;

    // solve recipe
    problem_size_sum += foods.size();
    RecipeProblem problem(profile, foods);
    auto result = problem.solve();

    // calculate completeness number (ranges from 0.0 to 1.0)
    // note: nutrients aren't weighted in the completeness number
    double completeness = 0.0;
    for (int i=0; i < result.length(); ++i) {
        completeness += min(1.0, result[i] / profile.get_targets()[i]);
    }
    completeness /= result.length();
}

