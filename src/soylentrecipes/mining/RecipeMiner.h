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

/**
 * Mines a food database for good recipes
 */
class RecipeMiner
{
public:
    RecipeMiner(int argc, char** argv);

    /**
     * Depth-first search on all seemingly-useful combinations of foods
     *
     * Note: depth-first because of memory use
     * Note: there is a max on the size of a combination
     */
    void mine();

private:
    void mine_();

private:
    int _argc;
    char** _argv;
};

