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

class Recipe(object):
    
    '''
    A recipe: which foods, how much of each, resulting score.
    
    Parameters
    ----------
    food_indices : np.array
        Indices of foods in recipe referencing foods in all_foods
    nutrition_target : soylent_recipes.nutrition_target.NormalizedNutritionTarget
        Nutrition target the recipe should be solved for
    all_foods : np.array
        All normalized foods.
    '''
    
    def __init__(self, food_indices, nutrition_target, all_foods):
        # Solve diet problem resulting in scored recipe
        self._food_indices = food_indices.copy()
        self._score, self._amounts = solver.solve(nutrition_target, all_foods[food_indices])
    
    @property
    def food_indices(self):
        '''
        Food indices
        
        Returns
        -------
        np.array([int])
        '''
        return self._food_indices.copy()
    
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
        
        `amounts[i]` is the amount of food referred to by `food_indices[i]` to
        use.
        
        Returns
        -------
        np.array([float])
        '''
        return self._amounts
    
    def __len__(self):
        '''
        Number of foods
        '''
        return len(self._foods)
    
    def __repr__(self):
        return 'Recipe(food_indices={})'.format(self._food_indices)
    