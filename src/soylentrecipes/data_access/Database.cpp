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
#include <stdexcept>
#include "Database.h"

using namespace std;

Database::Database()
{
    ensure(sqlite3_open("soylentrecipes.sqlite", &connection), "Failed to open sqlite db");
}

Database::~Database()
{
    sqlite3_close(connection);
}

void Database::ensure(int code, string msg) {
    if (code != SQLITE_OK && code != SQLITE_ROW && code != SQLITE_DONE) {
        throw_(msg);
    }
}

void Database::throw_(string msg) {
    throw runtime_error(msg + ": " + sqlite3_errmsg(connection));
}
