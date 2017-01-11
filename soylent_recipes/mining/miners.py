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
import attr
from soylent_recipes.various import profile
from soylent_recipes.mining.cluster_recipe import ClusterRecipes, TopClusterRecipes
from soylent_recipes.mining.recipe import Recipe
from soylent_recipes.mining.top_k import TopK
import numpy as np

_logger = logging.getLogger(__name__)

@attr.s(frozen=True)
class Stats(object):
    recipes_scored = attr.ib()
    recipes_skipped_due_to_visited = attr.ib()
    
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

class Miner(object):
    
    def __init__(self):
        self._cancel = False
        self._max_foods = 20
        assert self._max_foods > 0
        
    def cancel(self):
        _logger.info('Cancelling')
        self._cancel = True
        
#     @profile()
    def mine_cluster_walk(self, root_node, nutrition_target, foods):
        '''
        Mine recipes
        
        Parameters
        ----------
        root_node : soylent_recipes.cluster.Node
            Root node of hierarchical clustering of normalized foods
        nutrition_target : soylent_recipes.nutrition_target.NormalizedNutritionTarget
        max_
        foods : pd.DataFrame
            All normalized foods, matching the food indices referenced by the cluster nodes.
            
        Returns
        -------
        Stats
        [Recipe]
            Recipes sorted by descending score.
        '''
        assert (foods.columns == nutrition_target.index).all()  # sample root node to check that foods have same nutrients as the target
        max_leafs = 10
        max_branches = 1000
        _logger.info('Mining: cluster crawl, max_foods={}, max_leafs={}, max_branches={}'.format(self._max_foods, max_leafs, max_branches))
        recipes = ClusterRecipes(nutrition_target, foods.values)
        top_recipes = TopClusterRecipes(max_leafs=max_leafs, max_branches=max_branches)
        top_recipes.push(recipes.create([root_node]))
        
        for recipe in top_recipes.pop_branches():
            # return when cancelled
            if self._cancel:
                break
            
            # Split cluster
            next_cluster = recipe.next_cluster
            left, right = next_cluster.children
            recipe_both = recipes.replace(recipe, [next_cluster], [left, right])
            top_recipes.unset_pushed()
            if recipe_both and (recipe_both.score > recipe.score or not recipe.solved): #TODO always true, because never solved
                if len(recipe_both) <= self._max_foods:
                    # We have room for both and we know it improves score, so add it
                    top_recipes.push(recipe_both)
                else:
                    # We need to drop a food to stay within the max foods limit
                    for cluster in recipe_both.clusters:
                        split_recipe = recipes.replace(recipe_both, [cluster], [])
                        if split_recipe and (split_recipe.score > recipe.score or not recipe.solved): #TODO always true #TODO what if left or right happens to have the same representative. No need to solve it again, but do push it again despite having equal score
                            # Only push if it still improves
                            top_recipes.push(split_recipe)
            
            if not top_recipes.pushed:
                # None of the above splits resulted in improved score, so replace
                # the cluster with the food that it represents. This is an
                # approximation, further splits could still have led to a better
                # score.
                recipe = recipes.replace(recipe, [next_cluster], [next_cluster.leaf_node])
                if recipe:
                    top_recipes.push(recipe)
        
        _logger.info(top_recipes.format_stats())
        stats = Stats(
            recipes.recipes_scored,
            recipes.recipes_skipped_due_to_visited
        )
        return stats, [recipe for recipe in top_recipes if recipe.is_leaf]
        
        # old: did not yield any results in reasonable time, but then again wasn't tested for correctness either. Still, this bruteforce likely wouldn't have worked; far too large search space.
        #TODO we could throw out any foods that aren't contributing once we
        #`solved` flips to True. But in a way that history is kept so that
        #we can go back when index changes
        # Simply finding the first good combo takes a looong time
        
    def mine_random(self, nutrition_target, foods): #TODO reuse mine_greedy with refine_passes=0
        '''
        Randomly grab max_foods foods, repeat until stopped, keep top k scoring
        recipes.
        
        Returns
        -------
        Stats
        [Recipe]
            Recipes sorted by descending score.
        '''
        k = 1000
        _logger.info('Mining: random, max_foods={}, k={}'.format(self._max_foods, k))
        top_recipes = TopK(k, key=lambda recipe: recipe.score)
        recipes_scored = 0
        foods_ = foods.values
        while not self._cancel:
            food_indices = np.random.choice(len(foods_), self._max_foods, replace=False)
            top_recipes.push(Recipe(food_indices, nutrition_target, foods_))
            recipes_scored += 1
            
        stats = Stats(
            recipes_scored,
            recipes_skipped_due_to_visited=0
        )
        return stats, top_recipes.sorted_items
    
    def mine_greedy(self, nutrition_target, foods):
        '''
        Like mine_random but greedily refine each random selection.
        
        Pick max_foods foods at random. Then i in range(max_foods), try
        replacing recipe[i] with any food in foods, keeping the one resulting in
        the best score. Repeat until stopped. Keep top k scoring.
        
        Returns
        -------
        Stats
        [Recipe]
            Recipes sorted by descending score.
        '''
        k = 1000
        _logger.info('Mining: greedy, max_foods={}, k={}, passes=1'.format(self._max_foods, k))
        top_recipes = TopK(k, key=lambda recipe: recipe.score)
        top_intermediates = TopK(1, key=lambda recipe: recipe.score)
        recipes_scored = 0
        foods_ = foods.values
        while not self._cancel:
            food_indices = np.random.choice(len(foods_), self._max_foods, replace=False)
            
            # Greedily select best food on each index
            for i in range(self._max_foods):
                # Try each food as food_indices[i]
                for food_index in range(len(foods_)):
                    food_indices[i] = food_index
                    recipes_scored += 1
                    recipe = Recipe(food_indices, nutrition_target, foods_)
                    top_intermediates.push(recipe)
                    if self._cancel:
                        break
                    
                # Select the best
                food_indices = top_intermediates.pop().food_indices #TODO shouldn't Recipe.food_indices return a copy instead? Test whether it'd affect performance much (probably not)
                if self._cancel:
                    break
            
            recipes_scored += 1
            top_recipes.push(Recipe(food_indices, nutrition_target, foods_))
            print('.', end='', flush=True)
            
        stats = Stats(
            recipes_scored,
            recipes_skipped_due_to_visited=0
        )
        return stats, top_recipes.sorted_items
