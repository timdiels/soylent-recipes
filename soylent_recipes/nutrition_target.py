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

import attr
import numpy as np
import pandas as pd

def _convert_minimize(minimize):
    if minimize:
        for nutrient, weight in minimize.items():
            if weight < 0.0 or np.isclose(weight, 0.0):
                raise ValueError(
                    'minimize weight for nutrient {!r} is <= 0. '
                    'It must be > 0 and not np.isclose to 0. '
                    'Got weight={!r}'
                    .format(nutrient, weight)
                )
        sum_ = sum(minimize.values())
        return {nutrient: weight/sum_ for nutrient, weight in minimize.items()}
    else:
        return minimize

@attr.s(frozen=True)
class NutritionTarget(object):
    '''
    Desired nutrition to achieve
    
    Parameters
    ----------
    minima : {nutrient :: str => float}
        Minimum value constraints on nutrients (and variables)
    maxima : {nutrient :: str => float}
        Maximum value constraints on nutrients (and variables)
    minimize : {nutrient :: str => weight :: float}
        Minimize the amount of given nutrients, along with weights. I.e. minimize weighted sum.
    '''
    minima = attr.ib()
    maxima = attr.ib()
    minimize = attr.ib(convert=_convert_minimize)
    
    def assert_recipe_matches(self, amounts, foods): #TODO rename assert_recipe_satisfies
        '''
        Assert recipe satisfies this nutrition target
        
        Parameters
        ----------
        amounts : np.array(float)
        foods : pd.DataFrame
        '''
        foods_ = foods.iloc[:,foods.columns != 'description']
        result = pd.Series(amounts, index=foods_.index).dot(foods_)
        for nutrient, min_ in self.minima.items():
            assert result[nutrient] > min_ or np.isclose(result[nutrient], min_)
        for nutrient, max_ in self.maxima.items():
            assert result[nutrient] < max_ or np.isclose(result[nutrient], max_) 

def from_config():
    '''
    Create nutrition target from config file
    '''
    from .config import extrema, minimize
    
    # extrema
    for nutrient, (min_, max_) in extrema.items():
        assert np.isfinite(min_), nutrient
        assert min_ >= 0, nutrient
        
        assert not np.isinf(max_), nutrient
        
        if not np.isnan(max_):
            assert min_ + 1e-8 < max_, "{}'s min ({}) >= max ({}). Should be min < max.".format(nutrient, min_, max_)
            
    # split into targets, minima, maxima
    minima = {nutrient: min_ for nutrient, (min_, max_) in extrema.items()}
    maxima = {nutrient: max_ for nutrient, (min_, max_) in extrema.items() if not np.isnan(max_)}
    
    # minimize
    for nutrient, weight in minimize.items():
        assert not np.isclose(weight, 0.0), nutrient
        if weight > 0:
            assert nutrient in minima, nutrient  # Else it might minimize to -inf (in which case the linear (diet) problem is unbounded and no solution is returned) 
        if weight < 0:
            assert nutrient in maxima, nutrient  # Else it might maximize to inf (in which case the linear (diet) problem is unbounded and no solution is returned)
    
    # make sure everthing is float
    minima = {nutrient: float(value) for nutrient, value in minima.items()}
    maxima = {nutrient: float(value) for nutrient, value in maxima.items()}
    minimize = {nutrient: float(weight) for nutrient, weight in minimize.items()}
    
    return NutritionTarget(minima, maxima, minimize)

