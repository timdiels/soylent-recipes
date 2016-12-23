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
from soylent_recipes.miner import TopK, Recipe
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
        score = 2.5
        amounts = np.array([2.0, 1.1, 3.0])
        def solve(nutrition_target_, foods):
            # Correct args passed in
            assert nutrition_target_ == nutrition_target
            df_.assert_equals(foods, expected_foods, ignore_order={1})
            
            # Return mock values 
            return (score, amounts)
        mocker.patch.object(solver, 'solve', solve)
        
        #
        clusters = [
            Node(id_=0, max_distance=3.0, representative=food0, children=(
                Node(id_=3, max_distance=0.5, representative=pd.Series([]), children=()),
                Node(id_=4, max_distance=0.2, representative=pd.Series([]), children=()),
            )),
            Node(id_=1, max_distance=4.5, representative=food1, children=(
                Node(id_=5, max_distance=2.0, representative=pd.Series([]), children=()),
                Node(id_=6, max_distance=1.0, representative=pd.Series([]), children=()),
            )),
            Node(id_=2, max_distance=0.0, representative=food2, children=()),
        ]
        
        # Create and assert
        recipe = Recipe(clusters, nutrition_target)
        assert recipe.score == score  # matches return of `solve`
        assert_allclose(recipe.amounts, amounts)  # matches return of `solve`
        assert recipe.solved  # score not NaN => solved
        assert not recipe.is_leaf  # some clusters are branches => not is_leaf
        assert recipe.clusters == tuple(clusters)
        assert len(recipe) == len(clusters)
        assert recipe.next_cluster == clusters[1]  # cluster with max max_distance
        assert recipe.max_distance == 4.5  # next_cluster.max_distance
        
        # next_max_distance: worst recipe.max_distance after next cluster split
        # First case: split clusters less max distance than a cluster in recipe.clusters
        assert recipe.next_max_distance == 3.0
        
        # Now the other case: split clusters larger max distance than all clusters in recipe.clusters
        clusters[2] = (
            Node(id_=2, max_distance=7.0, representative=food2, children=(
                Node(id_=7, max_distance=6.0, representative=pd.Series([]), children=()),
                Node(id_=8, max_distance=5.0, representative=pd.Series([]), children=()),
            ))
        )
        recipe = Recipe(clusters, nutrition_target)
        assert recipe.next_max_distance == 6.0
        
    def test_not_solved(self, mocker, nutrition_target):
        '''
        Test things specific to the `not recipe.solved` case
        '''
        score = np.nan
        mocker.patch.object(solver, 'solve', lambda *args: (score, None))
        node = Node(id_=1, representative=pd.Series([]), max_distance=0.0, children=())
        recipe = Recipe([node], nutrition_target)
        assert not recipe.solved  # score is nan => not solved
        with pytest.raises(InvalidOperationError):
            recipe.amounts
        
    def test_leaf(self, mocker, nutrition_target):
        '''
        Test things specific to the `recipe.is_leaf` case
        '''
        mocker.patch.object(solver, 'solve', lambda *args: (np.nan, None))
        node = Node(id_=1, representative=pd.Series([]), max_distance=0.0, children=())
        recipe = Recipe([node], nutrition_target)
        assert recipe.is_leaf  # all clusters are leafs => is_leaf
        assert recipe.max_distance == 0.0
        with pytest.raises(InvalidOperationError):
            recipe.next_cluster
        with pytest.raises(InvalidOperationError):
            recipe.next_max_distance

    def test_replace(self, mocker, nutrition_target):
        '''
        Test recipe.replace() entirely
        '''
        solve = mocker.Mock(return_value=(np.nan, None))
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

    def test_le(self, mocker, nutrition_target):
        '''
        Test <= operator
        '''
        def _Recipe(max_distance, score):
            food = pd.Series([])
            node = Node(id_=1, representative=food, max_distance=max_distance, children=())
            mocker.patch.object(solver, 'solve', lambda *args: (score, np.array([])))
            return Recipe([node], nutrition_target)
            
        recipe5_10 = _Recipe(max_distance=5.0, score=10.0)
        recipe5_9 = _Recipe(max_distance=5.0, score=9.0)
        recipe5_8 = _Recipe(max_distance=5.0, score=8.0)
        recipe4_9 = _Recipe(max_distance=4.0, score=9.0)
        assert recipe5_10 <= recipe5_10  # compared to self
        assert not (recipe5_10 <= recipe5_9)  # compared to lower score, same max_distance
        assert recipe5_9 <= recipe5_10  # compared to higher score, same max_distance
        assert recipe4_9 <= recipe5_9  # compared to same score, higher max_distance
        assert not (recipe5_9 <= recipe4_9)  # compared to same score, lower max_distance
        assert recipe4_9 <= recipe5_10  # compared to higher score, higher max_distance
        assert not (recipe5_10 <= recipe4_9)  # compared to lower score, lower max_distance
        assert not (recipe4_9 <= recipe5_8)  # compared to lower score, higher max_distance
        assert not (recipe5_8 <= recipe4_9)  # compared to higher score, lower max_distance
    
class TestTopK(object):
    
    @pytest.fixture
    def top_k(self):
        return TopK(k=100)  # high enough k such that pruning does not kick in
    
    def test_pushed(self, top_k):
        # When constructed, not pushed
        assert not top_k.pushed
        
        # When pushed, pushed
        top_k.push(mocks.Recipe())
        assert top_k.pushed
        
        # When unset, no longer pushed
        top_k.unset_pushed()
        assert not top_k.pushed
        
        # When pushed again, pushed
        top_k.push(mocks.Recipe())
        assert top_k.pushed

    def test_pop(self, top_k):
        # When constructed, nothing to pop
        assert list(top_k.pop_branches()) == []
        
        # When push branch, it's returned in pop
        branch = mocks.Recipe(is_leaf=False)
        top_k.push(branch)
        assert list(top_k.pop_branches()) == [branch]
        
        # When push branch while iterating, it's returned as well
        top_k.push(branch)
        first = True
        actual = []
        for recipe in top_k.pop_branches():
            actual.append(recipe)
            if first:
                top_k.push(branch)
                first = False
        assert actual == [branch, branch]
        
        # Only pop branches
        leaf = mocks.Recipe(is_leaf=True)
        top_k.push(leaf)
        top_k.push(branch)
        assert list(top_k.pop_branches()) == [branch]
        
    def test_pop_order(self, top_k):
        '''
        Branch recipes are popped according to (next_max_distance, score) descendingly
        '''
        recipe1 = mocks.Recipe(is_leaf=False, next_max_distance=10.0, score=0.0)
        recipe2 = mocks.Recipe(is_leaf=False, next_max_distance=5.0, score=5.0)
        recipe3 = mocks.Recipe(is_leaf=False, next_max_distance=5.0, score=4.0)
        
        # Push in one order and check
        top_k.push(recipe3)
        top_k.push(recipe2)
        top_k.push(recipe1)
        print(list(top_k))
        assert list(top_k.pop_branches()) == [recipe1, recipe2, recipe3]
        
        # Push in another order and check
        top_k.push(recipe2)
        top_k.push(recipe1)
        top_k.push(recipe3)
        assert list(top_k.pop_branches()) == [recipe1, recipe2, recipe3]

    def test_iter(self, top_k):
        assert list(top_k) == []
        
        # When iterated, return all recipes sorted descendingly by score
        leaf = mocks.Recipe(score=3)
        branch = mocks.Recipe(is_leaf=False, score=2)
        leaf2 = mocks.Recipe(score=1)
        top_k.push(branch)
        top_k.push(leaf)
        top_k.push(leaf2)
        assert list(top_k) == [leaf, branch, leaf2]
        
    def test_push(self):
        '''
        Prune after each push
        
        Prune recipe iff k recipes <= recipe. recipe1 <= recipe2 iff recipe1 is
        at least as detailed as recipe2, yet has an equal or worse score.
        
        Basic push functionality already tested by test_pop
        '''
        top_k = TopK(k=2)
        
        # When k recipes of the same max_distance have better score, prune recipe
        recipe5_10 = mocks.Recipe(is_leaf=False, max_distance=5.0, score=10.0)
        recipe5_9 = mocks.Recipe(is_leaf=False, max_distance=5.0, score=9.0)
        recipe5_8 = mocks.Recipe(is_leaf=False, max_distance=5.0, score=8.0)
        top_k.push(recipe5_10)
        top_k.push(recipe5_8)
        top_k.push(recipe5_9)
        assert set(top_k) == {recipe5_10, recipe5_9}
        
        # Order in which we push does not matter
        top_k.push(recipe5_8)
        assert set(top_k) == {recipe5_10, recipe5_9}
        
        # When pushing one with less max_distance but a score <= to the other 2,
        # gets pruned
        recipe4_9 = mocks.Recipe(is_leaf=False, max_distance=4.0, score=9.0) 
        top_k.push(recipe4_9)
        assert set(top_k) == {recipe5_10, recipe5_9}
        
        # When pushing with more max_distance and a score <= to only 5_10,
        # 5_9 gets pruned
        recipe6_10 = mocks.Recipe(is_leaf=False, max_distance=6.0, score=10.0)
        top_k.push(recipe6_10)
        assert set(top_k) == {recipe6_10, recipe5_10}
        
        # When pushing with more max_distance and a worse score than any other,
        # nothing gets pruned
        recipe7_8 = mocks.Recipe(is_leaf=False, max_distance=7.0, score=8.0)
        top_k.push(recipe7_8)
        assert set(top_k) == {recipe7_8, recipe6_10, recipe5_10}
        
        # When pushing with less max_distance and a better score than any other,
        # nothing gets pruned
        recipe4_11 = mocks.Recipe(is_leaf=False, max_distance=4.0, score=11.0)
        top_k.push(recipe4_11)
        assert set(top_k) == {recipe7_8, recipe6_10, recipe5_10, recipe4_11}
        
        # Pushing in between in a way that causes no pruning
        recipe4h_11 = mocks.Recipe(is_leaf=False, max_distance=4.5, score=11.0)
        top_k.push(recipe4h_11)
        assert set(top_k) == {recipe7_8, recipe6_10, recipe5_10, recipe4h_11, recipe4_11}
        
        # Pushing in between in a way that causes multiple pruning
        recipe5h_12 = mocks.Recipe(is_leaf=False, max_distance=5.5, score=12.0)
        top_k.push(recipe5h_12)
        assert set(top_k) == {recipe7_8, recipe6_10, recipe5h_12, recipe4h_11}
        
        # Pushing something better below still works
        recipe4_12 = mocks.Recipe(is_leaf=False, max_distance=4, score=12.0)
        top_k.push(recipe4_12)
        assert set(top_k) == {recipe7_8, recipe6_10, recipe5h_12, recipe4h_11, recipe4_12}
