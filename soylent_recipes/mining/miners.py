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
from soylent_recipes.mining.recipe import Recipe
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
        
    def mine_random(self, nutrition_target, foods):
        '''
        Randomly grab max_foods foods, repeat until k solved recipes are found.
        
        Returns
        -------
        recipes_scored : int
        [Recipe]
            Up to k solved recipes.
        '''
        k = 1000
        _logger.info('Mining: random, max_foods={}, k={}'.format(self._max_foods, k))
        return self._mine_random(nutrition_target, foods, k, greedy=False)
    
    def mine_greedy(self, nutrition_target, foods):
        '''
        Like mine_random but greedily refine each random selection.
        
        Pick max_foods foods at random. For i in range(max_foods), try replacing
        recipe[i] with any food in foods, until the recipe solves. Repeat until
        k solved recipes are found.
        
        Returns
        -------
        recipes_scored : int
        [Recipe]
            Up to k solved recipes.
        '''
        k = 1000
        _logger.info('Mining: greedy, max_foods={}, k={}'.format(self._max_foods, k))
        return self._mine_random(nutrition_target, foods, k, greedy=True)
    
    def _mine_random(self, nutrition_target, foods, k, greedy):
        solved_recipes = []
        recipes_scored = 0
        foods_ = foods.values
        while not self._cancel:
            food_indices = np.random.choice(len(foods_), self._max_foods, replace=False)
            
            if greedy:
                # Greedily select best food on each index
                for i in range(self._max_foods):
                    original_index = food_indices[i]
                    # Try each food as food_indices[i]
                    for food_index in range(len(foods_)):
                        food_indices[i] = food_index
                        recipes_scored += 1
                        recipe = Recipe(food_indices, nutrition_target, foods_)
                        if recipe.solved or self._cancel:
                            break
                    if recipe.solved or self._cancel:
                        break
                    food_indices[i] = original_index
                print('.', end='', flush=True)
            else:
                recipes_scored += 1
                recipe = Recipe(food_indices, nutrition_target, foods_)
            if recipe.solved:
                solved_recipes.append(recipe)
                if len(solved_recipes) == k:
                    break
            
        return recipes_scored, solved_recipes
