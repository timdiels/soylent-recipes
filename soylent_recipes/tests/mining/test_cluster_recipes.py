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
Test soylent_recipes.mining.cluster_recipe
'''

from soylent_recipes.mining.cluster_recipe import ClusterRecipes, TopClusterRecipes
from soylent_recipes.cluster import Leaf, Branch
from soylent_recipes.tests.various import NutritionTarget
from soylent_recipes.tests import mocks
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
    return -1.0

def patch_solve(mocker, score=-1.0, amounts=None):
    '''
    Patch solver.solve to return mock value instead of actually solving
    '''
    mocker.patch.object(solver, 'solve', lambda *args: (score, amounts))

assert_allclose = partial(np.testing.assert_allclose, atol=1e-8)
    
class TestClusterRecipe(object):
    
    '''
    Test ClusterRecipe and ClusterRecipes.create
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
        score = 0.0
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
        recipe = ClusterRecipes(nutrition_target, foods_).create(clusters)
        assert recipe.score == score  # matches return of `solve`
        assert_allclose(recipe.amounts, amounts)  # matches return of `solve`
        assert recipe.solved  # score close to 0 == recipe.solved
        assert not recipe.is_leaf  # some clusters are branches => not is_leaf
        assert recipe.clusters == tuple(clusters)
        assert len(recipe) == len(clusters)
        assert recipe.next_cluster == clusters[1]  # cluster with max max_distance
        assert recipe.max_distance == 4.5  # next_cluster.max_distance
        
    def test_not_solved(self, mocker, nutrition_target):
        '''
        Test things specific to the `not recipe.solved` case
        '''
        score = -2.0
        patch_solve(mocker, score)
        node = Leaf(id_=1, food_index=0)
        foods = np.ones((1,1))
        recipe = ClusterRecipes(nutrition_target, foods).create([node])
        assert not recipe.solved  # score not close to 0 => not recipe.solved
        
    def test_leaf(self, mocker, nutrition_target, score):
        '''
        Test things specific to the `recipe.is_leaf` case
        '''
        patch_solve(mocker)
        node = Leaf(id_=1, food_index=0)
        foods = np.ones((1,1))
        recipe = ClusterRecipes(nutrition_target, foods).create([node])
        assert recipe.is_leaf  # all clusters are leafs => is_leaf
        assert recipe.max_distance == 0.0
        with pytest.raises(InvalidOperationError):
            recipe.next_cluster
        
class TestClusterRecipes(object):
    
    # Note trivial case of create() has already been tested above
    
    def test_create_visited(self, mocker, nutrition_target):
        '''
        When creating recipe with same set of clusters, return None
        '''
        patch_solve(mocker)
        nodes = [Leaf(id_=i, food_index=i) for i in range(2)]
        foods = np.ones((len(nodes),1))
        recipes = ClusterRecipes(nutrition_target, foods)
        
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
        recipes = ClusterRecipes(nutrition_target, foods)
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
        
        assert solve.call_count == 8  # number of successful ClusterRecipe creations (don't forget about the first recipe)
        
class TestTopClusterRecipes(object):
    
    @pytest.fixture
    def top_recipes(self):
        return TopClusterRecipes(max_leafs=100, max_branches=100)  # high enough k such that pruning does not kick in
    
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
        leaf = mocks.ClusterRecipe(score=3)
        branch = mocks.ClusterRecipe(is_leaf=False, score=2)
        leaf2 = mocks.ClusterRecipe(score=1)
        top_recipes.push(branch)
        top_recipes.push(leaf)
        top_recipes.push(leaf2)
        assert list(top_recipes) == [leaf, branch, leaf2]
        
    def test_pushed(self, top_recipes):
        # When constructed, not pushed
        assert not top_recipes.pushed
        
        # When pushed, pushed
        top_recipes.push(mocks.ClusterRecipe())
        assert top_recipes.pushed
        
        # When unset, no longer pushed
        top_recipes.unset_pushed()
        assert not top_recipes.pushed
        
        # When pushed again, pushed
        top_recipes.push(mocks.ClusterRecipe())
        assert top_recipes.pushed

    def test_pop_branches(self, top_recipes):
        def Branch():
            return mocks.ClusterRecipe(is_leaf=False)
        # When constructed, nothing to pop
        assert list(top_recipes.pop_branches()) == []
        
        # When push branch, it's returned in pop
        branch = Branch()
        top_recipes.push(branch)
        assert list(top_recipes.pop_branches()) == [branch]
        
        # When push branch while iterating, it's returned as well
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
        leaf = mocks.ClusterRecipe(is_leaf=True)
        top_recipes.push(leaf)
        top_recipes.push(branch)
        assert list(top_recipes.pop_branches()) == [branch]
        
    def test_pop_branches_order(self, top_recipes):
        '''
        Pop by descending max_distance
        '''
        recipe1 = mocks.ClusterRecipe(is_leaf=False, max_distance=30.0, score=6.0)
        recipe2 = mocks.ClusterRecipe(is_leaf=False, max_distance=20.0, score=3.0)
        recipe3 = mocks.ClusterRecipe(is_leaf=False, max_distance=10.0, score=4.0)
        
        # Push in one order and check
        top_recipes.push(recipe3)
        top_recipes.push(recipe2)
        top_recipes.push(recipe1)
        assert list(top_recipes.pop_branches()) == [recipe1, recipe2, recipe3]
        
    @pytest.mark.parametrize('is_leaf', (False, True))
    def test_push_more_than_k(self, is_leaf):
        '''
        When pushing more than max_branches branches, prune
        
        The analog holds for leafs.
        '''
        kwargs = dict(
            max_leafs=4,
            max_branches=4,
        )
        if is_leaf:
            kwargs['max_leafs'] = 2
        else:
            kwargs['max_branches'] = 2
        top_recipes = TopClusterRecipes(**kwargs)
        def recipe(max_distance, sub_score, is_leaf):
            return mocks.ClusterRecipe(is_leaf=is_leaf, max_distance=max_distance, score=sub_score)
        
        # When k recipes have better score, prune recipe
        recipe5_10 = recipe(max_distance=5.0, sub_score=10.0, is_leaf=is_leaf)
        recipe5_9 = recipe(max_distance=5.0, sub_score=9.0, is_leaf=is_leaf)
        recipe5_8 = recipe(max_distance=5.0, sub_score=8.0, is_leaf=is_leaf)
        top_recipes.push(recipe5_10)
        top_recipes.push(recipe5_8)
        top_recipes.push(recipe5_9)
        assert set(top_recipes) == {recipe5_10, recipe5_9}
        
        # Order in which we push does not matter
        top_recipes.push(recipe5_8)
        assert set(top_recipes) == {recipe5_10, recipe5_9}
        
        # Pushing in between prunes fine too (and max_distance does not matter)
        recipe4_9h = recipe(max_distance=4.0, sub_score=9.5, is_leaf=is_leaf)
        top_recipes.push(recipe4_9h)
        assert set(top_recipes) == {recipe5_10, recipe4_9h}
        
        # Check the other kind of recipe used the other maximum set, i.e. 4
        original = len(top_recipes)
        for _ in range(5):
            top_recipes.push(recipe(1.0, 1.0, not is_leaf))
        added = len(top_recipes) - original
        assert added == 4  # 4 got added, 1 got pruned
