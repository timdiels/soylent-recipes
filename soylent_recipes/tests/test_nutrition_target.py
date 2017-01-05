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
    
    def SingleTarget(self, min_, max_):
        return pd.DataFrame(
            [[min_, max_]],
            index=['food0'],
            columns=['min', 'max']
        )
    
    def test_min_zero(self):
        with pytest.raises(ValueError) as ex:
            nutrition_target_.create(self.SingleTarget(0, np.nan))
        test.assert_text_contains(str(ex.value), dedent('''\
            min <= 0. Expected: min > 0 or min=NaN. Invalid rows:
            food0    0'''
        ))
            
    def test_min_negative(self):
        with pytest.raises(ValueError) as ex:
            nutrition_target_.create(self.SingleTarget(-1, np.nan))
        test.assert_text_contains(str(ex.value), dedent('''\
            min <= 0. Expected: min > 0 or min=NaN. Invalid rows:
            food0   -1'''
        ))
        
    def test_min_infinite(self):
        with pytest.raises(ValueError) as ex:
            nutrition_target_.create(self.SingleTarget(np.inf, np.nan))
        test.assert_text_contains(str(ex.value), dedent('''\
            Encountered np.inf or -np.inf. Values must be finite or NaN. Invalid rows:
                   min  max
            food0  inf  NaN'''
        ))
            
    def test_max_infinite(self):
        with pytest.raises(ValueError) as ex:
            nutrition_target_.create(self.SingleTarget(0, np.inf))
        test.assert_text_contains(str(ex.value), dedent('''\
            Encountered np.inf or -np.inf. Values must be finite or NaN. Invalid rows:
                   min  max
            food0    0  inf'''
        ))
            
    def test_max_zero(self):
        with pytest.raises(ValueError) as ex:
            nutrition_target_.create(self.SingleTarget(np.nan, 0))
        test.assert_text_contains(str(ex.value), dedent('''\
            max <= min, 0. Expected: max > min, 0 or max=NaN. Invalid rows:
                   min  max
            food0  NaN    0'''
        ))
            
    def test_max_eq_min(self):
        with pytest.raises(ValueError) as ex:
            nutrition_target_.create(self.SingleTarget(1, 1))
        test.assert_text_contains(str(ex.value), dedent('''\
            max <= min, 0. Expected: max > min, 0 or max=NaN. Invalid rows:
                   min  max
            food0    1    1'''
        ))
            
    def test_max_lt_min(self):
        with pytest.raises(ValueError) as ex:
            nutrition_target_.create(self.SingleTarget(2, 1))
        test.assert_text_contains(str(ex.value), dedent('''\
            max <= min, 0. Expected: max > min, 0 or max=NaN. Invalid rows:
                   min  max
            food0    2    1'''
        ))
            
    def test_nan_row(self):
        with pytest.raises(ValueError) as ex:
            nutrition_target_.create(self.SingleTarget(np.nan, np.nan))
        test.assert_text_contains(str(ex.value), dedent('''\
            Some rows are all NaN (when treating min=0 as min=NaN). This does not define any constraint for the nutrient. Expected: min>0 or max>min,0. Either remove the nutrient or constrain it. Invalid rows:
                   min  max
            food0  NaN  NaN'''
        ))
            
    def test_output(self):
        input_ = pd.DataFrame(
            [
                [1, 3],
                [np.nan, 2],
                [2, np.nan],
            ],
            index=['food0', 'food1', 'food2'],
            columns=['min', 'max']
        )
        expected = pd.DataFrame(
            [
                [1, 3, 2],  # pseudo-target = (min+max)/2.0 if both are finite
                [np.nan, 2, 1],  # pseudo-target = max/2.0 if only max is finite
                [2, np.nan, 2.2],  # pseudo-target = 1.1*min if only min is finite
            ],
            index=input_.index,
            columns=['min', 'max', 'pseudo_target'],
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
    test.assert_text_equals(actual.strip(), _expected_config.strip())
    
_expected_config = '''
                                                            min           max
Energy from: alpha linolenic acid                  1.050000e+04  2.100000e+04
Energy from: carbohydrate                          7.875000e+05  1.137500e+06
Energy from: fat                                   3.500000e+05  6.125000e+05
Energy from: linoleic acid                         8.750000e+04  1.750000e+05
Energy from: linoleic acid + alpha linolenic acid           NaN  1.750000e+05
Energy from: protein                               1.750000e+05  6.125000e+05
Energy from: sugars, added                                  NaN  4.375000e+05
alpha linolenic acid                               1.600000e+00           NaN
calcium                                            1.000000e+00  2.500000e+00
carbohydrate                                       1.300000e+02           NaN
carotenoids                                                 NaN  6.000000e-03
cholesterol                                                 NaN  3.000000e-01
choline                                            5.500000e-01  3.500000e+00
copper                                             9.000000e-04  1.000000e-02
energy                                             1.750000e+06  1.800000e+06
fatty acids                                                 NaN  2.000000e+01
fiber                                              3.800000e+01           NaN
fluoride                                           4.000000e-03  1.000000e-02
folate                                             4.000000e-04  1.000000e-03
folate, added                                               NaN  1.000000e-03
iron                                               8.000000e-03  4.500000e-02
linoleic acid                                      1.700000e+01           NaN
magnesium                                          4.000000e-01           NaN
manganese                                          2.300000e-03  1.100000e-02
niacin                                             1.600000e-02           NaN
pantothenic acid                                   5.000000e-03           NaN
phosphorus                                         7.000000e-01  4.000000e+00
potassium                                          4.700000e+00           NaN
protein                                            6.960000e+01           NaN
riboflavin                                         1.300000e-03           NaN
selenium                                           5.500000e-05  4.000000e-04
sodium                                             1.500000e+00  2.300000e+00
thiamin                                            1.200000e-03           NaN
vitamin a                                          9.000000e-04           NaN
vitamin a, preformed                                        NaN  3.000000e-03
vitamin b12                                        2.400000e-06           NaN
vitamin b6                                         1.300000e-03  1.000000e-01
vitamin c                                          9.000000e-02  2.000000e+00
vitamin d                                          1.500000e-05  1.000000e-04
vitamin e                                          1.500000e-02           NaN
vitamin e, added                                            NaN  1.000000e+00
vitamin k                                          1.200000e-04           NaN
water                                              3.700000e+00           NaN
zinc                                               1.100000e-02  4.000000e-02
'''

# TODO
#
# Test config validation: give invalid input, expect ValueError raised
