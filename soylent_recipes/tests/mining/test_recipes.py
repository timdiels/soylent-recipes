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
Test soylent_recipes.mining.recipes
'''

from soylent_recipes.mining.recipes import Recipes
from soylent_recipes.cluster import Leaf, Branch
from soylent_recipes.tests.various import NutritionTarget
from chicken_turtle_util.exceptions import InvalidOperationError
from soylent_recipes import solver
from functools import partial
import numpy as np
import pytest

@pytest.fixture
def nutrition_target():
    return NutritionTarget([], [])
    
@pytest.fixture
def score():
    return (False, 0.0)

def patch_solve(mocker, score=(False, 0.0), amounts=None):
    '''
    Patch solver.solve to return mock value instead of actually solving
    '''
    mocker.patch.object(solver, 'solve', lambda *args: (score, amounts))

assert_allclose = partial(np.testing.assert_allclose, atol=1e-8)
    
class TestRecipe(object):
    
    '''
    Test Recipe and Recipes.create
    '''
    
    def test_branch(self, mocker, nutrition_target):
        '''
        Test everything on a branch recipe
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
        score = (True, 2.5)
        amounts = np.array([2.0, 1.1, 3.0])
        def solve(nutrition_target_, foods):
            # Correct args passed in
            assert nutrition_target_.equals(nutrition_target)
            np.testing.assert_allclose(foods, expected_foods)  # Note: column order does not matter
            
            # Return mock values 
            return (score, amounts)
        mocker.patch.object(solver, 'solve', solve)
        
        #
        leaf3 = Leaf(3, food_index=1)
        leaf4 = Leaf(4, food_index=-1)  # index set to -1 to trigger KeyError if it were to be used. leaf4 is not supposed to be used
        leaf5 = Leaf(5, food_index=3)
        leaf6 = Leaf(4, food_index=-1)
        clusters = [
            Branch(id_=0, max_distance=3.0, leaf_node=leaf3, children=(leaf3,leaf4)),
            Branch(id_=1, max_distance=4.5, leaf_node=leaf5, children=(leaf5,leaf6)),
            Leaf(id_=2, food_index=0),
        ]
        
        # Create and assert
        recipe = Recipes(nutrition_target, foods_).create(clusters)
        assert recipe.score == score  # matches return of `solve`
        assert_allclose(recipe.amounts, amounts)  # matches return of `solve`
        assert recipe.solved  # score[0] == recipe.solved
        assert not recipe.is_leaf  # some clusters are branches => not is_leaf
        assert recipe.clusters == tuple(clusters)
        assert len(recipe) == len(clusters)
        assert recipe.next_cluster == clusters[1]  # cluster with max max_distance
        assert recipe.max_distance == 4.5  # next_cluster.max_distance
        
    def test_not_solved(self, mocker, nutrition_target):
        '''
        Test things specific to the `not recipe.solved` case
        '''
        score = (False, 2.0)
        patch_solve(mocker, score)
        node = Leaf(id_=1, food_index=0)
        foods = np.ones((1,1))
        recipe = Recipes(nutrition_target, foods).create([node])
        assert not recipe.solved  # score[0] == recipe.solved
        
    def test_leaf(self, mocker, nutrition_target, score):
        '''
        Test things specific to the `recipe.is_leaf` case
        '''
        patch_solve(mocker)
        node = Leaf(id_=1, food_index=0)
        foods = np.ones((1,1))
        recipe = Recipes(nutrition_target, foods).create([node])
        assert recipe.is_leaf  # all clusters are leafs => is_leaf
        assert recipe.max_distance == 0.0
        with pytest.raises(InvalidOperationError):
            recipe.next_cluster
        
class TestRecipes(object):
    
    # Note trivial case of create() has already been tested above
    
    def test_create_visited(self, mocker, nutrition_target):
        '''
        When creating recipe with same set of clusters, return None
        '''
        patch_solve(mocker)
        nodes = [Leaf(id_=i, food_index=i) for i in range(2)]
        foods = np.ones((len(nodes),1))
        recipes = Recipes(nutrition_target, foods)
        
        # First time, return recipe
        assert recipes.create([nodes[0], nodes[1]]) is not None
        
        # Seen clusters before, return None
        assert recipes.create([nodes[0], nodes[1]]) is None
        
        # Order of clusters does not matter, return None
        assert recipes.create([nodes[1], nodes[0]]) is None
    
    def test_replace(self, mocker, nutrition_target):
        solve = mocker.Mock(return_value=(score, None))
        mocker.patch.object(solver, 'solve', solve)
        nodes = [Leaf(id_=i, food_index=i) for i in range(4)]
        foods = np.ones((4,1))
        recipes = Recipes(nutrition_target, foods)
        recipe = recipes.create([nodes[0]])
        
        # When replacee == replacement, raise
        with pytest.raises(ValueError):
            recipes.replace(recipe, [nodes[0]], [nodes[0]])
            
        # When replacee empty, raise
        with pytest.raises(ValueError):
            recipes.replace(recipe, [], [nodes[1]])
            
        # When replacee missing, raise
        with pytest.raises(Exception):
            recipes.replace(recipe, [nodes[1]], [nodes[2]])
        with pytest.raises(Exception):
            recipes.replace(recipe, [nodes[0], nodes[1]], [nodes[2]])
            
        # When replacee and replacement overlap in any other way, raise
        with pytest.raises(ValueError):
            recipes.replace(recipe, [nodes[0]], [nodes[1], nodes[0]])
            
        # When replace with one, all good
        recipe = recipes.replace(recipe, [nodes[0]], [nodes[1]])
        assert set(recipe.clusters) == {nodes[1]}
        
        # When replace with multiple, all good
        recipe = recipes.replace(recipe, [nodes[1]], [nodes[0], nodes[2]])
        assert set(recipe.clusters) == {nodes[0], nodes[2]}
        
        # When replace multiple with multiple, all good
        recipe = recipes.replace(recipe, [nodes[0], nodes[2]], [nodes[1], nodes[3]])
        assert set(recipe.clusters) == {nodes[1], nodes[3]}
        
        # When replace multiple with one, all good
        recipe = recipes.replace(recipe, [nodes[1], nodes[3]], [nodes[2]])
        assert set(recipe.clusters) == {nodes[2]}
        
        # When replace with none, leaving behind some, all good
        recipe = recipes.replace(recipe, [nodes[2]], [nodes[0], nodes[1], nodes[3]])
        recipe = recipes.replace(recipe, [nodes[3]], [])
        assert set(recipe.clusters) == {nodes[0], nodes[1]}
        
        # When replace some, but not all, all good
        recipe = recipes.replace(recipe, [nodes[0]], [nodes[2], nodes[3]])
        assert set(recipe.clusters) == {nodes[1], nodes[2], nodes[3]}
        
        assert solve.call_count == 8  # number of successful Recipe creations (don't forget about the first recipe)