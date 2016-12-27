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
from chicken_turtle_util.exceptions import InvalidOperationError
from soylent_recipes.nutrition_target import NutritionTarget
from soylent_recipes.miner import TopRecipes, Recipe
from soylent_recipes.cluster import Node
from soylent_recipes import solver
from . import mocks
import pytest
import pandas as pd
import numpy as np
from functools import partial

assert_allclose = partial(np.testing.assert_allclose, atol=1e-8)

class TestRecipe(object):
     
    @pytest.fixture
    def nutrition_target(self):
        return NutritionTarget({}, {}, {}, {})
    
    @pytest.fixture
    def score(self):
        return (False, 0.0)
    
    def test_branch(self, mocker, nutrition_target):
        '''
        Test everything on a branch recipe
        '''
        # Later we check these or combined and passed to `solve`
        food0 = pd.Series([0.2, 1.3], index=['nutr0', 'nutr1'], name='food0')
        food1 = pd.Series([2.2, 0.0], index=['nutr0', 'nutr1'], name='food1')
        food2 = pd.Series([0.1, 4.0], index=['nutr0', 'nutr1'], name='food2')
        expected_foods = pd.DataFrame(
            [
                [0.2, 1.3],
                [2.2, 0.0],
                [0.1, 4.0]
            ],
            columns=['nutr0', 'nutr1'],
            index=['food0', 'food1', 'food2']
        )
        
        # Mock `solve`
        score = (True, 2.5)
        amounts = np.array([2.0, 1.1, 3.0])
        def solve(nutrition_target_, foods):
            # Correct args passed in
            assert nutrition_target_ == nutrition_target
            df_.assert_equals(foods, expected_foods, ignore_order={1})
            
            # Return mock values 
            return (score, amounts)
        mocker.patch.object(solver, 'solve', solve)
        
        #
        def leaf(id_):
            return Node(id_, max_distance=0.0, representative=pd.Series([]), children=())
        clusters = [
            Node(id_=0, max_distance=3.0, representative=food0, children=(
                leaf(3),
                leaf(4)
            )),
            Node(id_=1, max_distance=4.5, representative=food1, children=(
                leaf(5),
                leaf(6)
            )),
            Node(id_=2, max_distance=0.0, representative=food2, children=()),
        ]
        
        # Create and assert
        recipe = Recipe(clusters, nutrition_target)
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
        mocker.patch.object(solver, 'solve', lambda *args: (score, None))
        node = Node(id_=1, representative=pd.Series([]), max_distance=0.0, children=())
        recipe = Recipe([node], nutrition_target)
        assert not recipe.solved  # score[0] == recipe.solved
        
    def test_leaf(self, mocker, nutrition_target, score):
        '''
        Test things specific to the `recipe.is_leaf` case
        '''
        mocker.patch.object(solver, 'solve', lambda *args: (score, None))
        node = Node(id_=1, representative=pd.Series([]), max_distance=0.0, children=())
        recipe = Recipe([node], nutrition_target)
        assert recipe.is_leaf  # all clusters are leafs => is_leaf
        assert recipe.max_distance == 0.0
        with pytest.raises(InvalidOperationError):
            recipe.next_cluster

    def test_replace(self, mocker, nutrition_target, score):
        '''
        Test recipe.replace() entirely
        '''
        solve = mocker.Mock(return_value=(score, None))
        mocker.patch.object(solver, 'solve', solve)
        node1 = Node(id_=1, representative=pd.Series([]), max_distance=0.0, children=())
        node2 = Node(id_=2, representative=pd.Series([]), max_distance=0.0, children=())
        node3 = Node(id_=3, representative=pd.Series([]), max_distance=0.0, children=())
        node4 = Node(id_=4, representative=pd.Series([]), max_distance=0.0, children=())
        recipe = Recipe([node1], nutrition_target)
        
        # When replacee == replacement, raise
        with pytest.raises(ValueError):
            recipe.replace([node1], [node1])
            
        # When replacee empty, raise
        with pytest.raises(ValueError):
            recipe.replace([], [node2])
            
        # When replacee missing, raise
        with pytest.raises(Exception):
            recipe.replace([node2], [node3])
        with pytest.raises(Exception):
            recipe.replace([node1, node2], [node3])
            
        # When replacee and replacement overlap in any other way, raise
        with pytest.raises(ValueError):
            recipe.replace([node1], [node2, node1])
            
        # When replace with one, all good
        recipe = recipe.replace([node1], [node2])
        assert set(recipe.clusters) == {node2}
        
        # When replace with multiple, all good
        recipe = recipe.replace([node2], [node1, node3])
        assert set(recipe.clusters) == {node1, node3}
        
        # When replace multiple with multiple, all good
        recipe = recipe.replace([node1, node3], [node2, node4])
        assert set(recipe.clusters) == {node2, node4}
        
        # When replace multiple with one, all good
        recipe = recipe.replace([node2, node4], [node3])
        assert set(recipe.clusters) == {node3}
        
        # When replace with none, leaving behind some, all good
        recipe = recipe.replace([node3], [node1, node2, node4])
        recipe = recipe.replace([node4], [])
        assert set(recipe.clusters) == {node1, node2}
        
        # When replace some, but not all, all good
        recipe = recipe.replace([node1], [node3, node4])
        assert set(recipe.clusters) == {node2, node3, node4}
        
        assert solve.call_count == 8  # number of successful Recipe creations (don't forget about the first recipe)

    def test_lt(self, mocker, nutrition_target):
        '''
        Test < operator
        
        Basically self.score < other.score
        '''
        def _Recipe(score):
            food = pd.Series([])
            node = Node(id_=1, representative=food, max_distance=0.0, children=())
            mocker.patch.object(solver, 'solve', lambda *args: (score, np.array([])))
            return Recipe([node], nutrition_target)
            
        recipe_f8 = _Recipe(score=(False, 8.0))
        recipe_f9 = _Recipe(score=(False, 9.0))
        recipe_t8 = _Recipe(score=(True, 8.0))
        recipe_t9 = _Recipe(score=(True, 9.0))
        
        assert recipe_f8 < recipe_f9
        assert recipe_f8 < recipe_t8
        assert recipe_f8 < recipe_t9
        
        assert not recipe_f9 < recipe_f8
        assert recipe_f9 < recipe_t8
        assert recipe_f9 < recipe_t9
        
        assert not recipe_t8 < recipe_f8
        assert not recipe_t8 < recipe_f9
        assert recipe_t8 < recipe_t9
        
        assert not recipe_t9 < recipe_f8
        assert not recipe_t9 < recipe_f9
        assert not recipe_t9 < recipe_t8
    
class TestTopRecipes(object):
    
    @pytest.fixture
    def top_recipes(self):
        return TopRecipes(k=100)  # high enough k such that pruning does not kick in
    
    def test_pushed(self, top_recipes):
        # When constructed, not pushed
        assert not top_recipes.pushed
        
        # When pushed, pushed
        top_recipes.push(mocks.Recipe())
        assert top_recipes.pushed
        
        # When unset, no longer pushed
        top_recipes.unset_pushed()
        assert not top_recipes.pushed
        
        # When pushed again, pushed
        top_recipes.push(mocks.Recipe())
        assert top_recipes.pushed

    def test_pop(self, top_recipes):
        # When constructed, nothing to pop
        assert list(top_recipes.pop_branches()) == []
        
        # When push branch, it's returned in pop
        branch = mocks.Recipe(is_leaf=False)
        top_recipes.push(branch)
        assert list(top_recipes.pop_branches()) == [branch]
        
        # When push branch while iterating, it's returned as well
        top_recipes.push(branch)
        first = True
        actual = []
        for recipe in top_recipes.pop_branches():
            actual.append(recipe)
            if first:
                top_recipes.push(branch)
                first = False
        assert actual == [branch, branch]
        
        # Only pop branches
        leaf = mocks.Recipe(is_leaf=True)
        top_recipes.push(leaf)
        top_recipes.push(branch)
        assert list(top_recipes.pop_branches()) == [branch]
        
    def test_pop_order(self, top_recipes):
        '''
        Branch recipes are popped according to score ascendingly
        '''
        recipe1 = mocks.Recipe(is_leaf=False, score=(False, 0.0))
        recipe2 = mocks.Recipe(is_leaf=False, score=(False, 3.0))
        recipe3 = mocks.Recipe(is_leaf=False, score=(False, 4.0))
        
        # Push in one order and check
        top_recipes.push(recipe3)
        top_recipes.push(recipe2)
        top_recipes.push(recipe1)
        assert list(top_recipes.pop_branches()) == [recipe1, recipe2, recipe3]

    def test_iter(self, top_recipes):
        assert list(top_recipes) == []
        
        # When iterated, return all recipes sorted descendingly by score
        leaf = mocks.Recipe(score=3)
        branch = mocks.Recipe(is_leaf=False, score=2)
        leaf2 = mocks.Recipe(score=1)
        top_recipes.push(branch)
        top_recipes.push(leaf)
        top_recipes.push(leaf2)
        assert list(top_recipes) == [leaf, branch, leaf2]
        
    def test_push(self):
        '''
        Prune after each push
        
        Prune recipe iff k recipes <= recipe.
        
        Basic push functionality already tested by test_pop
        ''' #TODO there's a separate TopRecipes for leafs and branches, so it can go up to 2K if you mix
        top_recipes = TopRecipes(k=2)
        
        # When k recipes have better score, prune recipe
        recipe5_10 = mocks.Recipe(is_leaf=False, max_distance=5.0, score=(False, 10.0))
        recipe5_9 = mocks.Recipe(is_leaf=False, max_distance=5.0, score=(False, 9.0))
        recipe5_8 = mocks.Recipe(is_leaf=False, max_distance=5.0, score=(False, 8.0))
        top_recipes.push(recipe5_10)
        top_recipes.push(recipe5_8)
        top_recipes.push(recipe5_9)
        assert set(top_recipes) == {recipe5_10, recipe5_9}
        
        # Order in which we push does not matter
        top_recipes.push(recipe5_8)
        assert set(top_recipes) == {recipe5_10, recipe5_9}
        
        # Pushing in between prunes fine too (and max_distance does not matter)
        recipe4_9h = mocks.Recipe(is_leaf=False, max_distance=4, score=(False, 9.5))
        top_recipes.push(recipe4_9h)
        assert set(top_recipes) == {recipe5_10, recipe4_9h}
