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

Finding the amounts
^^^^^^^^^^^^^^^^^^^
TODO the readme.md also docs an older version of this.

Having combined foods, we need to figure out the right amount to use of each
to satisfy the nutrition target. This is a relaxed form of what's called the
diet problem, which additionally requires that the cost (e.g. price) is
minimized. While the diet problem requires linear programming to be solved,
here we all we need is bounded least squares (which is faster than solving a
linear program).

With `x`, real vector >=0, the amounts of each food, the unknown we want to
solve for. With `A`, matrix, with A_ij is the amount of nutrient_i in (1g of)
food_j. `m`, vector>=0, minima (nan replaced by 0) of the nutrition target m_i
is minimum of nutrient_i to have. `M`, maxima. M>m.

We want to solve x for: Ax>=m and Ax<=M. A least squares problem is of the form
Ax=b. We can rewrite the former into the latter by first noting that:

    Ax>=m <=> -Ax<=-m
    =>
    solving Ax>=m and Ax<=M
    <=>
    solving [-A;A] x <= [-m;M]

we rewrite this as:

    D=[-A;A]
    b=[-m;M]
    solve Dx<=b

and finally:

    Dx<=b
    <=>
    Dx + z = b,  z>=0,vector of length b
    <=>
    [D,I] [x;z] = b

So our least squares problem is:

    [[-A;A], I] [x;z] = [-m;M]

The nutrition target is achieved iff the least squares residual is (close to)
0. In this case, the residual is the L2 norm of the vector of shortages to
minima and excesses to maxima.

.. TODO rewrite matrices: M_{n,m}(R) is proper notation of a real matrix
.. TODO also rewrite vectors

Terminology
^^^^^^^^^^^
In the context of this project, search or mining refers to finding food
combinations whereas solving refers to finding the right amount of each food
when already given a combination of foods. A combination of foods, with amounts
and score is called a Recipe.

Solver history
^^^^^^^^^^^^^^
Things tried before realising the full problem could be written as least
squares. This is when we still believed we needed a clever search algorithm
to find good recipes, i.e. unsolved recipes needed to give a score proportional
(or rather resulting in the same ordering; TODO ask what it's called;
proportional is too strict) to the distance to a valid solution, i.e. the
distance of the closest point Ax to the hyperrectangle corresponding to the
nutrition target.

- least squares

  Solved Ax=b with b being averages of the min/max of the nutrition target.
  Thus it solves an approximate (biased) problem.

  Sometimes can bound x. Can bound the result via the Ax<=b <=> Ax+z=b, z>=0
  trick. Possibly requires x>=0

  Some allow passing in an initial x, which hints it's an iterative algorithm
  (I did not check the source). At first glance, all listed algorithms
  converge, so the initial x must be for improving performance (less
  iterations when making a good guess). Would have been especially useful
  with search that incrementally builds the recipe by adding/replacing foods 1
  or a couple at a time.

  - scipy.optimize.nnls

    solves a whopping 3767 recipes per second (measured over 11s)
    initial x: cannot provide
    x>=0
    residual when impossible: L2 norm to target

  - scipy.optimize.least_squares

    initial x: can provide
    x: bounds of choice
    residual when impossible: ?

  - scipy.optimize.lsq_linear

    initial x: can provide
    x: bounds of choice
    residual when impossible: ?

  - scipy.optimize.leastsq

    initial x: can provide
    x: bounds of choice
    residual when impossible: ?

- linear program

  They have a linear objective to minimize (or mazimize), solve Ax=b, and
  constrain to Bx <= u.

  When given just inequalities, they will return either `x` or raise
  'Infeasible' and return some other things that were of no use to us.

  - scipy.optimize.linprog

    initial x: cannot provide
    result: bounds of choice
    x: bounds of choice

  - cvxopt.solvers.lp:

    initial x: can provide
    result: bounds of choice
    x: bounds of choice

    Quite advanced, has a couple of options to exploit the structure of our
    problem (which is quite specific).

- solve system of inequalities:

  - sympy (symbolic):

    - Matrix.gauss_jordan_solve, LUsolve:

      When used to solve Ax<=M, Ax>=m via Ax=b. The idea was to symbolically
      solve with b = symbols('b1 ...'), then subs b for m and M to get a vector
      of minima and maxima. This does not work as A could be singular leading
      to row_i = b_i or b_j, for which most methods raise "No solution".

      Would have had to write a modified version to make it work. Would have
      used a modified version of a numeric LU decomposition then as numeric is
      faster to compute than symbolic; and LU decomposition generally
      introduces less numerical error than Gauss Jordan.

    - linsolve

      is just a wrapper around Matrix.gauss_jordan_solve

    - reduce_inequalities:

      Only supports univariate inequalities.

