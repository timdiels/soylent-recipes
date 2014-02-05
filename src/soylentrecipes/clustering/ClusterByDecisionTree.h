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

#include <valarray>

//TODO found clusterings can be evaluated by looking at average/total squared error of each cluster in relation to cluster count

/**
 * Cluster foods by their nutrients
 *
 * using a decision tree.
 *
 * It's somewhat similar to: ftp://ftp.cse.buffalo.edu/users/azhang/disc/disc01/cd1/out/papers/cikm/p20.pdf
 * (or hopefully it will end up being that eventually...)
 */
class ClusterByDecisionTree
{
public:
    void cluster(FoodDatabase&);

private:
    void sort(std::vector<Food*>&, int dimension); // sort foods by dimension'th nutrition value

    template <class ForwardIterator>
    void split(ForwardIterator items_begin, ForwardIterator items_end);

    template <class ForwardIterator>
    std::valarray<double> get_centroid(ForwardIterator items_begin, ForwardIterator items_end);

    template <class ForwardIterator>
    double get_total_error(ForwardIterator items_begin, ForwardIterator items_end);

private:
    const double max_average_error = 0.1; // the max average member distance to a leaf cluster's centroid (a stop criterium for splitting) (L1 norm distance)
};

//////
// cpp TODO
//////

#include <vector>
#include <algorithm>
#include <boost/function_output_iterator.hpp>
#include <boost/iterator/indirect_iterator.hpp>
#include <boost/iterator/transform_iterator.hpp>
#include <boost/iterator/filter_iterator.hpp>

using namespace std;

// TODO make class private (not its fields ^^)
class Item {
public:
    Item(int id, valarray<double> values);
    static valarray<double> get_values(const Item& item);

public:
    int id;
    valarray<double> values;
};

Item::Item(int id, valarray<double> values)
:   id(id), values(values)
{
}

valarray<double> Item::get_values(const Item& item) {
    return item.values;
}

////////////////////////////////////////////////

void ClusterByDecisionTree::cluster(FoodDatabase& db) {
    // convert food to items
    vector<Item> items;
    auto emplace_food = [&items](FoodRecord r) {
        valarray<double> values(r.nutrient_values.size());
        copy(r.nutrient_values.begin(), r.nutrient_values.end(), begin(values));
        items.emplace_back(r.id, values);
    };
    db.get_foods(boost::make_function_output_iterator(emplace_food));

    // get minmax
    auto dimension_count = items.front().values.size();
    vector<double> min_value(dimension_count, INFINITY);
    vector<double> max_value(dimension_count, -INFINITY);
    for (auto& item : items) {
        for (int i=0; i<dimension_count; i++) {
            min_value.at(i) = min(item.values[i], min_value.at(i));
            max_value.at(i) = max(item.values[i], max_value.at(i));
        }
    }

    // normalise nutrient values to [0, 1]
    for (auto& item : items) {
        for (int i=0; i<dimension_count; i++) {
            item.values[i] = (item.values[i] - min_value.at(i)) / max(max_value.at(i) - min_value.at(i), 1.0);
        }
    }

    // start splitting
    auto pointer_to = std::function<Item*(Item&)>([](Item& item){
        return &item;
    });
    vector<Item*> ptrs;
    auto ptrs_begin = boost::make_transform_iterator(items.begin(), pointer_to);
    auto ptrs_end = boost::make_transform_iterator(items.end(), pointer_to);
    split(ptrs_begin, ptrs_end);
    cout << endl;
}

// TODO might also want to rerun later with L2 norm instead of L1 norm for distance
/**
 * ForwardIterator: iter to pointer of item
 */
template <class ForwardIterator>
void ClusterByDecisionTree::split(ForwardIterator items_begin, ForwardIterator items_end) {
    cout << "!";
    if (items_begin == items_end) return;

    auto deref_begin = boost::make_indirect_iterator(items_begin);
    auto deref_end = boost::make_indirect_iterator(items_end);

    // check split stop criterium
    double average_error = get_total_error(deref_begin, deref_end) / distance(deref_begin, deref_end); // note: = average distance to centroid

    cout << distance(items_begin, items_end) << " ";
    cout << average_error << " ";
    if (average_error <= max_average_error) {
        //cout << average_error << endl;
        // TODO cout cluster for debugging info
        return;  // stop splitting
    }

    // split on dimension with best information gain at its median's upper/lower limit
    valarray<double> centroid = get_centroid(deref_begin, deref_end);
    copy(begin(centroid), end(centroid), ostream_iterator<double>(cout, ","));
    cout << endl;
    size_t dimension_count = centroid.size();
    double smallest_error = INFINITY;
    vector<Item*> items1;
    vector<Item*> items2;
    for (int i=0; i < dimension_count; i++) {
        auto ge_centroid = std::function<bool(Item*)>([&centroid, i](Item* item) {
            return centroid[i] <= item->values[i];
        });
        // TODO std partition OP
        auto partition_begin = boost::make_filter_iterator(ge_centroid, items_begin, items_end);
        auto partition_end = boost::make_filter_iterator(ge_centroid, items_end, items_end);
        double total_error = get_total_error(make_indirect_iterator(partition_begin), make_indirect_iterator(partition_end));

        auto partition_begin2 = boost::make_filter_iterator(not1(ge_centroid), items_begin, items_end);
        auto partition_end2 = boost::make_filter_iterator(not1(ge_centroid), items_end, items_end);
        total_error += get_total_error(make_indirect_iterator(partition_begin2), make_indirect_iterator(partition_end2));

        if (total_error < smallest_error) {
            smallest_error = total_error;
            items1.clear();
            items2.clear();
            copy(partition_begin, partition_end, back_inserter(items1));
            copy(partition_begin2, partition_end2, back_inserter(items2));
        }
    }
    // Note: median might work better (but is probably more expensive to compute), or CLTree method

    split(items1.begin(), items1.end());
    split(items2.end(), items2.end());
}

template <class ForwardIterator>
valarray<double> ClusterByDecisionTree::get_centroid(ForwardIterator items_begin, ForwardIterator items_end) {
    auto values_begin = boost::make_transform_iterator(items_begin, Item::get_values);
    auto values_end = boost::make_transform_iterator(items_end, Item::get_values);
    return accumulate(values_begin, values_end, valarray<double>(values_begin->size())) / static_cast<double>(distance(values_begin, values_end));
}

template <class ForwardIterator>
double ClusterByDecisionTree::get_total_error(ForwardIterator items_begin, ForwardIterator items_end) {
    auto centroid = get_centroid(items_begin, items_end);

    auto l2_norm_squared = [&centroid](const Item& item) {
        valarray<double> diff = centroid - item.values;
        return inner_product(begin(diff), end(diff), begin(diff), 0.0);
    };

    /*auto l1_norm = [&centroid](const Item& item) {
        valarray<double> diff = centroid - item.values;
        diff = diff.apply(abs);
        return diff.sum();
    };*/

    auto distances_begin = boost::make_transform_iterator(items_begin, l2_norm_squared);
    auto distances_end = boost::make_transform_iterator(items_end, l2_norm_squared);
    return accumulate(distances_begin, distances_end, 0.0);
}
