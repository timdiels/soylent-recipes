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

import logging
from soylent_recipes import solver
import numpy as np
import pandas as pd
from textwrap import dedent
from itertools import chain
from chicken_turtle_util.exceptions import InvalidOperationError
import heapq

_logger = logging.getLogger(__name__)

cancel = False

class TopK(object): #TODO rename TopRecipes, k -> max_branches, max_leafs
    
    def __init__(self, k):
        self._k = k
        self._branches = []  # heapq by score, keeping the K highest scoring branch recipes
        self._leafs = []  # heapq by score, keeping the K highest scoring leaf recipes
        self._pushed = False
    
    def __iter__(self):
        '''
        Yield top recipes, ordered by descending score
        '''
        return iter(sorted(self._leafs + self._branches, reverse=True, key=lambda recipe: recipe.score))
    
    def pop_branches(self):
        '''
        Yield all branch recipes from worst to best
        
        Manipulating/accessing the TopK object while iterating is
        supported/safe. Any branch recipes pushed while iterating will be
        yielded.
        
        Yields
        ------
        Recipe
        '''
        while True:
            recipe = self._pop()
            if recipe is None:
                return
            yield recipe
        
    def unset_pushed(self):
        self._pushed = False
        
    def _pop(self):
        '''
        Pop the worst branch recipe
        
        Returns
        -------
        Recipe or None
            Branch recipe or, if no branch recipes, None
        '''
        # TODO a combo of next_max_distance, score might work better than
        # plainly next_max_distance first and score as tie-breaker (the former
        # being a float makes it unlikely, the score is ever taken into
        # account). How would you combine these 2 though?
        
        # Pop
        if not self._branches:
            return None
        recipe = heapq.heappop(self._branches)
        return recipe
    
    def push(self, recipe):
#         print('p', end='', flush=True)
        if recipe.is_leaf:
            recipes = self._leafs
        else:
            recipes = self._branches
            
        if len(recipes) >= self._k:
            popped = heapq.heappushpop(recipes, recipe)
            if popped != recipe:
                self._pushed = True
        else:
            heapq.heappush(recipes, recipe)
            self._pushed = True
#         print('P', end='', flush=True)
        
    @property
    def pushed(self):
        '''
        Whether a recipe has been pushed since the last call to `unset_pushed`
        (or since construction)
        '''
        return self._pushed
    
    def format_stats(self):
        recipes = self._leafs + self._branches
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

class Recipe(object):
    
    '''
    A recipe: which foods, how much of each, resulting score.
    
    Parameters
    ----------
    clusters : Iterable(soylent_recipes.cluster.Node)
        Clusters whose representatives form the foods of the recipe
    nutrition_target : soylent_recipes.nutrition_target.NutritionTarget
        Nutrition target the recipe should be solved for
    '''
    
    def __init__(self, clusters, nutrition_target):
        if not clusters:
            raise ValueError('clusters must be non-empty sequence. Got: {!r}'.format(self.clusters))
        
        self._clusters = tuple(clusters)
        self._nutrition_target = nutrition_target
        
        # Solve diet problem resulting in scored recipe
        foods = pd.DataFrame([cluster.representative for cluster in self.clusters])
        self._score, self._amounts = solver.solve(self._nutrition_target, foods)
    
    @property
    def clusters(self):
        '''
        Clusters whose representatives form the foods of the recipe
        
        Returns
        -------
        tuple(soylent_recipes.cluster.Node)
        '''
        return self._clusters
    
    @property
    def score(self):
        '''
        Score of recipe. 
        
        Returns
        -------
        (solved :: bool, sub_score :: float)
            sub_score is never NaN.
        '''
        return self._score
    
    @property
    def solved(self):
        return self._score[0]
    
    @property
    def amounts(self):
        '''
        Amount of each food to use to achieve the most optimal score `score`.
        
        `amounts[i]` is the amount of `clusters[i].representative` to use.
        
        Returns
        -------
        np.array([float])
        '''
        return self._amounts
    
    @property
    def max_distance(self):
        '''
        Max cluster.max_distance
        
        Returns
        -------
        float
        '''
        return max(cluster.max_distance for cluster in self.clusters)
    
    @property
    def next_cluster(self):
        '''
        Next cluster to split.
        
        Returns
        -------
        soylent_recipes.cluster.Node
        '''
        if self.is_leaf:
            raise InvalidOperationError('No next_cluster on a leaf recipe')
            
        # For the next cluster to split, pick the one with max max_distance in
        # order to reduce recipe max_distance in the split recipe
        return max((cluster for cluster in self.clusters), key=lambda cluster: cluster.max_distance)
        
    @property
    def is_leaf(self):
        '''
        Whether recipe is a leaf. True iff no cluster has a child.
        
        Returns
        -------
        bool
        '''
        return all(cluster.is_leaf for cluster in self.clusters)
        
    def replace(self, replacee, replacement):
        '''
        Replace clusters with clusters
        
        Parameters
        ----------
        replacee : Iterable(_Cluster)
            One or more clusters to replace
        replacement : Iterable(_Cluster)
            Zero or more clusters to replace the replacee with
            
        Returns
        -------
        Recipe
            Recipe with clusters replaced
        '''
        if not replacee:
            raise ValueError('replacee must not be empty. replacee={!r}'.format(replacee))
        if not set(replacement).isdisjoint(set(replacee)):
            raise ValueError(
                'replacement and replacee overlap: replacee={!r}. replacement={!r}.'
                .format(replacee, replacement)
            )
        clusters = list(self.clusters)
        for cluster in replacee:
            clusters.remove(cluster)
        clusters.extend(replacement)
        assert len(set(clusters)) == len(clusters)
        return Recipe(clusters, self._nutrition_target)
    
    def __lt__(self, other):
        '''
        recipe1 < recipe2 iff it's worse than recipe2
        '''
        return self.score < other.score #TODO take into account max_distance. When one is far more detailed than the other, this should affect comparison 
    
    def __len__(self):
        '''
        Number of (representing) foods
        '''
        return len(self.clusters)
    
    def __repr__(self): #TODO: not a good repr, make a format func or so
        return '{}, {:.2f}, {}, {}'.format(
            self.score,
            self.max_distance,
            ''.join(('f' if cluster.is_leaf else 'C') for cluster in self.clusters),
            ' '.join(str(cluster.id_) for cluster in self.clusters)
        )

#TODO add to CTU        
import cProfile
import pyprof2calltree
import functools
class profile(object):
    
    def __call__(self, f):
        @functools.wraps(f)
        def profiled(*args, **kwargs):
            profile = cProfile.Profile()
            profile.enable()
            try:
                return f(*args, **kwargs)
            finally:
                profile.disable()
                profile.dump_stats('profile.cprofile')
                pyprof2calltree.convert(profile.getstats(), 'profile.kgrind')
                pyprof2calltree.visualize(profile.getstats())
        return profiled
            

# TODO ideas:
# - instead of >, require to be at least x% better
# - instead of NaN score, solve a diet problem without min-max, or try to get the solver to solve it as close as possible and then add errors for it. Scores of relaxed problem should always be < score of real problem
@profile()
def mine(root_node, nutrition_target, top_recipes):
    '''
    Mine recipes
    
    Parameters
    ----------
    root_node : soylent_recipes.cluster.Node
        Root node of hierarchical clustering of foods
    nutrition_target : soylent_recipes.nutrition_target.NutritionTarget
    top_recipes : TopK
    '''
    _logger.info('Mining')
    max_foods = 10
    top_recipes.push(Recipe([root_node], nutrition_target))
    
    for recipe in top_recipes.pop_branches():
#         print('i', end='', flush=True)
        # return when cancelled
        if cancel:
            return
        
        # Split cluster
        cluster = recipe.next_cluster
        left, right = cluster.children
        recipe_both = recipe.replace([cluster], [left, right])
        top_recipes.unset_pushed()
        if recipe_both.score > recipe.score or not recipe.solved:
            if len(recipe_both) <= max_foods:
                # We have room for both and we know it improves score, so add it
                top_recipes.push(recipe_both)
            else:
                # We need to drop a food to stay within the max foods limit
                for cluster in recipe_both.clusters:
                    split_recipe = recipe_both.replace([cluster], [])
                    if split_recipe.score > recipe.score or not recipe.solved: #TODO what if left or right happens to have the same representative. No need to solve it again, but do push it again despite having equal score
                        # Only push if it still improves
                        top_recipes.push(split_recipe)
        
        if not top_recipes.pushed:
            # None of the above splits resulted in improved score, so replace
            # the cluster with the food that represents it. This is an
            # approximation, further splits could still have led to a better
            # score.
            assert False  #FIXME cluster.representative is a food, need to replace with representative_node Leaf node of representative
            top_recipes.push(recipe.replace([cluster], [cluster.representative]))  
    
    # old: did not yield any results in reasonable time, but then again wasn't tested for correctness either. Still, this bruteforce likely wouldn't have worked; far too large search space.
    #TODO we could throw out any foods that aren't contributing once we
    #`solved` flips to True. But in a way that history is kept so that
    #we can go back when index changes
    # Simply finding the first good combo takes a looong time
                    
        