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

#include <valarray>
#include <vector>
#include <algorithm>
#include <boost/function_output_iterator.hpp>
#include <boost/iterator/indirect_iterator.hpp>
#include <boost/iterator/transform_iterator.hpp>
#include <boost/iterator/filter_iterator.hpp>
#include <valgrind/callgrind.h>
#include <libalglib/dataanalysis.h>

using namespace std;
using namespace alglib;

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
template <class ForwardIterator>
valarray<double> get_centroid(ForwardIterator items_begin, ForwardIterator items_end) {
    assert(items_begin != items_end);
    auto values_begin = boost::make_transform_iterator(items_begin, Item::get_values);
    auto values_end = boost::make_transform_iterator(items_end, Item::get_values);
    return accumulate(values_begin, values_end, valarray<double>(values_begin->size())) / static_cast<double>(distance(values_begin, values_end));
}

template <class ForwardIterator>
double get_total_error(ForwardIterator items_begin, ForwardIterator items_end) {
    if (items_begin == items_end) return 0.0;

    auto centroid = get_centroid(items_begin, items_end);

    auto l2_norm_squared = [&centroid](const Item& item) {
        valarray<double> diff = centroid - item.values;
        return inner_product(begin(diff), end(diff), begin(diff), 0.0);
    };

    auto distances_begin = boost::make_transform_iterator(items_begin, l2_norm_squared);
    auto distances_end = boost::make_transform_iterator(items_end, l2_norm_squared);
    return accumulate(distances_begin, distances_end, 0.0);
}
