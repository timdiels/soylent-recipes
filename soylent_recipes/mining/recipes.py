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

from soylent_recipes import solver
from chicken_turtle_util.exceptions import InvalidOperationError

class Recipes(object):
    
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
        Recipe or None
            Recipe if first time creating it, None otherwise.
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
            return Recipe(clusters, self._nutrition_target, self._foods)
        
    def replace(self, recipe, replacee, replacement):
        '''
        Replace clusters on recipe with clusters
        
        Parameters
        ----------
        recipe : Recipe
            Recipe whose clusters to start from
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
        clusters = list(recipe.clusters)
        for cluster in replacee:
            clusters.remove(cluster)
        clusters.extend(replacement)
        assert len(set(clusters)) == len(clusters)
        return self.create(clusters)

class Recipe(object):
    
    '''
    A recipe: which foods, how much of each, resulting score.
    
    Do not create directly, use Recipes.create instead.
    
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
        
        # Solve diet problem resulting in scored recipe
        foods = all_foods[[cluster.food_index for cluster in self.clusters]]
        self._score, self._amounts = solver.solve(nutrition_target, foods)
    
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
        
    def __len__(self):
        '''
        Number of (representing) foods
        '''
        return len(self.clusters)
    
    def __repr__(self):
        return 'Recipe(clusters=[{}])'.format(' '.join(str(cluster.id_) for cluster in self.clusters))