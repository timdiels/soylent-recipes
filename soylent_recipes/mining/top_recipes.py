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

import pandas as pd
from textwrap import dedent
from itertools import chain
from soylent_recipes.mining.top_k import TopK

class TopRecipes(object):
    
    '''
    List of top recipes
    
    Keeps k branches, k leafs. When exceeding k branches/leafs, drops the lowest
    scoring branch/leaf respectively.
    '''
    
    def __init__(self, max_leafs, max_branches):
        self._key = lambda recipe: recipe.score
        self._pushed = False
        self._leafs = TopK(max_leafs, self._key)
        self._branches = TopK(max_branches, self._key)
        
        # Note: pruning will be unused so long as k>=max_branches, given how we use this
        self._branches_by_max_distance = TopK(max_branches, lambda recipe: -recipe.max_distance) 
    
    def __iter__(self):
        '''
        Yield top recipes, ordered by descending score
        '''
        return iter(sorted(chain(self._leafs, self._branches), reverse=True, key=self._key))
    
    def pop_branches(self):
        '''
        Yield all branch recipes sorted by descending max_distance
        
        Manipulating/accessing the TopK object while iterating is
        supported/safe. Any branch recipes pushed while iterating will be
        yielded.
        
        Yields
        ------
        Recipe
        '''
        while self._branches:
            recipe = self._branches_by_max_distance.pop()
            self._branches.remove(recipe)
            assert len(self._branches) == len(self._branches_by_max_distance), '{} == {}'.format(len(self._branches), len(self._branches_by_max_distance))
            yield recipe
        
    def unset_pushed(self):
        self._pushed = False
        
    def push(self, recipe):
        if recipe is None:
            raise ValueError("recipe is None. It shouldn't.")
        
        #
        if recipe.is_leaf:
            recipes = self._leafs
        else:
            recipes = self._branches
        popped = recipes.push(recipe)
        pushed = popped != recipe
        if pushed:
            self._pushed = True
            if not recipe.is_leaf:
                if popped is not None:
                    self._branches_by_max_distance.remove(popped)
                self._branches_by_max_distance.push(recipe)
        assert len(self._branches) == len(self._branches_by_max_distance), '{} == {}'.format(len(self._branches), len(self._branches_by_max_distance))
        
    @property
    def pushed(self):
        '''
        Whether a recipe has been pushed since the last call to `unset_pushed`
        (or since construction)
        '''
        return self._pushed
    
    def format_stats(self):
        recipes = list(self._leafs) + list(self._branches)
        max_distances = pd.Series(recipe.max_distance for recipe in recipes)
        return (
            dedent('''\
                Solved: {solved}/{total}
                Counts grouped by max_distance:
                {max_distances} 
            ''')
            .format(
                solved=sum(recipe.solved for recipe in recipes),
                total=len(recipes),
                max_distances='\n'.join('{:.2f}: {}'.format(max_distance, count) for max_distance, count in max_distances.value_counts().sort_index().items())
            )
        )
        
    def __len__(self):
        '''
        Number of recipes (leaf or branch) in top
        '''
        return len(self._leafs) + len(self._branches)