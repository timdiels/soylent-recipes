Developer documentation
=======================

Documentation for developers/contributors of Soylent Recipes.

Terminology
-----------
**TODO move this top-level, it's needed/used by everything**
In the context of this project, search or mining refers to finding food
combinations whereas solving refers to finding the right amount of each food
when already given a combination of foods. A combination of foods, with amounts
and score is called a Recipe.


Project decisions
-----------------

Nutrition target
^^^^^^^^^^^^^^^^
We assume the nutrition target is based on DRI. As such non-DRI recommendations
may not fit in the input model we have. This allows for writing an easier
model for linear programming, and easier programming in general. If different
nutrition target modelling is desired, it may be able to add it in (doing it up
front would have been just guess work).

The nutrition target should also be translatable to a linear programming
problem, as that's the solver we use to solve the diet problem.

NutritionTarget
^^^^^^^^^^^^^^^
See soylent_recipes.nutrition_target.NutritionTarget

Design choice:
NutritionTarget min cannot be 0. This way it is nan if there is no min
constraint. min=0 would not actually constrain the nutrient as negative
values are impossible due to already requiring positive amounts of foods.

Finding the amounts
^^^^^^^^^^^^^^^^^^^
TODO the readme.md also docs an older version of this.

Having combined foods, we need to figure out the right amount to use of each
to satisfy the nutrition target. This is a relaxed form of what's called the
diet problem, which additionally requires that the cost (e.g. price) is
minimized. While the diet problem requires linear programming to be solved,
here we all we need is bounded least squares (which is faster than solving a
linear program).

