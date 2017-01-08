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

from chicken_turtle_util.exceptions import InvalidOperationError
import pandas as pd
import numpy as np
from textwrap import dedent
from itertools import chain
from soylent_recipes.mining.top_k import TopK
from soylent_recipes.mining.recipe import Recipe

class TopClusterRecipes(object):
    
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
        ClusterRecipe
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

class ClusterRecipes(object):
    
    '''
    Context of created recipes
    '''
    
    def __init__(self, nutrition_target, all_foods):
        '''
        Parameters
        ----------
        nutrition_target : soylent_recipes.nutrition_target.NormalizedNutritionTarget
            Nutrition target the recipes should be solved for
        all_foods : np.array
            All normalized foods.
        '''
        self._nutrition_target = nutrition_target
        self._foods = all_foods
        self._visited = set()
        self._recipes_scored = 0
        self._recipes_skipped_due_to_visited = 0  # recipes rejected due to already having been visited
        
    @property
    def recipes_scored(self):
        return self._recipes_scored
    
    @property
    def recipes_skipped_due_to_visited(self):
        return self._recipes_skipped_due_to_visited
        
    def create(self, clusters):
        '''
        Create recipe if it has not been created before
        
        Returns
        -------
        ClusterRecipe or None
            ClusterRecipe if first time creating it, None otherwise.
        '''
        # clusters
        if not clusters:
            raise ValueError('clusters must be non-empty sequence. Got: {!r}'.format(self.clusters))
        clusters = tuple(sorted(clusters))
        
        # When we've already visited the recipe, skip it
        if clusters in self._visited:
            self._recipes_skipped_due_to_visited += 1
            return None
        else:
            self._recipes_scored += 1
            self._visited.add(clusters)
            return ClusterRecipe(clusters, self._nutrition_target, self._foods)
        
    def replace(self, recipe, replacee, replacement):
        '''
        Replace clusters on recipe with clusters
        
        Parameters
        ----------
        recipe : ClusterRecipe
            Recipe whose clusters to start from
        replacee : Iterable(_Cluster)
            One or more clusters to replace
        replacement : Iterable(_Cluster)
            Zero or more clusters to replace the replacee with
            
        Returns
        -------
        ClusterRecipe
            Recipe with clusters replaced
        '''
        if not replacee:
            raise ValueError('replacee must not be empty. replacee={!r}'.format(replacee))
        if not set(replacement).isdisjoint(set(replacee)):
            raise ValueError(
                'replacement and replacee overlap: replacee={!r}. replacement={!r}.'
                .format(replacee, replacement)
            )
        clusters = list(recipe.clusters)
        for cluster in replacee:
            clusters.remove(cluster)
        clusters.extend(replacement)
        assert len(set(clusters)) == len(clusters)
        return self.create(clusters)

class ClusterRecipe(object):
    
    '''
    Recipe of food nodes
    
    Do not create directly, use ClusterRecipes.create instead.
    
    Implements soylent_recipes.mining.recipe.Recipe.
    
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
        self._clusters = clusters
        self._recipe = Recipe(np.fromiter((cluster.food_index for cluster in self.clusters), int), nutrition_target, all_foods)
        
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
        
    def __len__(self):
        '''
        Number of (representing) foods
        '''
        return len(self.clusters)
    
    def __repr__(self):
        return 'ClusterRecipe(clusters=[{}])'.format(' '.join(str(cluster.id_) for cluster in self.clusters))
    
    def __getattr__(self, attr):
        return getattr(self._recipe, attr)
    
