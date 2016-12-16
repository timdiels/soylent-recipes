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
from functools import partial
import heapq
import attr
import numpy as np
import asyncio

_logger = logging.getLogger(__name__)

# Source: https://mail.python.org/pipermail/python-list/2010-December/594821.html
# Adjusted to be keep top k scoring items as: (score, item)
class TopK(object):
    
    def __init__(self, k):
        self._k = k
        self._scores = []
        self._items = {}  # score => [item]
    
    def add(self, pair):
        heap = self._heap
        if len(heap) >= self.n:
            score, item = pair
            popped = heapq.heappushpop(heap, score)
            added = score != popped
            if added:
                self._items[score].append(item)
                items = self._items[popped]
                if len(items) == 1:
                    del self._items[popped]
                else:
                    items.pop()
            self.tally = partial(heapq.heappushpop, heap)
        else:
            added = True
            heapq.heappush(heap, item)
        return added
    
    def __iter__(self):
        '''
        Yield all (score, item) in descending order
        '''
        return (
            (score, item) 
            for score, items in sorted(self._items.items(), reverse=True)
            for item in items
        )
    
    def __str__(self):
        return str(sorted(self.heap, reverse=True))
    
    def __len__(self):
        return len(self._scores)
    
Recipe = attr.make_class('Recipe', ('amounts', 'foods'), frozen=True)
cancel = False

def mine(foods, nutrition_target, top_recipes):
    '''
    Mine recipes
    
    Parameters
    ----------
    foods : pd.DataFrame
    nutrition_target : soylent_recipes.nutrition_target.NutritionTarget
    '''
    max_foods = 10
    start = True
    food_indices = []
    scores = [-np.inf]
    index = 0
    _logger.info('Mining')
    while food_indices or start:
        start = False
        for index in range(index, len(foods)):
            # return when cancelled
            if cancel:
                return
            
            # temporarily add index and solve
            print(food_indices + [index], len(top_recipes))
            foods_ = foods.iloc[food_indices + [index]]
            objective, amounts = solver.solve(nutrition_target, foods_)
            solved = objective is not None
            
            if solved:
                # score result
                score = -objective
                top_recipes.add((score, Recipe(amounts, foods_)))
            else:
                assert scores[-1] == -np.inf
                score = -np.inf
                
            # if did not manage to solve, keep it (we probably do not have enough foods to combine yet);
            # or if the new food (index) improves the score, keep it;
            # unless we've hit max_foods, then there's no room
            if (not solved or score > scores[-1]) and len(food_indices)+1 < max_foods:
                scores.append(score)
                food_indices.append(index)
                
            #TODO we could throw out any foods that aren't contributing once we
            #`solved` flips to True. But in a way that history is kept so that
            #we can go back when index changes
            # Simply finding the first good combo takes a looong time
                    
        #
        index = food_indices.pop() + 1
        scores.pop()
        