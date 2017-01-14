History
=======

Summary of the project's history, how things evolved. This is not intended to
be a changelog. Events are roughly chronologically.

C++ version
-----------
About 3 years ago, I worked on the C++ version of 

recall 12ms per Recipe to solve. Turned out to be way faster now. But due to
that expected slowness I did not consider full random.

...
---

Tried cvxopt.solvers.lp and scipy.optimize.linprog. Either gives the ideal
solution, or when infeasible, returns no solution at all or trivially
retrievable measure of how far off we are from a solution.

solver changes

cluster_walk
------------

clustering
^^^^^^^^^^
Designed to aid the algorithm.

Outputted the tree with ete3 as a rectangular dendrogram in pdf format (takes a
few minutes to load) and as a newick file.

The NCBI data also includes a clustering, probably curated. Could have simply
used that.

search
^^^^^^
cluster_walk: explain.

removal
^^^^^^^
With the solver being so surprisingly fast, we can simply mine by making
random combinations until we have a solution. The solutions are as diverse as
can be.

cluster_walk removed, obsoleted by random search.  Both cluster_walk and random search
find optimal recipes within reasonable time. While it's faster than random
search, its output is not as diverse as that of random search. Its recipes are
so similar that it essentially returns just 1 recipe; and without any
randomness it will return that same recipe each run.

---

Efficient TopK class by using python's heapq.

---

ecyglpki's last commit was 3 years ago (at time of writing = Jan 2017) while
glpk's last release was 8 months ago. Further, it has a memory leak when using
intopt. Submitted an issue for it here
https://github.com/equaeghe/ecyglpki/issues/9. So I decided to switch to an up
to date binding.

python-glpk also was out of date, so I settled with swiglpk which is up to date
and does not leak in our case.
