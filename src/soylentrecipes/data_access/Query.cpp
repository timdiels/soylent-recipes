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

#include <assert.h>
#include "Query.h"
#include "Database.h"

using namespace std;

Query::Query(Database& db, string sql)
:   db(db)
{
    db.ensure(sqlite3_prepare_v2(db.connection, sql.c_str(), -1, &stmt, nullptr), "Failed to prepare statement");
}

Query::~Query() {
    db.ensure(sqlite3_finalize(stmt), "Failed to destroy statement");
}

bool Query::step() {
    auto ret = sqlite3_step(stmt);
    db.ensure(ret, "Failed to step statement");
    return ret == SQLITE_ROW;
}

int Query::get_column_count() {
    return sqlite3_column_count(stmt);
}

bool Query::is_null(int column) {
    assert(column < sqlite3_column_count(stmt));
    return sqlite3_column_type(stmt, column) == SQLITE_NULL;
}

int Query::get_int(int column) {
    assert(column < sqlite3_column_count(stmt));
    assert(sqlite3_column_type(stmt, column) == SQLITE_INTEGER);
    return sqlite3_column_int(stmt, column);
}

string Query::get_string(int column) {
    assert(column < sqlite3_column_count(stmt));
    assert(sqlite3_column_type(stmt, column) == SQLITE3_TEXT);
    return reinterpret_cast<const char*>(sqlite3_column_text(stmt, column));
}

double Query::get_double(int column) {
    assert(column < sqlite3_column_count(stmt));
    assert(sqlite3_column_type(stmt, column) == SQLITE_FLOAT);
    return sqlite3_column_double(stmt, column);
}

double Query::get_double(int column, double default_) {
    if (is_null(column)) {
        return default_;
    }

    assert(column < sqlite3_column_count(stmt));
    assert(sqlite3_column_type(stmt, column) == SQLITE_FLOAT);
    return sqlite3_column_double(stmt, column);
}

void Query::bind_int(int index, int value) {
    assert(index > 0);
    db.ensure(sqlite3_bind_int(stmt, index, value), "Failed to bind");
}

void Query::bind_double(int index, double value) {
    assert(index > 0);
    db.ensure(sqlite3_bind_double(stmt, index, value), "Failed to bind");
}

void Query::reset() {
    db.ensure(sqlite3_reset(stmt), "Failed to reset statement");
}

