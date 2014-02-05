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
#include <soylentrecipes/domain/NutrientProfile.h>

/**
 * Mines a food database for good recipes
 */
template <class ForwardIterator>
class RecipeMiner
{
public:
    RecipeMiner(const NutrientProfile& profile, ForwardIterator food_begin, ForwardIterator food_end, Recipes&);
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
    /**
     * Examines combinations of 'foods' with other foods
     *
     * foods: ordered by id
     */
    void mine(const std::vector<FoodIt>& foods);
    void examine_recipe(const std::vector<FoodIt>& foods);

private:
    const NutrientProfile& profile;
    const ForwardIterator foods_begin;
    const ForwardIterator foods_end;
    Recipes& recipes;
    const size_t dimension_count;

    const int max_combo_size = 12;

    bool m_stop;

    // stats
    long examine_rejected = 0;  // how many food combos were rejected due to 'too incomplete'
    long examine_total = 0;  // how many food combos were offered for solving
    long problem_size_sum = 0;  // sum of len(foods) of recipe problems that were solved
};


/////////////////////////////////////
// hpp
/////////////////////////////////////

#include <iostream>
#include <exception>
#include <valgrind/callgrind.h>
#include "RecipeMiner.h"
#include "RecipeProblem.h"

using namespace std; // TODO shouldn't do this

/**
 * Thrown when mining needs to stop
 */
class TerminationException : public exception {
};

template <class ForwardIterator>
RecipeMiner<ForwardIterator>::RecipeMiner(const NutrientProfile& profile, ForwardIterator food_begin, ForwardIterator food_end, Recipes& recipes)
:   profile(profile), foods_begin(food_begin), foods_end(food_end), recipes(recipes), dimension_count(profile.get_targets().length()), m_stop(false)
{
}

template <class ForwardIterator>
RecipeMiner<ForwardIterator>::~RecipeMiner() {
}

template <class ForwardIterator>
void RecipeMiner<ForwardIterator>::stop() {
    m_stop = true;
}

template <class ForwardIterator>
void RecipeMiner<ForwardIterator>::mine() {
    // TODO resume where we last left off
    vector<FoodIt> foods;
    foods.reserve(max_combo_size);

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
    //long max_combo_size = 5; // TODO debug
    double elapsed_time = (end_time - start_time) / static_cast<double>(CLOCKS_PER_SEC);
    long total_calculated = examine_total - examine_rejected;
    double time_per_problem = elapsed_time * 1000.0 / total_calculated; // in ms
    long food_count = distance(foods_begin, foods_end);

    double total_recipes = 1; // max combinations that can be made with given foods
    int k=1;
    for (int i=0; i < max_combo_size; i++) {
        total_recipes *= food_count - i;
        if (i>0) {
            k *= i;
        }
    }
    total_recipes /= k;

    double acceptance_rate = total_calculated / static_cast<double>(examine_total);
    double accepted_recipes = acceptance_rate * total_recipes;

    cout << endl;
    cout << examine_rejected << endl;
    cout << "Rejection percentage (too incomplete): " << examine_rejected / static_cast<double>(examine_total) << endl;
    cout << "Total recipe problems calculated: " << total_calculated << endl;
    cout << "Time spent per problem: " << time_per_problem << " ms" << endl;
    cout << "Processor time used since program start: " << elapsed_time / 60.0 << " minutes" << endl;
    cout << "Average problem size: " << problem_size_sum / static_cast<double>(total_calculated) << " foods" << endl;
    cout << "Food count: " << food_count << endl;
    cout << "Recipe count before rejection: " << total_recipes << endl;
    cout << "Accepted recipes: " << accepted_recipes << endl;
    cout << "Time needed to calculate accepted recipes: " << accepted_recipes * time_per_problem / 1000.0 / 60.0 / 60.0 / 24.0 << " days" << endl;
}

template <class ForwardIterator>
void RecipeMiner<ForwardIterator>::mine(const vector<FoodIt>& foods) {
    if (m_stop) {
        throw TerminationException();
    }

    if (foods.size() < max_combo_size) {
        auto next_foods = foods;
        FoodIt next_food;
        if (foods.empty()) {
            next_food = foods_begin;
        }
        else {
            next_food = foods.back();
            next_food++;
        }

        for (; next_food != foods_end; next_food++) {
            next_foods.push_back(next_food);
            mine(next_foods);
            next_foods.pop_back();
        }
    }

    if (!foods.empty()) {
        examine_recipe(foods);
    }
}

template <class ForwardIterator>
void RecipeMiner<ForwardIterator>::examine_recipe(const vector<FoodIt>& foods) {
    examine_total++;

    // calculate max completeness TODO does this offer any benefit? Is it meaningful?
    {
    double max_completeness = 0.0;
    for (int i=0; i<dimension_count; i++) {
        for (auto& food : foods) {
            if (food->as_matrix()[i] > 0.0) {
                max_completeness += 1.0;
                break;
            }
        }
    }
    max_completeness /= dimension_count;
    if (!recipes.is_useful(max_completeness)) {
        examine_rejected++;
        return; // this recipe won't be useful, so don't bother with calculations
    }
    }

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

    // add recipe
    if (recipes.is_useful(completeness)) {
        recipes.add_recipe(foods, completeness);
        //cout << completeness << endl << endl;
    }
}

