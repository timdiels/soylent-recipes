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

#TODO make class with nutrition_target in ctor and transform it to the perfect representation for perf here
def solve(nutrition_target, foods):
    '''
    Calculate food amounts to reach the nutrition target
    
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
    score : float
        Score of recipe. Never NaN. Higher score is better.
    amounts : np.array(float)
        The amounts of each food to use to optimally achieve the nutrition
        target. ``amounts[i]`` is the amount of the i-th food to use.
    '''
    nutrition_target = nutrition_target.values
    transposed_foods = foods.transpose()
    A = np.vstack((-transposed_foods, transposed_foods))
    b = np.concatenate((-nutrition_target[:,0], nutrition_target[:,1]))
    mask = ~np.isnan(b)
    A = A[mask]
    b = b[mask]
    A = np.hstack([A, np.eye(len(b), len(b))])
    amounts, residual = scipy.optimize.nnls(A, b)
    return -residual, amounts[:len(foods)]
