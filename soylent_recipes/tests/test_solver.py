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
Test soylent_recipes.solver
'''

from chicken_turtle_util import data_frame as df_
from soylent_recipes import solver
from soylent_recipes.nutrition_target import NutritionTarget
import pandas as pd
import numpy as np
from functools import partial

assert_allclose = partial(np.testing.assert_allclose, atol=1e-8)

def test_minima():
    '''
    When target has minima, adhere to them
    '''
    nutrition_target = NutritionTarget(
        minima={
            'nutrient1': 5.0,
            'nutrient2': 2.0,
        },
        maxima={},
        targets={},
        minimize={},
    )
    foods = pd.DataFrame(
        [
            [2.0, 0.0],
            [0.0, 4.0],
        ],
        columns=['nutrient1', 'nutrient2']
    )
    amounts = solver.solve(nutrition_target, foods)
    nutrition_target.assert_recipe_matches(amounts, foods)
    
def test_maxima():
    '''
    When target has maxima, adhere to them
    '''
    nutrition_target = NutritionTarget(
        minima={},
        maxima={
            'nutrient1': 5.0,
            'nutrient2': 2.0,
        },
        targets={},
        minimize={},
    )
    foods = pd.DataFrame(
        [
            [2.0, 0.0],
            [0.0, 4.0],
        ],
        columns=['nutrient1', 'nutrient2']
    )
    amounts = solver.solve(nutrition_target, foods)
    nutrition_target.assert_recipe_matches(amounts, foods)
    
def test_minmax_overlap():
    '''
    When target has min and max, with some foods sharing nutrients, do fine
    '''
    nutrition_target = NutritionTarget(
        minima={
            'nutrient1': 2.0,
            'nutrient2': 1.0,
        },
        maxima={
            'nutrient1': 3.0,
            'nutrient2': 2.0,
        },
        targets={},
        minimize={},
    )
    foods = pd.DataFrame(
        [
            [3.0, 0.0],  # unlike previous tests, these values are asymmetric
            [2.0, 4.0],
        ],
        columns=['nutrient1', 'nutrient2']
    )
    amounts = solver.solve(nutrition_target, foods)
    nutrition_target.assert_recipe_matches(amounts, foods)
    
def test_targets():
    '''
    When target has targets, adhere to them
    '''
    nutrition_target = NutritionTarget(
        minima={},
        maxima={},
        targets={
            'nutrient1': 5.0,
            'nutrient2': 2.0,
        },
        minimize={},
    )
    foods = pd.DataFrame(
        [
            [2.0, 0.0],
            [3.0, 4.0],
        ],
        columns=['nutrient1', 'nutrient2']
    )
    amounts = solver.solve(nutrition_target, foods)
    nutrition_target.assert_recipe_matches(amounts, foods)
    
def test_minimize():
    '''
    Minimize according to target.minimize
    '''
    nutrition_target = NutritionTarget(
        minima={
            'nutrient3': 0.0,  # Note: each nutrient needs to appear in at least one constraint
            'nutrient4': 0.0,
        },
        maxima={},
        targets={
            'nutrient1': 5.0,
            'nutrient2': 2.0,
        },
        minimize={'nutrient3': 1, 'nutrient4': 1},
    )
    foods = pd.DataFrame(
        [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 1.0, 0.0], # this
            [1.0, 1.0, 0.0, 1.0], # and this will be avoided due to `minimize`
            [0.0, 1.0, 0.0, 0.0],
        ],
        columns=['nutrient1', 'nutrient2', 'nutrient3', 'nutrient4']
    )
    amounts = solver.solve(nutrition_target, foods)
    nutrition_target.assert_recipe_matches(amounts, foods)
    assert_allclose(amounts[1:3], [0, 0])
    
def test_minimize_weighted():
    '''
    Take into account weights when minimizing
    
    Take into account food[nutrient]*amount, not plain food[nutrient].
    '''
    nutrition_target = NutritionTarget(
        minima={
            'nutrient1': 3.0,
            'nutrient2': 0.0,  # Note: each nutrient needs to appear in at least one constraint
            'nutrient3': 0.0,
        },
        maxima={},
        targets={},
        minimize={'nutrient2': 1, 'nutrient3': 2},
    )
    foods = pd.DataFrame(
        [
            [0.1, 0.1, 0.0],  # .1 checks that amount*food[nutrient] is taken into account instead of just food[nutrient]
            [1.0, 0.0, 1.0],  # could satisfy nutrient1 with this, but nutrient3 has higher penalty, so this should have 0 amount 
        ],
        columns=['nutrient1', 'nutrient2', 'nutrient3']
    )
    amounts = solver.solve(nutrition_target, foods)
    nutrition_target.assert_recipe_matches(amounts, foods)
    assert_allclose(amounts, [30.0, 0.0])
    
def test_minimize_negative_weights():
    '''
    Minimize negative weights too (i.e. maximize)
    '''
    nutrition_target = NutritionTarget(
        minima={
            'nutrient1': 1.0,
        },
        maxima={
            'nutrient2': 5.0,
        },
        targets={},
        minimize={'nutrient1': 1, 'nutrient2': -1},
    )
    foods = pd.DataFrame(
        [
            [1.0, 0.0],
            [0.0, 1.0], 
        ],
        columns=['nutrient1', 'nutrient2']
    )
    amounts = solver.solve(nutrition_target, foods)
    nutrition_target.assert_recipe_matches(amounts, foods)
    assert_allclose(amounts, [1.0, 5.0])
    
# TODO analog for maximize
    