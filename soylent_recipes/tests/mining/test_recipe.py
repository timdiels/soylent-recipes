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
Test soylent_recipes.mining.recipe
'''

from soylent_recipes.mining.recipe import Recipe
from soylent_recipes.tests.various import NutritionTarget
from soylent_recipes import solver
from functools import partial
import numpy as np
import pytest

@pytest.fixture
def nutrition_target():
    return NutritionTarget([], [])
    
def patch_solve(mocker, score=-1.0, amounts=None):
    '''
    Patch solver.solve to return mock value instead of actually solving
    '''
    mocker.patch.object(solver, 'solve', lambda *args: (score, amounts))

assert_allclose = partial(np.testing.assert_allclose, atol=1e-8)
    
def test_solved(mocker, nutrition_target):
    '''
    Test solved recipe
    '''
    # Later we check these or combined and passed to `solve`
    foods_ = np.array(
        [
            [0.2, 1.3],
            [2.2, 0.0],
            [1337, 22.0],  # added this unused one to test food_indices are used correctly
            [0.1, 4.0],
        ]
    )
    expected_foods = np.array(
        [
            [2.2, 0.0],
            [0.1, 4.0],
            [0.2, 1.3],
        ],
    )
    
    # Mock `solve`
    score = 0.0
    amounts = np.array([2.0, 1.1, 3.0])
    def solve(nutrition_target_, foods):
        # Correct args passed in
        assert nutrition_target_.equals(nutrition_target)
        np.testing.assert_allclose(foods, expected_foods)  # Note: column order does not matter
        
        # Return mock values 
        return (score, amounts)
    mocker.patch.object(solver, 'solve', solve)
    
    # Create and assert
    food_indices = np.array([1,3,0])
    recipe = Recipe(food_indices, nutrition_target, foods_)
    assert recipe.score == score  # matches return of `solve`
    assert_allclose(recipe.amounts, amounts)  # matches return of `solve`
    assert recipe.solved  # score close to 0 == recipe.solved
    np.testing.assert_array_equal(recipe.food_indices, food_indices)
    assert len(recipe) == len(food_indices)
    
def test_not_solved(mocker, nutrition_target):
    '''
    Test things specific to an unsolved recipe
    '''
    score = -2.0
    patch_solve(mocker, score)
    food_indices = np.array([0])
    foods = np.ones((1,1))
    recipe = Recipe(food_indices, nutrition_target, foods)
    assert not recipe.solved  # score not close to 0 => not recipe.solved
