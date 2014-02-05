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

#include <string>
#include <sqlite3.h>

class Database;

class Query {
public:
    Query(Database& db, std::string sql);
    ~Query();

    bool step();
    void reset();
    int get_column_count();
    bool is_null(int column);
    int get_int(int column);
    int get_int(int column, int default_);
    std::string get_string(int column);
    double get_double(int column);
    double get_double(int column, double default_);
    void bind_int(int index, int value);
    void bind_double(int index, double value);
    sqlite3_int64 last_insert_id(); // returns id of last inserted row of this database connection (i.e. not per statement!)

private:
    Query(const Query&) = delete;

private:
    Database& db;
    sqlite3_stmt* stmt;
};

