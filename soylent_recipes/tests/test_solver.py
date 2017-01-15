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
from soylent_recipes import nutrition_target as nutrition_target_
from .various import NutritionTarget
import pandas as pd
import numpy as np
from functools import partial
import pytest

assert_allclose = partial(np.testing.assert_allclose, atol=1e-8)

def nutrition(amounts, foods):
    return pd.Series(amounts, index=foods.index, name='amount').dot(foods)
    
@pytest.fixture
def solve(): #TODO inline
    def solve(nutrition_target, foods):
        return solver.solve(nutrition_target, foods.values)
    return solve

def assert_all_integer(x):
    np.testing.assert_array_equal(x, np.floor(x))

def test_minima(solve):
    '''
    When target has minima, adhere to them
    '''
    nutrition_target = NutritionTarget(
        [
            [5, np.nan],
            [2, np.nan],
        ],
        index=['nutrient1', 'nutrient2']
    )
    foods = pd.DataFrame(
        [
            [2.0, 0.0],
            [0.0, 4.0],
        ],
        columns=['nutrient1', 'nutrient2']
    )
    amounts = solve(nutrition_target, foods)
    assert_all_integer(amounts)
    nutrition_ = nutrition(amounts, foods)
    nutrition_target_.assert_satisfied(nutrition_target, nutrition_)
        
def test_maxima(solve):
    '''
    When target has maxima, adhere to them
    '''
    nutrition_target = NutritionTarget(
        [
            [np.nan, 5],
            [np.nan, 2],
        ],
        index=['nutrient1', 'nutrient2']
    )
    foods = pd.DataFrame(
        [
            [2.0, 0.0],
            [0.0, 4.0],
        ],
        columns=['nutrient1', 'nutrient2']
    )
    amounts = solve(nutrition_target, foods)
    assert_all_integer(amounts)
    nutrition_ = nutrition(amounts, foods)
    nutrition_target_.assert_satisfied(nutrition_target, nutrition_)
    
def test_minmax_overlap(solve):
    '''
    When target has min and max, with some foods sharing nutrients, do fine
    '''
    nutrition_target = NutritionTarget(
        [
            [20, 30],
            [10, 20],
        ],
        index=['nutrient1', 'nutrient2']
    )
    foods = pd.DataFrame(
        [
            [3.0, 0.0],  # unlike previous tests, these values are asymmetric
            [2.0, 4.0],
        ],
        columns=['nutrient1', 'nutrient2']
    )
    amounts = solve(nutrition_target, foods)
    assert_all_integer(amounts)
    nutrition_ = nutrition(amounts, foods)
    nutrition_target_.assert_satisfied(nutrition_target, nutrition_)
    
def test_infeasible(solve):
    '''
    When target cannot be met perfectly, even with floats, simply return None
    '''
    nutrients = ['nutrient1', 'nutrient2']
    nutrition_target = NutritionTarget(
        [
            [2, 4],
            [3, 5],
        ],
        index=nutrients
    )
    foods = pd.DataFrame(
        [
            [3.0, 2.0],
            [3.0, 1.0],
        ],
        columns=nutrients
    )
    assert solve(nutrition_target, foods) is None
    
def test_infeasible_ints(solve):
    '''
    When target could be met with floats, but not with ints, return None
    '''
    nutrition_target = NutritionTarget(
        [
            [2, 3],
            [1, 2],
        ],
        index=['nutrient1', 'nutrient2']
    )
    foods = pd.DataFrame(
        [
            [3.0, 0.0],  # unlike previous tests, these values are asymmetric
            [2.0, 4.0],
        ],
        columns=['nutrient1', 'nutrient2']
    )
    assert solve(nutrition_target, foods) is None
