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
        Nutrient extrema/bounds and nutrients to minimize. Recipes with a
        nutrient exceeding its extrema are rejected entirely. Nutrients to
        minimize will be minimized within the constraints of nutrient extrema.
        Nutrient values are in SI units (i.e. g most of the time).
        
        Index: str. Nutrient name, may contain spaces.
        
        Columns:
        
        min : float
            Minimum required amount of nutrient. min > 0 or is NaN. If NaN, no
            minimum constraint is imposed on the nutrient.
        max : float
            Maximum allowed amount of nutrient. max > min, 0 or is NaN. If NaN,
            no maximum constraint is imposed on the nutrient.
        minimize_weight : float
            Minimize nutrient according to this weight. Weight > 0 or is NaN. If
            NaN, the nutrient is not minimized. The more weight relative to
            other nutrients, the more it is minimized. E.g. if nutrient1 has
            weight 1 and nutrient2 has weight 2, having 2 units of nutrient1 is
            equivalent to 1 unit of nutrient in calculating total error.
        
        Min, max form an inclusive range (though it does not matter much with floats).
        
        Either of min, max, minimize_weight is finite. Extrema and minimize_weight
        are mutually exclusive (minimize_weight is NaN iff min or max is finite).
    
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
        return pd.DataFrame(columns=('min', 'max', 'minimize_weight', 'pseudo_target'), dtype=float)
    
    # Set dtype to float
    target = target.astype(float)
    
    # Validate
    _validate(target, original)
    
    # Normalise minimize_weight to sum to 1
    target['minimize_weight'] /= target['minimize_weight'].sum()
    
    # Add pseudo targets
    def pseudo_target(row):
        if np.isnan(row['max']):
            if np.isnan(row['min']):
                return np.nan
            else:
                # *1.1 for less likelihood of undershooting the min
                return 1.1 * row['min']
        else:  # max_ is nan
            if np.isnan(row['min']):
                # *0.5 for less likelihood of overshooting the max. Not 0.9
                # as that would require far too much of something we just
                # don't want too much of
                return 0.5 * row['max']
            else:  # min > 0
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
    
    # minimize_weight > 0 or NaN
    mask = target['minimize_weight'] <= 0
    invalid_rows = original[mask]
    if not invalid_rows.empty:
        raise ValueError(
            'minimize_weight <= 0. '
            'Expected: minimize_weight > 0 or =NaN. '
            'Invalid rows:\n{}'
            .format(invalid_rows['minimize_weight'].to_string())
        )
    
    # No all NaN rows
    mask = target.isnull().all(axis=1)
    invalid_rows = original[mask]
    if not invalid_rows.empty:
        raise ValueError(
            'Some rows are all NaN (when treating min=0 as min=NaN). '
            'This does not define any constraint or target for the nutrient. Expected: min>0 or max>min,0 or minimize_weight>0. '
            'Invalid rows:\n{}'
            .format(invalid_rows.to_string())
        )
    
    # Extrema and minimize_weight mutually exclusive
    has_extrema = target[['min', 'max']].notnull().any(axis=1)
    has_minimize = target['minimize_weight'].notnull()
    mask = has_extrema & has_minimize
    invalid_rows = original[mask]
    if not invalid_rows.empty:
        raise ValueError(
            'Both extrema (min, max) and minimize_weight are given. '
            'Extrema an minimize_weight are mutually exclusive; not supported. Expected: minimize_weight=nan iff (min>0 or max is finite). '
            'Invalid rows:\n{}'
            .format(invalid_rows.to_string())
        )

class NutritionTarget(object):
    '''
    Interface: desired nutrition to achieve.
    
    This is a pd.DataFrame.
    
    Index: str. Nutrient name, may contain spaces.
    
    Columns:
    
    min : float
        Minimum required amount of nutrient. min > 0 or is NaN. If NaN, no
        minimum constraint is imposed on the nutrient.
    max : float
        Maximum allowed amount of nutrient. max > min, 0 or is NaN. If NaN,
        no maximum constraint is imposed on the nutrient.
    minimize_weight : float
        Minimize nutrient according to this weight. Weight > 0 or is NaN. If
        NaN, the nutrient is not minimized. The more weight relative to
        other nutrients, the more it is minimized. Sums to 1.
    pseudo_target : float
        Target to use instead of extrema when using a solver which does not
        support extrema/bounds constraints. In calculating error to the pseudo
        target, euclidean distance must be used (or a metric proportional to it,
        e.g. squared). NaN if min and max are NaN.
        
    Min, max form an inclusive range (though it does not matter much with floats).
    
    Either of min, max, minimize_weight is finite. Extrema and minimize_weight
    are mutually exclusive (minimize_weight is NaN iff min or max is finite).
    '''
    
    def __init__(self, *args, **kwargs):
        raise Exception('This is an interface, for use in documentation only. Do not reference it in code')
    
def assert_satisfied(nutrition_target, amounts, foods):
    '''
    Assert nutrition target satisfied by given recipe
    
    Parameters
    ----------
    nutrition_target : NutritionTarget
        Nutrition target to satisfy
    amounts : np.array(float)
        Amounts of the recipe
    foods : pd.DataFrame
        Foods of the recipe
    '''
    assert (amounts >= 0).all()
    
    result = pd.Series(amounts, index=foods.index, name='amount').dot(foods)
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
