soylent-recipes
===============

Mines the USDA food database for food combinations that match the nutrient
profile in the database. Prints found combinations to stdout.

Compilation
-----------

Dependencies (install them):

- http://www.alglib.net/download.php
- sqlite3

Steps:

1. cd data
2. ./create.sh  # press C-d at every sqlite prompt, and q at the end to exit 'less'
3. cd build/release
4. ./cmake\_
5. make
6. cp ../../data/soylentrecipes.sqlite .

Now in order to run it type: ./soylentrecipes
