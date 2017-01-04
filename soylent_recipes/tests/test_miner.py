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
from soylent_recipes.cluster import Leaf, Branch
from soylent_recipes import solver
from . import mocks
import pytest
import pandas as pd
import numpy as np
from functools import partial

assert_allclose = partial(np.testing.assert_allclose, atol=1e-8)

Leaf_ = partial(Leaf, food=pd.Series())

class TestRecipe(object):
     
    @pytest.fixture
    def nutrition_target(self):
        return NutritionTarget({}, {}, {}, {})
    
    @pytest.fixture
    def score(self):
        return (False, 0.0)
    
    def patch_solve(self, mocker, score=(False, 0.0), amounts=None):
        '''
        Patch solver.solve to return mock value instead of actually solving
        '''
        mocker.patch.object(solver, 'solve', lambda *args: (score, amounts))
    
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
        leaf3 = Leaf(3, food0)
        leaf4 = Leaf_(4)
        leaf5 = Leaf(5, food1)
        leaf6 = Leaf_(4)
        clusters = [
            Branch(id_=0, max_distance=3.0, leaf_node=leaf3, children=(leaf3,leaf4)),
            Branch(id_=1, max_distance=4.5, leaf_node=leaf5, children=(leaf5,leaf6)),
            Leaf(id_=2, food=food2),
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
        self.patch_solve(mocker, score)
        node = Leaf(id_=1, food=pd.Series([]))
        recipe = Recipe([node], nutrition_target)
        assert not recipe.solved  # score[0] == recipe.solved
        
    def test_leaf(self, mocker, nutrition_target, score):
        '''
        Test things specific to the `recipe.is_leaf` case
        '''
        self.patch_solve(mocker)
        node = Leaf_(id_=1)
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
        nodes = [Leaf_(id_=i) for i in range(4)]
        recipe = Recipe([nodes[0]], nutrition_target)
        
        # When replacee == replacement, raise
        with pytest.raises(ValueError):
            recipe.replace([nodes[0]], [nodes[0]])
            
        # When replacee empty, raise
        with pytest.raises(ValueError):
            recipe.replace([], [nodes[1]])
            
        # When replacee missing, raise
        with pytest.raises(Exception):
            recipe.replace([nodes[1]], [nodes[2]])
        with pytest.raises(Exception):
            recipe.replace([nodes[0], nodes[1]], [nodes[2]])
            
        # When replacee and replacement overlap in any other way, raise
        with pytest.raises(ValueError):
            recipe.replace([nodes[0]], [nodes[1], nodes[0]])
            
        # When replace with one, all good
        recipe = recipe.replace([nodes[0]], [nodes[1]])
        assert set(recipe.clusters) == {nodes[1]}
        
        # When replace with multiple, all good
        recipe = recipe.replace([nodes[1]], [nodes[0], nodes[2]])
        assert set(recipe.clusters) == {nodes[0], nodes[2]}
        
        # When replace multiple with multiple, all good
        recipe = recipe.replace([nodes[0], nodes[2]], [nodes[1], nodes[3]])
        assert set(recipe.clusters) == {nodes[1], nodes[3]}
        
        # When replace multiple with one, all good
        recipe = recipe.replace([nodes[1], nodes[3]], [nodes[2]])
        assert set(recipe.clusters) == {nodes[2]}
        
        # When replace with none, leaving behind some, all good
        recipe = recipe.replace([nodes[2]], [nodes[0], nodes[1], nodes[3]])
        recipe = recipe.replace([nodes[3]], [])
        assert set(recipe.clusters) == {nodes[0], nodes[1]}
        
        # When replace some, but not all, all good
        recipe = recipe.replace([nodes[0]], [nodes[2], nodes[3]])
        assert set(recipe.clusters) == {nodes[1], nodes[2], nodes[3]}
        
        assert solve.call_count == 8  # number of successful Recipe creations (don't forget about the first recipe)
        
    def test_clusters(self, mocker, nutrition_target):
        # recipe.clusters is sorted by cluster id
        self.patch_solve(mocker)
        node1 = Leaf(id_=1, food=pd.Series([]))
        node2 = Leaf(id_=2, food=pd.Series([]))
        recipe1 = Recipe([node1, node2], nutrition_target)
        recipe2 = Recipe([node2, node1], nutrition_target)
        assert recipe1.clusters == (node1, node2)
        assert recipe2.clusters == (node1, node2)
    
    def test_eq(self, mocker, nutrition_target):
        # recipes are equal iff recipe.clusters equals
        self.patch_solve(mocker)
        nodes = [Leaf_(id_=i) for i in range(3)]
        recipe1 = Recipe([nodes[0], nodes[1]], nutrition_target)
        recipe2 = Recipe([nodes[1], nodes[0]], nutrition_target)
        assert recipe1 == recipe2
        recipe3 = Recipe([nodes[0], nodes[2]], nutrition_target) 
        assert recipe1 != recipe3
        assert recipe2 != recipe3

class TestTopRecipes(object):
    
    @pytest.fixture(autouse=True)
    def set_recipe_eq_by_identity(self, mocker):
        '''
        Patch mock recipes to equal iff identical.
        '''
        mocker.patch.object(mocks.Recipe, '__eq__', lambda s, other: id(s) == id(other))
        
    @pytest.fixture
    def top_recipes(self):
        return TopRecipes(k=100)  # high enough k such that pruning does not kick in
    
    def test_push(self, top_recipes):
        '''
        Test push and iter (not exceeding k)
        '''
        # When created, iter empty
        assert list(top_recipes) == []
        
        # When push None, raise
        with pytest.raises(ValueError):
            top_recipes.push(None)
            
        # When push some, pushed recipes appear in iter, sorted descendingly by score
        leaf = mocks.Recipe(score=3)
        branch = mocks.Recipe(is_leaf=False, score=2)
        leaf2 = mocks.Recipe(score=1)
        top_recipes.push(branch)
        top_recipes.push(leaf)
        top_recipes.push(leaf2)
        assert list(top_recipes) == [leaf, branch, leaf2]
        
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

    def test_pop_branches(self, top_recipes):
        def Branch():
            return mocks.Recipe(is_leaf=False)
        # When constructed, nothing to pop
        assert list(top_recipes.pop_branches()) == []
        
        # When push branch, it's returned in pop
        branch = Branch()
        top_recipes.push(branch)
        assert list(top_recipes.pop_branches()) == [branch]
        
        # When push branch while iterating, it's returned as well
        branch = Branch()
        branch2 = Branch()
        top_recipes.push(branch)
        first = True
        actual = []
        for recipe in top_recipes.pop_branches():
            actual.append(recipe)
            if first:
                top_recipes.push(branch2)
                first = False
        assert actual == [branch, branch2]
        
        # When push leafs and branches, only pop branches
        branch = Branch()
        leaf = mocks.Recipe(is_leaf=True)
        top_recipes.push(leaf)
        top_recipes.push(branch)
        assert list(top_recipes.pop_branches()) == [branch]
        
    def test_push_visited(self, top_recipes):
        '''
        Ignore push of recipe that has been pushed before (=visited)
        '''
        # When pushed recipe in top_recipes, ignore it
        branch = mocks.Recipe(is_leaf=False)
        top_recipes.push(branch)
        top_recipes.push(branch)
        assert set(top_recipes) == {branch}
        
        # When pushed recipe not in top_recipes, but has been pushed before, ignore it
        list(top_recipes.pop_branches())
        top_recipes.push(branch)
        assert list(top_recipes) == []
        
    def test_pop_branches_order(self, top_recipes):
        '''
        Pop by descending max_distance
        '''
        recipe1 = mocks.Recipe(is_leaf=False, max_distance=30.0, score=(False, 6.0))
        recipe2 = mocks.Recipe(is_leaf=False, max_distance=20.0, score=(False, 3.0))
        recipe3 = mocks.Recipe(is_leaf=False, max_distance=10.0, score=(False, 4.0))
        
        # Push in one order and check
        top_recipes.push(recipe3)
        top_recipes.push(recipe2)
        top_recipes.push(recipe1)
        assert list(top_recipes.pop_branches()) == [recipe1, recipe2, recipe3]
        
    @pytest.mark.parametrize('is_leaf', (False, True))
    def test_push_more_than_k(self, is_leaf):
        '''
        When pushing more than k branches, prune
        
        The analog holds for leafs. I.e. the max size of top recipes is 2k = k
        leafs + k branches.
        '''
        top_recipes = TopRecipes(k=2)
        def recipe(max_distance, sub_score):
            return mocks.Recipe(is_leaf=is_leaf, max_distance=max_distance, score=(False, sub_score))
        
        # When k recipes have better score, prune recipe
        recipe5_10 = recipe(max_distance=5.0, sub_score=10.0)
        recipe5_9 = recipe(max_distance=5.0, sub_score=9.0)
        recipe5_8 = recipe(max_distance=5.0, sub_score=8.0)
        top_recipes.push(recipe5_10)
        top_recipes.push(recipe5_8)
        top_recipes.push(recipe5_9)
        assert set(top_recipes) == {recipe5_10, recipe5_9}
        
        # Order in which we push does not matter
        recipe5_8 = recipe(max_distance=5.0, sub_score=8.0)
        top_recipes.push(recipe5_8)
        assert set(top_recipes) == {recipe5_10, recipe5_9}
        
        # Pushing in between prunes fine too (and max_distance does not matter)
        recipe4_9h = recipe(max_distance=4.0, sub_score=9.5)
        top_recipes.push(recipe4_9h)
        assert set(top_recipes) == {recipe5_10, recipe4_9h}
