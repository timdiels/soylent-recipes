User guide
==========
This guide introduces concepts and shows how to mine recipes on your own
machine.

Concepts, background
--------------------
Each iteration, the miner randomly picks `max_foods` from the food database.
Then it applies a solver to find the amounts to use of each food. If the recipe
satisfies the nutrition target, the recipe is outputted to `recipes.txt`.

As food database, the USDA food database is used. Generally, food databases
mostly contain foods with generic names (as opposed to brand names); these
generic foods are usually the average of measurements of a similar food from a
couple of brands.  The food database contains no price data, so returned
recipes are not optimized for being cheap.

The solver returns food amounts as integers (it solves an integer linear
program with GLPK library).  Amounts are expressed in grams, I assumed 1g to be
the granularity at which one can still accurately use a weighing scale to cook
the recipe.

Requirements
------------
Soylent Recipes has been tested on Linux with Python 3.5. It is expected to
work on Python>=3.4. It probably works on Mac and may work on Windows too.

Installation and usage
----------------------
- Download and unpack https://github.com/timdiels/soylent-recipes/archive/master.zip
- cd into the unpacked directory: cd soylent-recipes-master
- Configure it to match your needs (you can skip this if you want to use the
  defaults):

  `max_foods`, `max_recipes` (number of solved recipes to output) and the
  nutrition target can be configured by editing `soylent_recipes/config.py`.

- Run ``pip3 install -e .``. If this conflicts with your installed packages, do
  it in a virtual environment instead
- Run ``soylent --usda-data data/usda_nutrient_db_sr28`` to run the miner.
- The output is in `recipes.txt`. Windows users may need to use notepad++ to
  view it.
