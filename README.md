soylent-recipes
===============

Mines the USDA food database for food combinations that match the nutrient
profile in the database. Prints found combinations to stdout.

If you already know which foods you want to use but simply want to know the
amounts to take of each, use this:
http://www.neos-guide.org/content/diet-problem-demo.

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

Problem description: Recipe/Diet Problem
----------------------------------------

Let a recipe problem be: given a set of foods, and a nutrition profile, find
the amounts to optimally satisfy the nutrition profile. (This is more commonly known as a
Diet Problem (http://www.neos-guide.org/content/diet-problem))

Each food has m properties/nutrients of an ingredient (the contained amount of magnesium, carbs, ...).

Construct a matrix A with: A_{i,j} = the amount of the i-th property of the j-th food.

With n foods, there are amounts X_1, ..., X_n to find.

The nutrient profile provides us with Y_i and M_i for each nutrient. Y_i is the desired amount of nutrient i, M_i is the max allowed amount of nutrient i.

This leads to
- m equations, j=1,2,...m: X_1 A_{1,j} + ... + X_n A_{n,j} = Y_i. 
- m inequalities, j=1,2,...m: X_1 A_{1,j} + ... + X_n A_{n,j} <= M_i. 

Which is a constrained least squares problem.

Algorithm
---------

The algorithm used is an active-set algorithm. Namely: http://www.alglib.net/optimization/boundandlinearlyconstrained.php#header1.

The function f to mimimize is: \lnorm A\*x - y \rnorm_2

The gradient of f(x) is: the vector D, j=1,2,...,n, D[j] =  2 \sum_{i=1}^m ((A\*x-y)_i a_{i,j})

Performance
-----------

Last noted performance:

- solving a recipe probleem of on average 8.5 foods takes 9834889 instructions (= callgrind instruction fetch cost)
