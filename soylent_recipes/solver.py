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

from cvxopt import matrix, solvers
import numpy as np
import logging
import pprint

_logger = logging.getLogger(__name__)
solvers.options['show_progress'] = False

def solve(nutrition_target, foods):
    '''
    Solve diet problem
    
    The diet problem: given a list of foods, how much of each food is required
    to optimally satisfy a nutrition target?
    
    Parameters
    ----------
    nutrition_target : soylent_recipes.nutrition_target.NutritionTarget
        The desired nutrition
    foods : pd.DataFrame
        The foods to use to achieve the nutrition target
        
    Returns
    -------
    objective : float or None
        The value of the linear combination corresponding to
        `nutrition_target.minimize`. Lower is better. If no
        (optimal) solution found, returns ``None``.
    amounts : np.array(float) or None
        The amounts of each food to use to optimally achieve the nutrition
        target. ``amounts[i]`` is the amount of the i-th food to use. If no
        (optimal) solution found, returns ``None``.
    '''
    # TODO making use of structure would allow better performance
    
    # Note:
    #
    # - http://cvxopt.org/userguide/coneprog.html#linear-programming
    # - Gx + s = h, s>=0 => Gx <= h  # Note: it appears it's actually xG and xA instead of Gx and Ax
    # - Ax = b
    # - minimize c^T x
    #
    # Our x_i: the amount of the i-th food to use in recipe
    
    G = []
    h = []
    A = []
    b = []
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
    for nutrient, value in nutrition_target.targets.items():
        A.append(foods[nutrient])
        b.append(value)
        
    # minimize
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
    
    if A:
        assert b
        A = matrix(np.column_stack(A).transpose())
        b = matrix(b)
    else:
        A = None
        b = None
        
    if not c:
        c = matrix(np.zeros(len(foods)))
    else:
        c = matrix(np.array(c).sum(axis=0))
#     print('g', G)
#     print('h', h)
#     print('A', A)
#     print('b',b)
#     print('c', c)
    
    solution = solvers.lp(c, G, h, A, b)
    _logger.debug('Diet problem solution:\n' + pprint.pformat(solution))
    if solution['status'] == 'optimal': #TODO status == 'unknown' is interesting as well, simply means it terminated before converging (max iterations reached)
        return solution['objective'], np.reshape(solution['x'], len(foods))
    else:
        return None, None
