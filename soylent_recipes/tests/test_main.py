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

'''
Test soylent_recipes.main
'''

from chicken_turtle_util import data_frame as df_
from soylent_recipes import main
from .various import NutritionTarget
import pandas as pd
import numpy as np

def test_handle_nans():
    '''
    Replace NaNs with 0 for some nutrients, then drop foods which still have NaN
    values
     
    Specifically:
    
    - fill energy conversion factors (cal/g) with the generic value across
      foods. Also add missing conversion factor columns.
    - fill NaN in harmless nutrients (not appearing in maxima or minimize)
    - fill NaN for the first `risky_fill_count` other nutrients
    '''
    nutrition_target = NutritionTarget(
        [
            [1, np.nan],
            [np.nan, 3],
            [np.nan, 2],
            [np.nan, 4],
        ],
        index=('harmless1', 'harmful1', 'harmful2', 'harmful3'),
    )
    foods = pd.DataFrame(
        [
            [np.nan, np.nan, np.nan, np.nan, np.nan, 1, 2],
            [1, 2, 3, 4, 5, 6, 7],
            [1, 2, 3, 4, np.nan, np.nan, 7], # will be dropped because one too many harmful/risky NaN
        ],
        index=['food1', 'food2', 'food3'], 
        columns=(
            'Conversion factor: protein', 'Conversion factor: fat',
            'Conversion factor: carbohydrate', 'harmless1', 'harmful1', 'harmful2',
            'harmful3'
        )
    )
    original = foods.copy()
    actual = main.handle_nans(foods, nutrition_target, risky_fill_count=1)
    
    # Input untouched
    df_.assert_equals(foods, original)
    
    # Output as expected
    expected = pd.DataFrame(
        [
            [4e3, 9e3, 4e3, 0, 0, 1, 2, 3.95e3, 9e3, 9e3, 9e3],
            [1, 2, 3, 4, 5, 6, 7, 3.95e3, 9e3, 9e3, 9e3],
        ],
        index=['food1', 'food2'],
        columns=(
            'Conversion factor: protein', 'Conversion factor: fat',
            'Conversion factor: carbohydrate', 'harmless1', 'harmful1', 'harmful2',
            'harmful3',
            'Conversion factor: sugars, added',
            'Conversion factor: linoleic acid',
            'Conversion factor: alpha linolenic acid',
            'Conversion factor: linoleic acid + alpha linolenic acid',
        )
    )
    df_.assert_equals(actual, expected, ignore_order={1}, all_close=True)
    
def test_add_energy_components():
    '''
    Replace 'Conversion factor:' columns with 'Energy from:' columns using
    hardcoded conversion factors
    '''
    foods = pd.DataFrame(
        [
            [1, 2, 3, 4, 5, 6, 7, 1, 2, 3, 4, 5, 6, 7, 10],
        ],
        index=['food1'],
        columns=(
            'Conversion factor: protein',
            'Conversion factor: fat', 
            'Conversion factor: carbohydrate',
            'Conversion factor: sugars, added',
            'Conversion factor: linoleic acid',
            'Conversion factor: alpha linolenic acid',
            'Conversion factor: linoleic acid + alpha linolenic acid',
            'protein',
            'fat',
            'carbohydrate',
            'sugars, added',
            'linoleic acid',
            'alpha linolenic acid',
            'linoleic acid + alpha linolenic acid',
            'nutrient1',
        )
    )
    original = foods.copy()
    actual = main.add_energy_components(foods)
    
    # Input untouched
    df_.assert_equals(foods, original)
    
    # Output as expected
    expected = pd.DataFrame(
        [
            [1, 4, 9, 16, 25, 36, 49, 1, 2, 3, 4, 5, 6, 7, 10],
        ],
        index=['food1'],
        columns=(
            'Energy from: protein',
            'Energy from: fat', 
            'Energy from: carbohydrate',
            'Energy from: sugars, added',
            'Energy from: linoleic acid',
            'Energy from: alpha linolenic acid',
            'Energy from: linoleic acid + alpha linolenic acid',
            'protein',
            'fat',
            'carbohydrate',
            'sugars, added',
            'linoleic acid',
            'alpha linolenic acid',
            'linoleic acid + alpha linolenic acid',
            'nutrient1',
        )
    )
    df_.assert_equals(actual, expected, ignore_order={1}, all_close=True)
    
def test_normalize():
    nutrients = ('nutrient1', 'nutrient2')
    foods = pd.DataFrame(
        [
            [1, 2],
            [3, 5],
        ],
        index=('food1', 'food2'),
        columns=nutrients
    )
    nutrition_target = NutritionTarget([[1, 3], [2, 4]], index=nutrients)
    original_foods = foods.copy()
    original_nutrition_target = nutrition_target.copy()
    actual_foods, actual_nutrition_target = main.normalize(foods, nutrition_target)
    
    # Input untouched
    df_.assert_equals(foods, original_foods, all_close=True)
    df_.assert_equals(nutrition_target, original_nutrition_target, all_close=True)
    
    # actual_foods as expected
    expected = pd.DataFrame(
        [
            [0.5, 2.0/3.0],
            [1.5, 5.0/3.0],
        ],
        index=foods.index,
        columns=foods.columns
    )
    df_.assert_equals(actual_foods, expected, all_close=True)
    
    # actual_nutrition_target as expected
    expected = pd.DataFrame(
        [
            [0.5, 1.5],
            [2.0/3.0, 4.0/3.0],
        ],
        index=nutrition_target.index,
        columns=('min', 'max')
    )
    df_.assert_equals(actual_nutrition_target, expected, all_close=True)
