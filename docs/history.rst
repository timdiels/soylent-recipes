History
=======

Summary of the project's history. This is not intended to be a changelog.

C++ version
-----------
About 3 years ago, I made the first attempt to find soylent recipes. It was
written in C++. It took about 12ms to solve a recipe (in retrospect, this is
very slow). I tried searching by a k-means and a hierarchical clustering (with
alglib). Finally, I tried a genetic algorithm (with the BEAGLE library).
Neither had much success, but this was due to a bug in the recipe scoring
algorithm; e.g. water was considered enough to 'eat' to meet the daily
nutrition target; i.e. all experiments had to be redone.

Nowadays, I know not to rely on output coming from software that has not been
thoroughly tested. More important modules of the software, get more thorough
testing than other modules (e.g. a bug in food sorting in outputted recipes
going undetected, is not a big problem).

Python version
--------------
Instead of continuing, I started over in Python. While you could achieve better
performance in C++, the increase in development time is generally not worth it.

I started by constructing a nutrition target based on the DRI. This nutrition
target consisted of 3 optional parts:

- extrema/bounds: min and max of each nutrient. Binary: in range / out of
  range.
- target: achieve as closely as possible
- minimize: equivalent to target=0, except for it being weighted

Eventually this nutrition target was simplified to just having extrema. Target
and minimize were hardly used and can be sufficiently approximated using
extrema.

Then, I parsed and cleaned the USDA foods data with respect to the nutrition
target; filling in some missing nutrition values with 0 and dropping foods with
too many missing data entirely. The recipe solver does not handle missing data,
so we must fill missing values or drop far too many foods. This left about 6400
of 8000 foods.

For the first recipe solver, I used a linear program (cvxopt.solvers.lp). Despite
testing, I overlooked a misunderstanding of Ax=b, expecting it to solve a least
squares. It will be worthwhile to read a book on optimization algorithms next
time I need one.

Brute force search
------------------
As a baseline, I implemented a trivial brute force search, which tries the
cartesian product: `foods**max_foods` (with `max_foods<10`), a combinatorial
explosion. In retrospect, randomly selecting foods would have made a better
baseline. In the future, I will use such an unbiased probabilistic algorithm as
baseline.

Cluster walk search
-------------------
With brute force not yielding any result (and not knowing that the solver had a
bug), I switched to a more informed search algorithm. This is later called
cluster_walk and eventually removed in favor of simple random search. It
combines foods by crawling a hierarchical clustering top-down. Leaf nodes are
foods. In a recipe, each cluster node is replaced by the food closest to its
center.  The clustering is generated with scikit-learn; it is agglomerative,
the distance metric is euclidean distance and the linkage is complete.

Complete linkage was chosen to have a max distance between foods per cluster.
The search algorithm treats this as the opposite of the level of detail. The
idea is to combine at low levels of detail first, to weed out less promising
combinations, and then increase detail by splitting clusters into their
children.

At each cluster split, when exceeding `max_foods`, one of the clusters of the
recipe is dropped, but each recipe that is (only marginally) better than the
parent recipe (i.e.  before splitting a cluster) is added to a top k recipes
structure (using the heapq library for efficiency). When `k` is exceeded, the
top k pops, in its final version, the lowest scoring recipe. The cluster walk,
at each iteration, pops the least detailed recipe from the top k, splits it and
adds it splits back to the top k.

Note that cluster walk requires a solver which provides scores on partial
solutions (i.e. when nutrition target is not fully satisfied).

While cluster walk very quickly reached a good solution, it only gave a single
solution despite having a top k as they were only k variations of 1 recipe.
This is due to popping the lowest scoring recipe and pushing `max_foods`
variations of the same recipe at each split of a cluster. One possible way
around this is to also take into account similarity to other recipes when
popping when exceeding `k`, such that if 2 recipes are sufficiently similar, pop
the lowest scoring of those 2 recipes.

The final clustering (with normalized foods and RED as distance metric) is
available as a `newick formatted file <clustering newick_>`_ and as a
`rectangular dendrogram in pdf <clustering pdf_>`_ (the latter may take a few
minutes to load). 

Not that the USDA data appears to include a curated clustering (perhaps not
hierarchical), that I could have used to quickly have a first clustering,
before trying to make one more suited for the task at hand (i.e. based on
nutrient values, ignoring scale).

Clustering: distance metric
---------------------------
Euclidean distance is chosen over Manhattan distance as we care more about
larger individual differences than smaller ones. E.g. we consider `target -
actual = [0.1, 0.9]` as far worse than a difference vector of `[0.5, 0.5]`.
Manhattan distance would yield the same distance on each of the former
difference vectors.

The ideal distance metric assigns low distance to foods which behave similarly
in a recipe. Thus differences in scale do not matter as when `food1=z*food2`
(`z>0`) we can simply take `z` amount of `food2` to match `food1` and thus the
distance between these 2 foods should be 0.

To incorporate this, the clustering distance metric was changed to relative
Euclidean distance (RED), which ignores scale.

Later, clustering was entirely removed as the only search algorithm left
(random), does not use it.

Pseudo targets
--------------
At the time, a least squares solver was in use which minimized `foods * amounts
= nutrition_target`. I.e. it did not support extrema and required everything to
be converted to a single target vector called the pseudo-targets.

This conversion went as follows for extrema:

- `min+max/2`, if it has a min and a max
- `max/2`, if it has only a max.
- `1.1*min`, if it has only a min. 
  
The min-only pseudo-target exceeds the min a bit so that least squares does
not undershoot the min as easily, as it does not care whether the difference is
negative or positive.

The max-only psuedo-target does the same thing however the pseudo-target
is set to `0.5 * max` instead of `0.9 * max`, the latter being admittedly
somewhat arbitrary.

Later, as solvers supported proper extrema, pseudo targets were removed;
greatly simplifying things.

Nutrient values normalization
-----------------------------
The clustering and recipe scoring (for solvers that provide a score) was
further improved by normalizing nutrient values to their nutrition target. For
example when `nutrient1` and `nutrient2` have a target of 1 and 10
respectively, a difference of 1 in `nutrient1` should be equivalent to a
difference of `10` in `nutrient2`. To get Euclidean distance (used in both
clustering and recipe scoring) to treat these as equal, we divide nutrient
values by their target (or their pseudo target).

Later, clustering and recipe scoring were removed, and thus nutrient
normalization was removed as well.

Greedy search
-------------
Greedy search starts from a random sample of foods of size `max_foods`. It then
makes a single pass over the foods. At iteration i, it replaces the i-th food
with the food that yields the highest score combined with the other foods in
the recipe. This requires a solver that returns a score (on partial solutions).

Greedy search was later removed as it is outperformed by random search.
Only comparing to foods in the clustering, cut to a certain `max_distance`
(or equivalently, level of detail), might outperform random search.

Random search
-------------
Take a random sample of foods of size `max_foods`, drop unused foods. Do this
until `k` solved recipes have been found.

Recipe solvers
--------------
Recipe solvers in the order we tried them.

With the old more complex nutrition target:

- cvxopt.solvers.lp

  Ax=b used for targets. However instead of first satisfying `extrema`, then
  least squaring the `targets` and finally minimizing `minimize`, this first
  least squared the `targets` and then tried to satisfy `extrema`. This
  resulted in far more infeasible status results than necessary.

- numpy.linalg.lstsq

  Least squares of `foods * amounts = pseudo_targets`. However, `amounts` can be
  negative! Returns the negative of its residue as score.

  Pseudo target derivation contained a bug at this point.

- scipy.optimize.nnls

  Like, numpy.linalg.lstsq, except nnls ensures `amounts>=0`.
  Solves 3767 recipes / s

  Some time after, pseudo targets were fixed and the nutrition target was
  simplified to just extrema.

With the simple nutrition target (just extrema):

- sympy: solve symbolically
  
  - Matrix.gauss_jordan_solve, LUsolve, LUdecomposition, linsolve (a wrapper
    around Matrix.gauss_jordan_solve).
    
    #math (freenode) suggested to treat the extrema as a system of inequalities
    to solve symbolically with Gaussian elimination. 
    
    Rewriting the problem properly as described in the scipy.optimize.nnls
    solution below would work, but solving the problem numerically is faster
    than solving it symbolically. There is no reason to solve it symbolically.

  - reduce_inequalities
  
    Only supports univariate inequalities.
  
- scipy.optimize.nnls

  We realized how to rewrite the real problem as a least squares problem, i.e.
  it solves with extrema in mind and not some pseudo targets (the latter were
  removed after this solver was implemented). This solves at a whopping rate of
  about 1000 recipes / s (after optimizing with profiler). However, amounts are
  floats, not integers, which may be hard to measure properly (e.g. weighing
  1.02g can be tricky)

  Before showing how to rewrite, consider these definitions:

  - `x` (above referred to as `amounts`): real vector >=0, the amounts of each food, the unknown we want to
    solve for.
  - `A` (above referred to as `foods`): matrix, with A_ij = the amount of
    nutrient_i in (1g of) food_j.
  - `m`: vector>=0, minima (nan replaced by 0) of the nutrition target. m_i
    is the minimum of nutrient_i to ahve.
  - `M`: maxima of the nutrition target. M>m.

  and these notations:

  - [A;B]: stack matrices vertically, on top of each other
  - [A,B]: stack matrices horizontally, next to each other

  We want to solve `Ax>=m and Ax<=M`.  A least squares problem is of the form
  `Ax=b`.

  First we combine the minima and maxima. Given that `Ax>=m iff -Ax<=-m`,
  solving `Ax>=m and Ax<=M` is equivalent to solving `[-A;A] x <= [-m;M]`.

  For brevity, we introduce some variables::

      D=[-A;A]
      b=[-m;M]
      solve Dx<=b
      
  Finally, note that `Dx<=b` iff `Dx+z=b, z>=0, z is a vector`. Or as least
  squares `[D,I] [x;z] = b`.

  So our least squares problem is::

      [[-A;A], I] [x;z] = [-m;M]

  The nutrition target is achieved iff the least squares residual is (close to)
  0. In this case, the residual is the L2 norm of the vector of shortages to
  the minima and excesses to the maxima.

- GLPK via ecyglpki wrapper:

  Solve a mixed integer linear program with the GLPK library. Here, we can
  directly supply the extrema to the algorithm without any rewriting. The
  amounts are now constrained to integers. Linear program solvers are slower
  than least squares, and mixed integer linear programs are generally even
  slower, but in the measurement of the previous algorithm we could see we had
  performance to spare. This solver solves at a rate of 298.7 recipes / s.

  While GLPK's KKT.PB check could provide us with a decent score when not able
  to solve the recipe (i.e. nutrition target cannot be satisfied with the given
  foods), the solver now only returns whether it solved or not instead of a
  score. Score was used by greedy and cluster_walk search, which have been
  removed at this point.

  At the time of writing, the ecyglpki wrapper has a memory leak. I've `reported
  this bug <ecyglpki memleak issue_>`_ to ecyglpki.  Its last release is 2-3
  years older than GLPK's.

  Note that we pick 0 as objective function. We do not have any price data on
  our foods to optimize by. Also note that linear program libraries can differ
  quite a bit; for example GLPK offers a `KKT.*` checks, whereas I did not
  immediately find these in cvxopt.

- GLPK via python-glpk

  Did not try this as it also appears to be out of date.

- GLPK via swiglpk wrapper:

  Does not leak memory. Solves 229.6 recipes / s. 
  
  The profiler reveals that 40% of time is wasted on __setitem__ of
  intArray/doubleArray of the swiglpk wrapper, which explains the performance
  loss in switching to this wrapper. Perhaps this could be optimized away using
  Cython, or rather swiglpk should offer an interface by which we can provide a
  numpy array. Still, the current speed may still be acceptable.

.. _ecyglpki memleak issue: https://github.com/equaeghe/ecyglpki/issues/9

