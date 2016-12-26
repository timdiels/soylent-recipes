# This file is part of Soylent Recipes.
# 
# Soylent Recipes is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Soylent Recipes is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Soylent Recipes.  If not, see <http://www.gnu.org/licenses/>.

'''
Diet problem solver
'''

from cvxopt import matrix
import cvxopt
import numpy as np
import logging
import pprint
import pandas as pd
from math import sqrt

_logger = logging.getLogger(__name__)
cvxopt.solvers.options['show_progress'] = False

def solve(nutrition_target, foods):
    '''
    Calculate food amounts to reach nutrition_target
    
    This solves a diet problem: given a list of foods, how much of each food is
    required to optimally satisfy a nutrition target?
    
    Currently, only least squares is used to solve. Because of this the returned
    score[0] is currently always False. In the future, a quadratic program will
    be used to solve it properly with least squares as a fallback for when no
    optimal solution exists to the real problem. Least squares solves a
    relaxed/unconstrained version of the problem.
    
    Parameters
    ----------
    nutrition_target : soylent_recipes.nutrition_target.NutritionTarget
        The desired nutrition
    foods : pd.DataFrame
        The foods to use to achieve the nutrition target
        
    Returns
    -------
    score : (solved :: bool, sub_score :: float)
        Score of recipe. When the linear problem is unsolvable, solved=False and
        sub_score is based on a least squares problem instead. sub_score is
        never NaN.
    amounts : np.array(float)
        The amounts of each food to use to optimally achieve the nutrition
        target. ``amounts[i]`` is the amount of the i-th food to use.
    '''
    sub_score, amounts = _solve_least_squares(nutrition_target, foods) # solve relaxed problem
    return (False, sub_score), amounts  #TODO try linear program as well

def _solve_least_squares(nutrition_target, foods):
    # Convert minima, maxima -> extrema
    extrema = pd.concat(
        [
            pd.Series(nutrition_target.minima, name='min'),
            pd.Series(nutrition_target.maxima, name='max')
        ],
        axis=1
    )
    
    # Convert extrema to pseudo-targets
    pseudo_targets = []
    for nutrient, min_, max_ in extrema.itertuples(name=None):
        assert not (np.isnan(min_) and np.isnan(max_))
        if np.isnan(min_):
            target = max_
        elif np.isnan(max_):
            target = min_
        else:
            target = (min_ + max_) / 2.0
        pseudo_targets.append((nutrient, target))
        
    #
    A = []
    b = []
    
    # pseudo-targets and targets
    targets = (
        (3.0, pseudo_targets),
        (2.0, nutrition_target.targets.items())
    )
    for weight, targets_ in targets:
        for nutrient, target in targets_:
            A.append(sqrt(weight) * foods[nutrient].values)
            b.append(sqrt(weight) * target)
    
    # minimize
    for nutrient, weight in nutrition_target.minimize.items():
        A.append(sqrt(weight) * foods[nutrient].values)
        b.append(0.0)
    
    # solve
    x, residual, _, _ = np.linalg.lstsq(A, b)
    if len(residual) == 0:  # when rank A < number of foods or when len(A) <= number of foods
        # we found a perfect solution (perhaps one of infinite perfect solutions)
        # due to A not sufficiently constraining x (though shouldn't b be taken into account as well?)  
        score = 0.0
    else:
        score = -float(residual)
    return score, x
    
def _solve_linear_program(nutrition_target, foods):
    # TODO it appears that when A, b are given, Ax=b is first solved and only
    # the free variables are varied in conelp. Instead we should add targets to
    # the minimizing part. Further, l1-norm won't work as that isn't linear, but
    # without abs adding targets to the minimize part makes absolutely no sense.
    # What we need to do instead is calculate l2 norm of Ax-b using coneqp (or
    # its simpler variant rather). The example shows how to take an l2-norm
    # using it. It will then minimize that l2-norm as we first expected from
    # conelp. We then still need to squeeze in the regular
    # nutrition_target.minimize; they can be easily added. Just do the same as
    # lsq above, but move the extrema into constraints instead of converting to
    # pseudo targets. Some code can be shared between the two.
    assert False
    
    # Note:
    #
    # - http://cvxopt.org/userguide/coneprog.html#linear-programming
    # - Gx + s = h, s>=0 => Gx <= h
    # - Ax = b
    # - minimize c^T x
    #
    # - size(A) = (p,n)
    #
    # It's roughly equivalent to solving `Ax=b`. Then with whatever free
    # variables are left (i.e. when len(x) > len(A)), it will try to solve `Gx +
    # s = h` while also minimizing `c^T x`. Verified this by leaving no free
    # variables after `Ax=b` and setting 1 simple constraint with G and h; after
    # which is indeed failed to solve.
    #
    # Our x_i: the amount of the i-th food to use in recipe
    
#     print('?', end='', flush=True)
    G = []
    h = []
    c = []
    
    # minima
    for nutrient, minimum in nutrition_target.minima.items():
        G.append(-foods[nutrient])
        h.append(-minimum)
    
    # maxima
    for nutrient, maximum in nutrition_target.maxima.items():
        G.append(foods[nutrient])
        h.append(maximum)

    # targets
    assert not nutrition_target.targets  # because not implemented atm. Need to add to minimize instead
#     for nutrient, value in nutrition_target.targets.items():
#         A.append(foods[nutrient] + [target])
#         A.append(foods[nutrient])
#         b.append(value)
        
    # minimize -> c
    #TODO assert sum of nutrition_target.minimize weights is 1
    for nutrient, weight in nutrition_target.minimize.items():
        c.append(weight * foods[nutrient].values)
        
    # convert to matrices and run
    if not G:
        assert not h
        G = matrix([], (0, len(foods)), 'd')
        h = matrix([], (0, 1), 'd')
    else:
        G = matrix(np.column_stack(G).transpose()) #TODO transpose above
        h = matrix(h)
    
    if not c:
        c = matrix(np.zeros(len(foods)))
    else:
        c = matrix(np.array(c).sum(axis=0))
#     print('G', G)
#     print('h', h)
#     print('c', c)
    
    solution = cvxopt.solvers.lp(c, G, h) #Note: providing primalstart/dualstart might improve performance? Could do so based on previously solved recipe # "exploiting structure" is also a thing that could improve performance
    _logger.debug('Diet problem solution:\n' + pprint.pformat(solution))
    
    # objective:
    # The value of the linear combination corresponding to
    # `nutrition_target.minimize`. Lower is better.
    if solution['status'] == 'optimal': #TODO status == 'unknown' is interesting as well, simply means it terminated before converging (max iterations reached)
        print('.', end='', flush=True)
        return -solution['objective'], np.reshape(solution['x'], len(foods))
    else:
#         print('!', end='', flush=True)
        # no optimal solution
        return np.nan, None
