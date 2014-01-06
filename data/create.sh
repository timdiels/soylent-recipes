#!/usr/bin/sh

rm soylentrecipes.sqlite
rm errors.log

sqlite3 -init create_db.sql soylentrecipes.sqlite 2>>errors.log

pushd usda_sr26
./convert_to_sql.sh > import.sql
popd
sqlite3 -init usda_sr26/import.sql soylentrecipes.sqlite 2>>errors.log

less errors.log
