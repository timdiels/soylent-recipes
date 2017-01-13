# soylent-recipes

Mines a food database for food combinations that match the nutrient
profile in the database. Current implementation leads to results that match the
target profile by 75%.

Currently it uses the USDA database, but you could fill it up with other food
data as well.

If you already know which foods you want to use for your soylent recipe but
simply want to know the amounts to take of each, use this
[diet problem applet] [http://www.neos-guide.org/content/dietproblem-demo].

## Usage

Packages to install with package manager: suitesparse

- git clone https://github.com/timdiels/soylent-recipes.git
- pip install .
- Download food data from https://www.ars.usda.gov/northeast-area/beltsville-md/beltsville-human-nutrition-research-center/nutrient-data-laboratory/docs/usda-national-nutrient-database-for-standard-reference/
- Put it in data/usda_nutrient_db_sr28 (i.e. that directory contains files like NUTR_DEF.txt)
- Run `soylent`

## Status

Having another go, this time using Python for faster development. The C++ implementation contained a bug in its recipe scoring function (due to lack of testing), as such previous results should be ignored (e.g. it considered a diet of pure water to match the nutritional profile quite well).

# Old

## Table of Contents

* [Approach to solving the problem](#approach-to-solving-the-problem)
* [Results](#results)
* [System requirements](#system-requirements)
* [Compilation](#compilation)
* [Project history](#project-history)

## Approach to solving the problem

The problem is: finding combos of foods that make for good (soylent) recipes,
regardless of taste.

Solving a single combo of foods is simple enough as explained in [Recipe/Diet
Problem](#recipe-diet-problem).

The mining phase entails choosing combinations of foods. Simply enumerating all
possible combinations would take years. After other attempts we've settled with
a genetic algorithm.

Note: we could use subspace clustering, after which we may be
able to use this clustering to aid in making good food combinations.


###  Recipe/Diet Problem

First some more detailed definitions of this subproblem.

Let a recipe problem be: given a set of foods, and a nutrition profile, find
the amounts to optimally satisfy the nutrition profile. (This is more commonly known as a
[Diet Problem](http://www.neos-guide.org/content/diet-problem))

Each food has m properties/nutrients of an ingredient (the contained amount of magnesium, carbs, ...).

Construct a matrix A with: A_{i,j} = the amount of the i-th property of the j-th food.

With n foods, there are amounts X_1, ..., X_n to find.

The nutrient profile provides us with Y_i and M_i for each nutrient. Y_i is the desired amount of nutrient i, M_i is the max allowed amount of nutrient i.

This leads to
- m equations, j=1,2,...m: X_1 A_{1,j} + ... + X_n A_{n,j} = Y_i. 
- m inequalities, j=1,2,...m: X_1 A_{1,j} + ... + X_n A_{n,j} <= M_i. 

Which is a constrained least squares problem.

The algorithm used to solve this is an [active-set algorithm](http://www.alglib.net/optimization/boundandlinearlyconstrained.php#header1).

The function f to mimimize is: \lnorm A\*x - y \rnorm_2

The gradient of f(x) is: the vector D, j=1,2,...,n, D[j] =  2 \sum_{i=1}^m ((A\*x-y)_i a_{i,j})

Last noted performance of solving a recipe in this project of on average 8.5 foods was 9834889 instructions (= callgrind instruction fetch cost)


## Results

Current results are mostly hilarious due to its total disregard for taste.

Obtaining the results isn't a very user friendly experience, but if you're up to it:

1. Run the miner with ./run.sh. It may take 45 minutes to compute.
2. The results are written to population.obm. Search that file for HallOfFame
   entries, as those are the best combinations the algorithm found.

Note: These combinations don't yet list the amount you need of each food in the
combo to satisfy the diet problem.


## Project history

Note: k-means and hierarchical clustering performed poorly on this data because
this data is highly dimensional (about 36 dimensions). 

Our previous attempts of combining foods used (ordered from newest to older):

- Cluster the data and then use the average of each cluster as if they were
  food in our naive miner which does enumerate all possibilities of up to a
  given size (e.g.  up to 5 foods in a single combo).

  Clustering algorithms used were: [these](http://www.alglib.net/dataanalysis/clustering.php),
  and an ad-hoc method which turned out to be pretty bad.

