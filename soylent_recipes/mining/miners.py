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
from soylent_recipes.config import max_foods, max_recipes
from soylent_recipes.various import profile
from soylent_recipes.mining.recipe import Recipe
import numpy as np

_logger = logging.getLogger(__name__)

@attr.s(frozen=True)
class Stats(object):
    recipes_scored = attr.ib()
    recipes_skipped_due_to_visited = attr.ib()
    
class Miner(object):
    
    def __init__(self):
        self._cancel = False
        assert max_foods > 0
        assert max_recipes > 0
        
    def cancel(self):
        _logger.info('Cancelling')
        self._cancel = True
        
    def mine_random(self, nutrition_target, foods):
        '''
        Randomly pick max_foods foods, repeat until k solved recipes are found.
        
        Returns
        -------
        recipes_tried : int
            Number of recipes tried.
        [Recipe]
            Up to k solved recipes.
        '''
        _logger.info('Mining: random, max_foods={}, max_recipes={}'.format(max_foods, max_recipes))
        solved_recipes = []
        recipes_tried = 0
        foods_ = foods.values
        while not self._cancel:
            food_indices = np.random.choice(len(foods_), max_foods, replace=False)
            
            recipes_tried += 1
            recipe = Recipe(food_indices, nutrition_target, foods_)
            
            if recipe.solved:
                print('.', end='', flush=True)
                solved_recipes.append(recipe)
                if len(solved_recipes) == max_recipes:
                    break
            
        return recipes_tried, solved_recipes
