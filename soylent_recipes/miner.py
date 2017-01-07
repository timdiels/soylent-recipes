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
from soylent_recipes.various import TopK

_logger = logging.getLogger(__name__)

cancel = False

class TopRecipes(object): #TODO k -> max_branches, max_leafs
    
    '''
    List of top recipes
    
    Keeps k branches, k leafs. When exceeding k branches/leafs, drops the lowest
    scoring branch/leaf respectively.
    '''
    
    def __init__(self, k):
        self._k = k
        self._key = lambda recipe: recipe.score
        self._pushed = False
        self._leafs = TopK(k, self._key)
        self._branches = TopK(k, self._key)
        self._visited = set()
        
        # Note: pruning will be unused so long as k>=max_branches, given how we use this
        self._branches_by_max_distance = TopK(k, lambda recipe: -recipe.max_distance) 
    
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
        
        # When we've already visited the recipe, skip it #TODO don't even create the recipe in the first place; thus avoiding scoring it
        if recipe in self._visited:
            return
        self._visited.add(recipe)
        
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

recipes_scored = 0

class Recipe(object):
    
    '''
    A recipe: which foods, how much of each, resulting score.
    
    Parameters
    ----------
    clusters : Iterable(soylent_recipes.cluster.Node)
        Clusters whose representatives form the foods of the recipe
    nutrition_target : soylent_recipes.nutrition_target.NormalizedNutritionTarget
        Nutrition target the recipe should be solved for
    all_foods : np.array
        All normalized foods.
    '''
    
    def __init__(self, clusters, nutrition_target, all_foods):
        if not clusters:
            raise ValueError('clusters must be non-empty sequence. Got: {!r}'.format(self.clusters))
        
        self._clusters = tuple(sorted(clusters, key=lambda cluster: cluster.id_))
        self._nutrition_target = nutrition_target
        self._all_foods = all_foods
        
        # Solve diet problem resulting in scored recipe
        foods = all_foods[[cluster.food_index for cluster in self.clusters]]
        self._score, self._amounts = solver.solve(self._nutrition_target, foods)
#         print(self._score[1])
        global recipes_scored
        recipes_scored += 1
    
    @property
    def clusters(self):
        '''
        Cluster nodes whose foods form the foods of the recipe
        
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
        
        `amounts[i]` is the amount of `clusters[i].food` to use.
        
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
        return Recipe(clusters, self._nutrition_target, self._all_foods)
    
    def __eq__(self, other):
        return other is not None and self.clusters == other.clusters
    
    def __hash__(self):
        return hash(self.clusters)
    
    def __len__(self):
        '''
        Number of (representing) foods
        '''
        return len(self.clusters)
    
    def __repr__(self):
        return 'Recipe(clusters=[{}])'.format(' '.join(str(cluster.id_) for cluster in self.clusters))
        
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
            

# Note: the current miner revisits recipes, which are then ignored by
# TopRecipes. This is how it ends up at the same point:
#
#   a b
#   split a and drop one
#   a1 b  ,  a2 b  , ...
#   split b and drop one
#   b1 b2 ,  b1 b2 , ...
#
# TODO could this be avoided?

# TODO ideas:
# - instead of >, require to be at least x% better
# - instead of NaN score, solve a diet problem without min-max, or try to get the solver to solve it as close as possible and then add errors for it. Scores of relaxed problem should always be < score of real problem
# @profile()
def mine(root_node, nutrition_target, top_recipes, foods):
    '''
    Mine recipes
    
    Parameters
    ----------
    root_node : soylent_recipes.cluster.Node
        Root node of hierarchical clustering of normalized foods
    nutrition_target : soylent_recipes.nutrition_target.NormalizedNutritionTarget
    top_recipes : TopK
    foods : pd.DataFrame
        All normalized foods, matching the food indices referenced by the cluster nodes.
    '''
    assert (foods.columns == nutrition_target.index).all()  # sample root node to check that foods have same nutrients as the target
    _logger.info('Mining')
    max_foods = 10
    top_recipes.push(Recipe([root_node], nutrition_target, foods.values))
    
    for recipe in top_recipes.pop_branches():
        # return when cancelled
        if cancel:
            return
        
        # Split cluster
        next_cluster = recipe.next_cluster
        left, right = next_cluster.children
        recipe_both = recipe.replace([next_cluster], [left, right])
        top_recipes.unset_pushed()
        if recipe_both.score > recipe.score or not recipe.solved: #TODO always true
            if len(recipe_both) <= max_foods:
                # We have room for both and we know it improves score, so add it
                top_recipes.push(recipe_both)
            else:
                # We need to drop a food to stay within the max foods limit
                for cluster in recipe_both.clusters:
                    split_recipe = recipe_both.replace([cluster], [])
                    if split_recipe.score > recipe.score or not recipe.solved: #TODO always true #TODO what if left or right happens to have the same representative. No need to solve it again, but do push it again despite having equal score
                        # Only push if it still improves
                        top_recipes.push(split_recipe)
        
        if not top_recipes.pushed:
            # None of the above splits resulted in improved score, so replace
            # the cluster with the food that it represents. This is an
            # approximation, further splits could still have led to a better
            # score.
            top_recipes.push(recipe.replace([next_cluster], [next_cluster.leaf_node]))
    
    # old: did not yield any results in reasonable time, but then again wasn't tested for correctness either. Still, this bruteforce likely wouldn't have worked; far too large search space.
    #TODO we could throw out any foods that aren't contributing once we
    #`solved` flips to True. But in a way that history is kept so that
    #we can go back when index changes
    # Simply finding the first good combo takes a looong time
                    
        