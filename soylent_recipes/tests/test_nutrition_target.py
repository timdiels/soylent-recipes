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

from chicken_turtle_util import data_frame as df_, test
from soylent_recipes import nutrition_target as nutrition_target_
from textwrap import dedent
import numpy as np
import pandas as pd
import pytest

class TestCreate(object):
    
    def SingleTarget(self, min_, max_, minimize_weight):
        return pd.DataFrame(
            [[min_, max_, minimize_weight]],
            index=['food0'],
            columns=['min', 'max', 'minimize_weight']
        )
    
    def test_min_zero(self):
        with pytest.raises(ValueError) as ex:
            nutrition_target_.create(self.SingleTarget(0, np.nan, np.nan))
        test.assert_text_contains(str(ex.value), dedent('''\
            min <= 0. Expected: min > 0 or min=NaN. Invalid rows:
            food0    0'''
        ))
            
    def test_min_negative(self):
        with pytest.raises(ValueError) as ex:
            nutrition_target_.create(self.SingleTarget(-1, np.nan, np.nan))
        test.assert_text_contains(str(ex.value), dedent('''\
            min <= 0. Expected: min > 0 or min=NaN. Invalid rows:
            food0   -1'''
        ))
        
    def test_min_infinite(self):
        with pytest.raises(ValueError) as ex:
            nutrition_target_.create(self.SingleTarget(np.inf, np.nan, np.nan))
        test.assert_text_contains(str(ex.value), dedent('''\
            Encountered np.inf or -np.inf. Values must be finite or NaN. Invalid rows:
                   min  max  minimize_weight
            food0  inf  NaN              NaN'''
        ))
            
    def test_max_infinite(self):
        with pytest.raises(ValueError) as ex:
            nutrition_target_.create(self.SingleTarget(0, np.inf, np.nan))
        test.assert_text_contains(str(ex.value), dedent('''\
            Encountered np.inf or -np.inf. Values must be finite or NaN. Invalid rows:
                   min  max  minimize_weight
            food0    0  inf              NaN'''
        ))
            
    def test_max_zero(self):
        with pytest.raises(ValueError) as ex:
            nutrition_target_.create(self.SingleTarget(np.nan, 0, np.nan))
        test.assert_text_contains(str(ex.value), dedent('''\
            max <= min, 0. Expected: max > min, 0 or max=NaN. Invalid rows:
                   min  max
            food0  NaN    0'''
        ))
            
    def test_max_eq_min(self):
        with pytest.raises(ValueError) as ex:
            nutrition_target_.create(self.SingleTarget(1, 1, np.nan))
        test.assert_text_contains(str(ex.value), dedent('''\
            max <= min, 0. Expected: max > min, 0 or max=NaN. Invalid rows:
                   min  max
            food0    1    1'''
        ))
            
    def test_max_lt_min(self):
        with pytest.raises(ValueError) as ex:
            nutrition_target_.create(self.SingleTarget(2, 1, np.nan))
        test.assert_text_contains(str(ex.value), dedent('''\
            max <= min, 0. Expected: max > min, 0 or max=NaN. Invalid rows:
                   min  max
            food0    2    1'''
        ))
            
    def test_minimize_weight_negative(self):
        with pytest.raises(ValueError) as ex:
            nutrition_target_.create(self.SingleTarget(np.nan, np.nan, -1))
        test.assert_text_contains(str(ex.value), dedent('''\
            minimize_weight <= 0. Expected: minimize_weight > 0 or =NaN. Invalid rows:
            food0   -1'''
        ))
            
    def test_minimize_weight_infinite(self):
        with pytest.raises(ValueError) as ex:
            nutrition_target_.create(self.SingleTarget(np.nan, np.nan, np.inf))
        test.assert_text_contains(str(ex.value), dedent('''\
            Encountered np.inf or -np.inf. Values must be finite or NaN. Invalid rows:
                   min  max  minimize_weight
            food0  NaN  NaN              inf'''
        ))
            
    def test_minimize_weight_zero(self):
        with pytest.raises(ValueError) as ex:
            nutrition_target_.create(self.SingleTarget(np.nan, np.nan, 0))
        test.assert_text_contains(str(ex.value), dedent('''\
            minimize_weight <= 0. Expected: minimize_weight > 0 or =NaN. Invalid rows:
            food0    0'''
        ))
            
    def test_nan_row(self):
        with pytest.raises(ValueError) as ex:
            nutrition_target_.create(self.SingleTarget(np.nan, np.nan, np.nan))
        test.assert_text_contains(str(ex.value), dedent('''\
            Some rows are all NaN (when treating min=0 as min=NaN). This does not define any constraint or target for the nutrient. Expected: min>0 or max>min,0 or minimize_weight>0. Invalid rows:
                   min  max  minimize_weight
            food0  NaN  NaN              NaN'''
        ))
            
    def test_extrema_and_minimize_weight_mutually_exclusive(self):
        cases = (
            ((1, np.nan, 1), 'food0    1  NaN                1'),
            ((np.nan, 1, 1), 'food0  NaN    1                1')
        )
        for args, line in cases:
            with pytest.raises(ValueError) as ex:
                nutrition_target_.create(self.SingleTarget(*args))
            test.assert_text_contains(str(ex.value), dedent('''\
                Both extrema (min, max) and minimize_weight are given. Extrema an minimize_weight are mutually exclusive; not supported. Expected: minimize_weight=nan iff (min>0 or max is finite). Invalid rows:
                       min  max  minimize_weight
                {}'''
                .format(line)
            ))
    
    def test_output(self):
        input_ = pd.DataFrame(
            [
                [1, 3, np.nan],
                [np.nan, 2, np.nan],
                [2, np.nan, np.nan],
                [np.nan, np.nan, 1],
                [np.nan, np.nan, 2],
            ],
            index=['food0', 'food1', 'food2', 'food3', 'food4'],
            columns=['min', 'max', 'minimize_weight']
        )
        expected = pd.DataFrame(
            [
                [1, 3, np.nan, 2],  # pseudo-target = (min+max)/2.0 if both are finite
                [np.nan, 2, np.nan, 1],  # pseudo-target = max/2.0 if only max is finite
                [2, np.nan, np.nan, 2.2],  # pseudo-target = 1.1*min if only min is finite
                [np.nan, np.nan, 1/3.0, np.nan],  # pseudo-target = nan if no extrema.
                [np.nan, np.nan, 2/3.0, np.nan],  # and minimize_weight sums to 1
            ],
            index=input_.index,
            columns=['min', 'max', 'minimize_weight', 'pseudo_target'],
            dtype=float
        )
        original = input_.copy()
        actual = nutrition_target_.create(input_)
        df_.assert_equals(input_, original)  # don't mutate input
        df_.assert_equals(actual, expected, all_close=True)  # correct output

def test_from_config():
    '''
    Test from_config and config.py
    '''
    # Record-playback styled test. Whenever you expect changes, run
    # print(actual), manually verify and paste in _expected_config.
    
    actual = nutrition_target_.from_config()
    del actual['pseudo_target']
    actual = actual.sort_index()
    actual = actual.to_string()
    print(actual)
    test.assert_text_equals(actual.strip(), _expected_config.strip())
    
_expected_config = '''
                                                            min           max  minimize_weight
Energy from: alpha linolenic acid                  1.050000e+04  2.100000e+04              NaN
Energy from: carbohydrate                          7.875000e+05  1.137500e+06              NaN
Energy from: fat                                   3.500000e+05  6.125000e+05              NaN
Energy from: linoleic acid                         8.750000e+04  1.750000e+05              NaN
Energy from: linoleic acid + alpha linolenic acid           NaN  1.750000e+05              NaN
Energy from: protein                               1.750000e+05  6.125000e+05              NaN
Energy from: sugars, added                                  NaN  4.375000e+05              NaN
alpha linolenic acid                               1.600000e+00           NaN              NaN
calcium                                            1.000000e+00  2.500000e+00              NaN
carbohydrate                                       1.300000e+02           NaN              NaN
carotenoids                                                 NaN           NaN         0.999539
cholesterol                                                 NaN  3.000000e-01              NaN
choline                                            5.500000e-01  3.500000e+00              NaN
copper                                             9.000000e-04  1.000000e-02              NaN
energy                                             1.750000e+06  1.800000e+06              NaN
fatty acids                                                 NaN           NaN         0.000461
fiber                                              3.800000e+01           NaN              NaN
fluoride                                           4.000000e-03  1.000000e-02              NaN
folate                                             4.000000e-04  1.000000e-03              NaN
folate, added                                               NaN  1.000000e-03              NaN
iron                                               8.000000e-03  4.500000e-02              NaN
linoleic acid                                      1.700000e+01           NaN              NaN
magnesium                                          4.000000e-01           NaN              NaN
manganese                                          2.300000e-03  1.100000e-02              NaN
niacin                                             1.600000e-02           NaN              NaN
pantothenic acid                                   5.000000e-03           NaN              NaN
phosphorus                                         7.000000e-01  4.000000e+00              NaN
potassium                                          4.700000e+00           NaN              NaN
protein                                            6.960000e+01           NaN              NaN
riboflavin                                         1.300000e-03           NaN              NaN
selenium                                           5.500000e-05  4.000000e-04              NaN
sodium                                             1.500000e+00  2.300000e+00              NaN
thiamin                                            1.200000e-03           NaN              NaN
vitamin a                                          9.000000e-04           NaN              NaN
vitamin a, preformed                                        NaN  3.000000e-03              NaN
vitamin b12                                        2.400000e-06           NaN              NaN
vitamin b6                                         1.300000e-03  1.000000e-01              NaN
vitamin c                                          9.000000e-02  2.000000e+00              NaN
vitamin d                                          1.500000e-05  1.000000e-04              NaN
vitamin e                                          1.500000e-02           NaN              NaN
vitamin e, added                                            NaN  1.000000e+00              NaN
vitamin k                                          1.200000e-04           NaN              NaN
water                                              3.700000e+00           NaN              NaN
zinc                                               1.100000e-02  4.000000e-02              NaN
'''

# TODO
#
# Test config validation: give invalid input, expect ValueError raised
