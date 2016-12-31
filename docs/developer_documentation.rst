Developer documentation
=======================

Documentation for developers/contributors of Soylent Recipes.

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

Clustering
^^^^^^^^^^
Trying all combinations is infeasible, so first we group similar foods
together. We pick a food per cluster to represent the cluster. Combinations of
representatives are then tried. At a later stage, representatives can be
swapped with other members of the cluster for fine tuning. We use hierarchical
clustering so we can start out coarse with a low maximum of representatives and
as then break up clusters into their children, increasing the max on
representatives for fine tuning.

Distance between food is approximately proportial to the score difference of
swapping one food with another in a recipe. As such, the design is such that:

- Food quantities are ignored. E.g. If 1 unit of `food1` offers exactly as much
  nutrition (all nutrient values equal) as 10 units of `food2`, their distance
  is 0.

- Nutrient values are interpreted relative to the nutrition target:

  - If nutrient has a min and max constraint: ``/= avg(min, max)``
  - If nutrient has only a min: ``/= min``
  - If nutrient has only a max: ``/= max``
  
  E.g. if `nutrient1` has a pseudo target of 1 and `nutrient2` has a pseudo
  target of 10, a difference of 1 in `nutrient1` will count 10 times as much as
  a difference of 1 in `nutrient2`

Formally, the distance function is defined as::

    Finally, nutrient differences are combined using squared euclidean
    distance.

    TODO point to source code instead
    TODO latex, d(f_1, f_2, t) = f_{1,i}...

f_1, f_2: food1 and food2, as vectors of nutrient values
t := nutrition target TODO prolly split into M=maxima, m=minima?

For the clustering algorithm itself:

- hierarchical: agglomerative (bottom-up), linkage criteria: maximum
- leaf := a food, branch := a cluster, tree := leaf or branch, root tree := a
  tree not currently part of a tree
- Start with each food as a leaf
- Combine the 2 root trees with the least distance to each other into a new branch
- distance between 2 trees is the max distance between any leaf of the first
  and any leaf of the second tree. Distance between 2 leafs is `d` as defined
  above.

This way each cluster has an associated max distance, which can be used as a
level of detail knob.

Doc TODO
--------
TopRecipes pops by descending max_distance. I.e. we continue with the least
refined. Though this does reduce pruning, increasing how much of the search
space we cover; i.e. it's more expensive. In the future, we might choose to pop
highest score instead and restart search with a random set of cluster nodes to
counter greediness. In either case, we simply prune lowest score first.

Scoring
^^^^^^^
There are 2 ways in which recipes are scored. First there is partial
score, which is the negative error to a least squares problem based on the
nutrition target; this is a (perhaps biased) approximation of the real problem.
For the real problem, the diet problem, we use a quadratic program; returning
the negative of the objective it tries to minimize. It constrains nutrient sums
to be in range of the extrema.

NutritionTarget
^^^^^^^^^^^^^^^
See soylent_recipes.nutrition_target.NutritionTarget

Design choice:
NutritionTarget min cannot be 0. This way it is nan if there is no min
constraint. min=0 would not actually constrain the nutrient as negative
values are impossible due to already requiring positive amounts of foods.

Pseudo targets
^^^^^^^^^^^^^^
When solving the relaxed problem with least squares, extrema are converted to
pseudo targets as distance to a target is all that least squares understands.

When has no min, but does have a max, pseudo=0.5*max. Placing it at min would punish
values close to the max far too harshly. Placing it at max would punish
values at zero far too harshly and punish exceeding the max far too lightly.
Putting it in the middle, punishes being at min or max equally. One could
consider 0.3*max. Question is which makes the best estimator for simply being
in the range [0, max].

When no max, but has non-zero min -> pseudo-target=1.1*min.
Placing the target at min would punish falling short of min far too lightly.
1.1*min assigns more error to falling short of min, at the cost of
overshooting the min. A reasonable approximation. Other than that the choice
of 1.1 is fairly arbitrary. E.g. would 1.2 be better or what about 1.05?

Remember that a nutrient has either a max or a min constraint, or both.

When has min and max -> pseudo-target= (min+max)/2

The solver is least squares. Squares because we want a deviation twice as large
to count more than twice as much.  This ensures that a difference to
pseudo-target of [0.1 0.9] is rated far worse than [0.5 0.5], while in
manhattan distance, these would get an equal 'rating'.

Normalising nutrients
^^^^^^^^^^^^^^^^^^^^^
When nutrient1 and nutrient2 have a pseudo-target of 1 and 10 respectively, a
difference in nutrient1 of 1 should be equivalent to a difference of 10 in
nutrient2 when scoring nutrient error to target or when calculating distance
between foods for clustering the foods. To achieve this, we normalise the foods
and nutrition target by dividing by the pseudo-target of the nutrient.

Clustering
^^^^^^^^^^
We would like a clustering which clusters foods which offer similar output in
recipes. I.e. the distance function should assign lower distance to foods which
provide a similar nutrient output when swapped in a recipe. This distance
function should ignore differences due to scale. E.g. food1 [1, 2] and food2
[2,4] are equivalent as one is a multiple of the other. It matters that there
is twice as much of the second nutrient as there is of the former in the food.
It matters not that food2 has twice as much of each nutrient as food1. After
all, in a recipe, we can simply take twice as much of food1 as we would of
food2 and the result would be the same.

In a recipe being solved, deviations will be judged by Euclidean distance. So
we will use a form of Euclidean distance for the clustering as well.

The chosen distance metric is then: relative Euclidean distance (RED)::

    d(a,b) = ||a/||a||_2, b/||b||_2 ||_2

By first normalising foods a, b to size 1; the metric will give more emphasis
to proportion rather than size.

Further, we want to use a hierarchical clustering. This allows our search
algorithm to start with low detail (the center of clusters closer to the root)
and then split clusters to increase detail. By splitting, we mean to replace a
cluster by its children. Agglomerative clustering is used, resulting in a
binary tree of clusters with foods as leafs.
