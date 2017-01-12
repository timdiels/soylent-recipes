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

import numpy as np
import logging
import scipy

_logger = logging.getLogger(__name__)

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
    nutrition_target : soylent_recipes.nutrition_target.NormalizedNutritionTarget
        The desired nutrition
    foods : np.array
        The foods to use to achieve the nutrition target. Contains exactly the
        nutrients required by the nutrition target in the exact same order. Rows
        represent foods, columns represent nutrients.
        
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
    amounts, residual = solve_least_squares(foods) # solve relaxed problem
    sub_score = -float(residual)
    return (False, sub_score), amounts  #TODO try linear program as well

def solve_least_squares(foods):
    A = foods.transpose()
    b = np.ones(foods.shape[1])
    return scipy.optimize.nnls(A, b)  # x>=0  #TODO could try a root finder alg instead, if that's faster and similarly accurate

