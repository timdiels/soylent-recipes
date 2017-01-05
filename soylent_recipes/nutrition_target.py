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

import numpy as np
import pandas as pd

def create(target):
    '''
    Create NutritionTarget
    
    Parameters
    ----------
    target : pd.DataFrame
        Nutrient constraints. Nutrient amounts are in SI units (i.e. g most of
        the time).
        
        Index: str. Nutrient name, may contain spaces.
        
        Columns:
        
        min : float
            Minimum required amount of nutrient. min > 0 or is NaN. If NaN, no
            minimum constraint is imposed on the nutrient.
        max : float
            Maximum allowed amount of nutrient. max > min, 0 or is NaN. If NaN,
            no maximum constraint is imposed on the nutrient.
        
        Either of min, max must be finite.
    
    Returns
    -------
    NutritionTarget
    '''
    # TODO what's the effect of close to zero minima? -> close to zero pseudo targets in some cases. Is 1e-8 really that close to 0?
    
    # Copy input so we don't mutate it
    original = target
    target = target.copy()
    
    # Skip if empty (avoids pd.DataFrame.applymap bug)
    if target.empty:
        return pd.DataFrame(columns=('min', 'max', 'pseudo_target'), dtype=float)
    
    # Set dtype to float
    target = target.astype(float)
    
    # Validate
    _validate(target, original)
    
    # Add pseudo targets
    def pseudo_target(row):
        if np.isnan(row['max']):
            # Has only a min constraint:
            # *1.1 for less likelihood of undershooting the min
            return 1.1 * row['min']
        elif np.isnan(row['min']):
            # Has only a max constraint:
            # *0.5 for less likelihood of overshooting the max. Not 0.9
            # as that would require far too much of something we just
            # don't want too much of
            return 0.5 * row['max']
        else:
            # Has a min and a max constraint:
            return (row['min'] + row['max']) / 2.0
    target['pseudo_target'] = target.apply(pseudo_target, axis=1)
    
    # Return
    return target

    
def _validate(target, original):
    # finite or NaN
    mask = target.applymap(np.isinf).any(axis=1)
    invalid_rows = original[mask]
    if not invalid_rows.empty:
        raise ValueError(
            'Encountered np.inf or -np.inf. '
            'Values must be finite or NaN. '
            'Invalid rows:\n{}'
            .format(invalid_rows.to_string())
        )
    
    # min > 0 or NaN
    mask = target['min'] <= 0
    invalid_rows = original[mask]
    if not invalid_rows.empty:
        raise ValueError(
            'min <= 0. '
            'Expected: min > 0 or min=NaN. '
            'Invalid rows:\n{}'
            .format(invalid_rows['min'].to_string())
        )
    
    # max > min and 0 if max not NaN
    mask = (target['max'] <= 0) | (target['max'] <= target['min'])
    invalid_rows = original[mask]
    if not invalid_rows.empty:
        raise ValueError(
            'max <= min, 0. '
            'Expected: max > min, 0 or max=NaN. '
            'Invalid rows:\n{}'
            .format(invalid_rows[['min', 'max']].to_string())
        )
    
    # No all NaN rows
    mask = target.isnull().all(axis=1)
    invalid_rows = original[mask]
    if not invalid_rows.empty:
        raise ValueError(
            'Some rows are all NaN (when treating min=0 as min=NaN). '
            'This does not define any constraint for the nutrient. Expected: min>0 or max>min,0. '
            'Either remove the nutrient or constrain it. '
            'Invalid rows:\n{}'
            .format(invalid_rows.to_string())
        )
    
class NutritionTarget(object):
    '''
    Interface: constraints and nutrition preferences
    
    This is a pd.DataFrame. Nutrient amounts are in SI units (i.e. g most of the
    time).
    
    Index: str. Nutrient name, may contain spaces.
    
    Columns:
    
    min : float
        Minimum required amount of nutrient. min > 0 or is NaN. If NaN, no
        minimum constraint is imposed on the nutrient.
    max : float
        Maximum allowed amount of nutrient. max > min, 0 or is NaN. If NaN,
        no maximum constraint is imposed on the nutrient.
    pseudo_target : float
        Target to use instead of extrema (min and max) when using a solver which
        does not support constraints. In calculating error to the pseudo target,
        euclidean distance must be used (or a metric proportional to it, e.g.
        squared euclidean distance).
        
    min or max (or both) is finite.
    '''
    
    def __init__(self, *args, **kwargs):
        raise Exception('This is an interface, for use in documentation only. Do not reference it in code')
    
def assert_satisfied(nutrition_target, result):
    '''
    Assert nutrition target satisfied by given nutrition (of a recipe)
    
    Parameters
    ----------
    nutrition_target : NutritionTarget
        Nutrition target to satisfy
    nutrition : pd.Series(float, columns=nutrients)
        Amount of each nutrient (in a recipe)
    '''
    nutrition_target = nutrition_target.join(result)
    
    # min
    mins = nutrition_target.dropna(subset=['min'])
    if not mins.empty:
        is_less = mins['min'] < mins['amount']
        is_close = mins[['min', 'amount']].apply(lambda row: np.isclose(*row), axis=1, raw=True)
        assert (is_less | is_close).all()
    
    # max
    maxes = nutrition_target.dropna(subset=['max'])
    if not maxes.empty:
        is_greater = maxes['max'] > maxes['amount']
        is_close = maxes[['max', 'amount']].apply(lambda row: np.isclose(*row), axis=1, raw=True)
        assert (is_greater | is_close).all()

def from_config():
    '''
    Create nutrition target from config file
    '''
    from .config import target
    return create(target)
