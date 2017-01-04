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
import pytest
from math import sqrt

assert_allclose = partial(np.testing.assert_allclose, atol=1e-8)

lsq = solver._solve_least_squares
lp = solver._solve_linear_program

#TODO not testing _solve_linear_program at the moment as we're temporarily not
#using it, and it's broken because wrong interpretation of A,x params to lp
@pytest.mark.parametrize('solve', (lsq,))# lp))
class TestBoth(object):
    
    def test_minima(self, solve):
        '''
        When target has minima, adhere to them
        '''
        nutrition_target = NutritionTarget(
            minima={
                'nutrient1': 5.0,
                'nutrient2': 2.0,
            },
            maxima={},
            minimize={},
        )
        foods = pd.DataFrame(
            [
                [2.0, 0.0],
                [0.0, 4.0],
            ],
            columns=['nutrient1', 'nutrient2']
        )
        _, amounts = solve(nutrition_target, foods)
        nutrition_target.assert_recipe_matches(amounts, foods)
        
    def test_maxima(self, solve):
        '''
        When target has maxima, adhere to them
        '''
        nutrition_target = NutritionTarget(
            minima={},
            maxima={
                'nutrient1': 5.0,
                'nutrient2': 2.0,
            },
            minimize={},
        )
        foods = pd.DataFrame(
            [
                [2.0, 0.0],
                [0.0, 4.0],
            ],
            columns=['nutrient1', 'nutrient2']
        )
        _, amounts = solve(nutrition_target, foods)
        nutrition_target.assert_recipe_matches(amounts, foods)
        
    def test_minmax_overlap(self, solve):
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
            minimize={},
        )
        foods = pd.DataFrame(
            [
                [3.0, 0.0],  # unlike previous tests, these values are asymmetric
                [2.0, 4.0],
            ],
            columns=['nutrient1', 'nutrient2']
        )
        _, amounts = solve(nutrition_target, foods)
        nutrition_target.assert_recipe_matches(amounts, foods)
        
    def test_minimize(self, solve):
        '''
        Minimize according to target.minimize
        '''
        nutrition_target = NutritionTarget(
            minima={
                'nutrient1': 5.0,
                'nutrient2': 2.0,
                'nutrient3': 0.0,
                'nutrient4': 0.0,
            },
            maxima={},
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
        _, amounts = solve(nutrition_target, foods)
        nutrition_target.assert_recipe_matches(amounts, foods)
        assert_allclose(amounts[1:3], [0, 0])
        
    def test_minimize_weighted(self, solve):
        '''
        Take into account weights when minimizing
        
        Take into account food[nutrient]*amount, not plain food[nutrient].
        '''
        if solve == lp:
            nutrition_target = NutritionTarget(
                minima={
                    'nutrient1': 3.0,
                    'nutrient2': 0.0,  # Note: each nutrient needs to appear in at least one constraint
                    'nutrient3': 0.0,
                },
                maxima={},
                minimize={'nutrient2': 1, 'nutrient3': 2},
            )
        else:
            assert solve == lsq
            nutrition_target = NutritionTarget(
                minima={
                    'nutrient1': 3.0  # Note: lsq relaxes the problem by converting minima/maxima to targets
                },
                maxima={},
                minimize={'nutrient2': 1, 'nutrient3': 2},
            )
        foods = pd.DataFrame(
            [
                [0.1, 0.1, 0.0],  # .1 checks that amount*food[nutrient] is taken into account instead of just food[nutrient]
                [1.0, 0.0, 1.0],  # could satisfy nutrient1 with this, but nutrient3 has higher penalty, so this should have 0 amount 
            ],
            columns=['nutrient1', 'nutrient2', 'nutrient3']
        )
        
        score, amounts = solve(nutrition_target, foods)
        
        if solve == lp:
            nutrition_target.assert_recipe_matches(amounts, foods)
        else:
            # manually confirmed these to be optimal
            assert_allclose(amounts, [18.0,   0.9])
            
            # manually confirmed correct weights are used. I.e. 3 for min-max(,
            # 2 for targets) and 1/normalised_weight for minimize (where
            # normalised weights sum to 1)
            assert np.isclose(score, -1.3416407864998738)
            
    def test_weights(self, solve):
        '''
        Test correct weights are given to error in extrema and minimize
        
        Weights:
        
        - extrema: 2 (for lp, simply ignore this line; extrema not part of score)
        - minimize: weights normalised such that they sum to 1
        '''
        if solve == lp:
            assert False #TODO
        else:
            nutrition_target = NutritionTarget(
                minima={'nutrient1': 2.0},
                maxima={},
                minimize={'nutrient2': 4.0},
            )
            foods = pd.DataFrame(
                [[1.0, 3.0]],
                columns=['nutrient1', 'nutrient2']
            )
            
            score, amounts = lsq(nutrition_target, foods)
            
            # The score is the negative of the residual, since the optimal cannot be
            # achieved, we need only assert the score to confirm correct weights
            # were chosen.
            assert np.isclose(score, -2.5584085962673253)  # Manually calculated the score
            
            # Also check amounts due to paranoia
            assert_allclose(amounts, [0.36363636])  # Manually checked the amounts are optimal

def test_pseudo_targets():
    '''
    Test lsq converts minima/maxima to pseudo-targets correctly
    
    Rules:
    
    - if min and max: pseudo target = (min+max)/2.0
    - if only min: pseudo target = min
    - if only max: pseudo target = max
    
    Note: Pseudo targets are an lsq only thing.
    '''
    nutrition_target = NutritionTarget(
        minima={
            'nutrient1': 3.0,
            'nutrient2': 1.0,
        },
        maxima={
            'nutrient1': 5.0,
            'nutrient3': 2.0,
        },
        minimize={},
    )
    foods = pd.DataFrame(
        [[1.0, 2.0, 3.0]],
        columns=['nutrient1', 'nutrient2', 'nutrient3']
    )
    
    score, amounts = lsq(nutrition_target, foods)
    
    # The score is the negative of the residual, since the optimal cannot be
    # achieved, we need only assert the score to confirm correct pseudo-targets
    # were chosen.
    assert np.isclose(score, -4.6291004988627575)  # Manually calculated the score
    
    # Also check amounts due to paranoia
    assert_allclose(amounts, [0.85714286])  # Manually checked the amounts are optimal
    
    