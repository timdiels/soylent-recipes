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

def lsq(nutrition_target, foods):
    amounts, residual = solver.solve_least_squares(foods)
    return -float(residual), amounts

def nutrition(amounts, foods):
    return pd.Series(amounts, index=foods.index, name='amount').dot(foods)
    
def lsq_score(nutrition_target, nutrition_):
    # score is negative of the l2-norm to the pseudo target
    return -np.sqrt(((nutrition_ - 1)**2).sum())

class TestBoth(object):
    
    @pytest.fixture
    def solve(self): #TODO inline, rm class, ...
        def solve(nutrition_target, foods):
            score, amounts = solver.solve(nutrition_target, foods.values)
            return score[1], amounts
        return solve
    
    def test_minima(self, solve):
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
            
    def test_maxima(self, solve):
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
        
    def test_minmax_overlap(self, solve):
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
            
def test_lsq_approximate():
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
    score, amounts = lsq(nutrition_target, foods)
    nutrition_ = nutrition(amounts, foods)
    
    # Assert score is calculated correctly
    expected = lsq_score(nutrition_target, nutrition_)
    assert np.isclose(score, expected)
    
    # Assert the latter food is unused, as it is less optimal than the former
    assert np.isclose(amounts[1], 0.0)
    
    # Double-check amount is positive
    assert amounts[0] > 0.0
      
    # Assert amounts is (locally) optimal
    amounts_ = amounts.copy()
    scores = []
    step = 1e-6
    for sign in (1.0, -1.0):
        for _ in range(10):
            amounts_[0] += step * sign
            scores.append(lsq_score(nutrition_target, nutrition(amounts_, foods)))
    assert score > min(scores) # if this fails, increase `step`
    max_score = max(scores)
    assert score > max_score or np.isclose(score, max_score)
