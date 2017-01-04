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

- Nutrient differences are weighted: (from largest to smallest weight):
  
  - nutrients with a non-zero min and/or max
  - nutrients appearing in minimize

  Not being in range of `[min, max]` leads to a recipe being rejected, making
  these nutrients important to have more weight; such that foods are more
  quickly considered different enough to warrant trying each of them.
  Nutrients appearing in minimize can't cause a food to be rejected; those
  nutrients should be avoided, but we haven't yet determined when they actually
  become harmful (no max).

- Nutrient values are interpreted relative to the nutrition target:

  - If nutrient has a non-zero min and max: ``/= avg(min, max)``
  - If nutrient has only a non-zero min: ``/= min``
  - If nutrient has only a non-zero max: ``/= max``
  - If nutrient only appears in minimize: normalise values to lie in range of
    ``[0, weight]``. (TODO minimize weights should sum to 1 and be >0)
  
  E.g. if `nutrient1` has a pseudo target of 1 and `nutrient2` has a pseudo
  target of 10, a difference of 1 in `nutrient1` will count 10 times as much as
  a difference of 1 in `nutrient2`

Formally, the distance function is defined as::

    Finally, nutrient differences are combined using squared euclidean
    distance.

    TODO point to source code instead
    TODO latex, d(f_1, f_2, t) = f_{1,i}...

f_1, f_2: food1 and food2, as vectors of nutrient values
t := nutrition target TODO prolly split into M=maxima, m=minima, minimize?

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
to be in range of the extrema and minimizes squared amounts of
nutrition_target.minimize. In both problems, weights are added such that
extrema take priority over minimize.

- minimize weights sum to 1
- pseudo targets are given weight 2


