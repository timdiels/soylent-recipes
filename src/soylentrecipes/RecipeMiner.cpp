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

#include <iostream>
#include <exception>
#include <valgrind/callgrind.h>
#include "RecipeMiner.h"
#include "RecipeProblem.h"

using namespace std;

/**
 * Thrown when mining needs to stop
 */
class TerminationException : public exception {
};

RecipeMiner::RecipeMiner(const NutrientProfile& profile, Foods& foods, Recipes& recipes)
:   profile(profile), foods(foods), recipes(recipes), m_stop(false)
{
}

RecipeMiner::~RecipeMiner() {
}

void RecipeMiner::stop() {
    m_stop = true;
}

void RecipeMiner::mine() {
    // TODO resume where we last left off
    vector<FoodIt> foods;
    foods.reserve(max_combo_size);

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
    cout << endl;
    cout << "Rejection percentage (too similar): " << orthogonality_rejected / static_cast<double>(orthogonality_total) << endl;
    cout << "Rejection percentage (too incomplete): " << examine_rejected / static_cast<double>(examine_total) << endl;
    long total_calculated = examine_total - examine_rejected;
    cout << "Total recipe problems calculated: " << total_calculated << endl;
    cout << "Time spent per problem: " << elapsed_time * 1000.0 / total_calculated << " ms" << endl;
    cout << "Processor time used since program start: " << elapsed_time / 60.0 << " minutes" << endl;
}

void RecipeMiner::mine(const vector<FoodIt>& foods) {
    if (m_stop) {
        throw TerminationException();
    }

    if (foods.size() < max_combo_size) {
        auto next_foods = foods;
        FoodIt next_food;
        if (foods.empty()) {
            next_food = this->foods.begin();
        }
        else {
            next_food = foods.back();
            next_food++;
        }

        for (; next_food != this->foods.end(); next_food++) {
            if (!are_orthogonal(foods, next_food)) {
                continue;
            }

            next_foods.push_back(next_food);
            mine(next_foods);
            next_foods.pop_back();
        }
    }

    if (!foods.empty()) {
        examine_recipe(foods);
    }
}

bool RecipeMiner::are_orthogonal(const vector<FoodIt>& foods, const FoodIt food) {
    orthogonality_total++;
    for (auto& food_ : foods) {
        if (food_->get_similarity(*food) > max_similarity) {
            orthogonality_rejected++;
            return false;
        }
    }
    return true;
}

void RecipeMiner::examine_recipe(const vector<FoodIt>& foods) {
    examine_total++;

    // calculate max completeness
    {
    double max_completeness = 0.0;
    for (int i=0; i<profile.get_nutrients().size(); i++) {
        for (auto& food : foods) {
            if (food->as_matrix()[i] > 0.0) {
                max_completeness += 1.0;
                break;
            }
        }
    }
    max_completeness /= profile.get_nutrients().size();
    if (!recipes.is_useful(max_completeness))
        examine_rejected++;
        return; // this recipe won't be useful, so don't bother with calculations
    }

    // solve recipe
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

        for (int i=0; i < result.length(); ++i) {
            auto& food = foods.at(i);
            cout << food->as_matrix().tostring(2) << endl; //<< " * " << result[i] << endl;
        }
        cout << completeness << endl << endl;
    }
}

