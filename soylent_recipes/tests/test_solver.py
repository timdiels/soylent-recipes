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
from soylent_recipes import nutrition_target as nutrition_target_, main
from .various import NutritionTarget
import pandas as pd
import numpy as np
from functools import partial
import pytest

assert_allclose = partial(np.testing.assert_allclose, atol=1e-8)

def _score(nutrition_target, nutrition_):
    # l2 norm of error to the extrema. Error is the amount it falls
    # short of a min constraint, or the amount it exceeds a max
    # constraint.
    #
    # solve should use this score
    error = np.concatenate([
        np.clip(nutrition_target['min'] - nutrition_, 0.0, np.inf),
        np.clip(nutrition_ - nutrition_target['max'], 0.0, np.inf)
    ])
    return -np.linalg.norm(error)
        
def nutrition(amounts, foods):
    return pd.Series(amounts, index=foods.index, name='amount').dot(foods)
    
@pytest.fixture
def solve(): #TODO inline
    def solve(nutrition_target, foods):
        return solver.solve(nutrition_target, foods.values)
    return solve

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
    foods, nutrition_target = main.normalize(foods, nutrition_target)
    score, amounts = solve(nutrition_target, foods)
    nutrition_ = nutrition(amounts, foods)
    nutrition_target_.assert_satisfied(nutrition_target, nutrition_)
    assert np.isclose(score, 0.0)  # perfect match
        
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
    foods, nutrition_target = main.normalize(foods, nutrition_target)
    score, amounts = solve(nutrition_target, foods)
    nutrition_ = nutrition(amounts, foods)
    nutrition_target_.assert_satisfied(nutrition_target, nutrition_)
    assert np.isclose(score, 0.0)  # perfect match
    
def test_minmax_overlap(solve):
    '''
    When target has min and max, with some foods sharing nutrients, do fine
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
    foods, nutrition_target = main.normalize(foods, nutrition_target)
    score, amounts = solve(nutrition_target, foods)
    nutrition_ = nutrition(amounts, foods)
    nutrition_target_.assert_satisfied(nutrition_target, nutrition_)
    assert np.isclose(score, 0.0)  # perfect match
            
def test_approximate(solve):
    '''
    When pseudo target cannot be met perfectly, least squares score is correct
    and amounts are optimal
    '''
    nutrients = ['nutrient1', 'nutrient2']
    nutrition_target = NutritionTarget(
        [
            [2, 4],  # pseudo target = 3
            [3, 5],  # pseudo target = 4
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
    foods, nutrition_target = main.normalize(foods, nutrition_target)
    score, amounts = solve(nutrition_target, foods)
    
    # Assert score
    expected = _score(nutrition_target, nutrition(amounts, foods))
    assert np.isclose(score, expected)
    
    # Assert the latter food is unused, as it is less optimal than the former
    assert np.isclose(amounts[1], 0.0)
    
    # Check the amount is positive
    assert amounts[0] > 0.0
      
    # Assert amounts is (locally) optimal
    amounts_ = amounts.copy()
    scores = []
    step = 1e-6
    for sign in (1.0, -1.0):
        for _ in range(10):
            amounts_[0] += step * sign
            scores.append(_score(nutrition_target, nutrition(amounts_, foods)))
    assert score > min(scores) # if this fails, increase `step`
    max_score = max(scores)
    assert score > max_score or np.isclose(score, max_score)
