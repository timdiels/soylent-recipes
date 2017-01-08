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
Test soylent_recipes.mining.top_recipes
'''

from soylent_recipes.mining.top_recipes import TopRecipes
from soylent_recipes.tests import mocks
import pytest

class TestTopRecipes(object):
    
    @pytest.fixture
    def top_recipes(self):
        return TopRecipes(max_leafs=100, max_branches=100)  # high enough k such that pruning does not kick in
    
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
        leaf = mocks.Recipe(is_leaf=True)
        top_recipes.push(leaf)
        top_recipes.push(branch)
        assert list(top_recipes.pop_branches()) == [branch]
        
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
        top_recipes = TopRecipes(**kwargs)
        def recipe(max_distance, sub_score, is_leaf):
            return mocks.Recipe(is_leaf=is_leaf, max_distance=max_distance, score=(False, sub_score))
        
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
