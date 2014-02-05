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

#include <map>
#include "util.h"

using namespace std; // TODO the ugly

/**
 * Clusters by orthogonality, it turns out this algorithm produces absolutely horrible results, as should be expected because I skipped doing any math for this
 */
class ClusterByOrthogonality
{
public:
    template <class ForwardIterator>
    void cluster(ForwardIterator foods_begin, ForwardIterator foods_end);

private:
    bool are_orthogonal(const FoodIt food1, const FoodIt food2);
};

bool ClusterByOrthogonality::are_orthogonal(const FoodIt food1, const FoodIt food2) {
    const double theta = 24.0 * (2.0 * M_PI / 360.0); // the minimum angle between 2 foods for them to be sufficiently different
    const double max_similarity = cos(theta);  // = cos theta, where theta is the minimum angle between 2 foods in a valid combination; 0.3 -> 72 degrees
    return food1->get_similarity(*food2) <= max_similarity;
}

template <class ForwardIterator>
void ClusterByOrthogonality::cluster(ForwardIterator foods_begin, ForwardIterator foods_end) {
    map<FoodIt, vector<FoodIt>> food_groups;

    for (FoodIt food = foods_begin; food != foods_end; food++) {
        bool orthogonal = true;
        for (auto& item : food_groups) {
            if (!are_orthogonal(item.first, food)) {
                orthogonal = false;
                item.second.push_back(food);
                break;
            }
        }
        if (orthogonal) {
            cout << "!";
            food_groups.insert(make_pair(food, vector<FoodIt>()));
        }
        else {
            cout << ".";
        }
    }

    cout << endl;
    for (auto item : food_groups) {
        cout << item.first->get_id() << ": " << item.second.size() << endl;
        /*for (auto f : item.second) {
            cout << f->get_description() << endl;
        }*/
    }

    size_t nutrient_count = foods_begin->as_matrix().length();
    double total_error = 0.0;
    for (auto& cluster : food_groups) {
        vector<Item> items;
        for (auto& food : cluster.second) {
            valarray<double> values(nutrient_count);
            copy(&food->as_matrix()[0], &food->as_matrix()[nutrient_count-1], begin(values));
            items.emplace_back(food->get_id(), values);
        }
        total_error += get_total_error(items.begin(), items.end());
    }

    cout << "Cluster count: " << food_groups.size() << endl;
    cout << "Total error: " << total_error << endl;
    cout << "Average error: " << total_error / distance(foods_begin, foods_end) << endl;
}
