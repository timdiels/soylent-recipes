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
Test soylent_recipes.nutrition_target
'''

from soylent_recipes import nutrition_target as nutrition_target_

def test_from_config():
    '''
    config module correctly transformed into a NutritionTarget
    '''
    # Note: will want to replace with from_config(test_config) to isolate from
    # real config changes (or rather actual config should not be part of
    # package)
    nutrition_target = nutrition_target_.from_config()
    expected = nutrition_target_.NutritionTarget(
        minima={
            'alpha linolenic acid': 1.6,
            'manganese': 0.0023,
            'choline': 0.55,
            'vitamin e, added': 0.0,
            'vitamin b12': 2.4e-06,
            'calcium': 1.0,
            'fiber': 38.0,
            'fluoride': 0.004,
            'phosphorus': 0.7,
            'folate, added': 0.0,
            'linoleic acid': 17.0,
            'selenium': 5.5e-05,
            'zinc': 0.011,
            'vitamin a, preformed': 0.0,
            'potassium': 4.7,
            'folate': 0.0004,
            'magnesium': 0.4,
            'copper': 0.0009,
            'carbohydrate': 130.0,
            'protein': 69.60000000000001,
            'energy': 1750000.0,
            'vitamin d': 1.5e-05,
            'vitamin b6': 0.0013,
            'water': 3.7,
            'cholesterol': 0.0,
            'niacin': 0.016,
            'riboflavin': 0.0013,
            'sodium': 1.5,
            'iron': 0.008,
            'vitamin a': 0.0009,
            'vitamin e': 0.015,
            'thiamin': 0.0012,
            'pantothenic acid': 0.005,
            'vitamin c': 0.09,
            'vitamin k': 0.00012,
            'carotenoids': 0.0,
            'fatty acids': 0.0,
            'Energy from: linoleic acid + alpha linolenic acid': 0.0,
            'Energy from: alpha linolenic acid': 10500.0,
            'Energy from: fat': 350000.0,
            'Energy from: carbohydrate': 787500.0,
            'Energy from: protein': 175000.0,
            'Energy from: sugars, added': 0.0,
            'Energy from: linoleic acid': 87500.0,
        },
        maxima={
            'zinc': 0.04,
            'manganese': 0.011,
            'choline': 3.5,
            'iron': 0.045,
            'energy': 1800000.0,
            'vitamin b6': 0.1,
            'vitamin e, added': 1.0,
            'cholesterol': 0.3,
            'calcium': 2.5,
            'sodium': 2.3,
            'fluoride': 0.01,
            'phosphorus': 4,
            'vitamin d': 0.0001,
            'folate, added': 0.001,
            'selenium': 0.0004,
            'copper': 0.01,
            'vitamin a, preformed': 0.003,
            'vitamin c': 2.0,
            'folate': 0.001,
            'Energy from: linoleic acid + alpha linolenic acid': 175000.0,
            'Energy from: alpha linolenic acid': 21000.0,
            'Energy from: fat': 612500.0,
            'Energy from: carbohydrate': 1137500.0,
            'Energy from: protein': 612500.0,
            'Energy from: sugars, added': 437500.0,
            'Energy from: linoleic acid': 175000.0,
        },
        targets={
        },
        minimize={'fatty acids': 1.0, 'cholesterol': 1.0, 'carotenoids': 1.0},
    )
    assert nutrition_target.minima == expected.minima
    assert nutrition_target.maxima == expected.maxima
    assert nutrition_target.targets == expected.targets
    assert nutrition_target.minimize == expected.minimize

# TODO
#
# Test config validation: give invalid input, expect ValueError raised
