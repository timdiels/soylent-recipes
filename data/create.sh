#!/usr/bin/sh

pushd usda_sr26
./convert_to_sql.sh > import.sql
popd

rm soylentrecipes.sqlite
rm errors.log
sqlite3 soylentrecipes.sqlite -init create_db.sql 2>>errors.log
sqlite3 soylentrecipes.sqlite -init usda_sr26/import.sql 2>>errors.log
