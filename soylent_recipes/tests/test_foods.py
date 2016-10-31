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
Test soylent_recipes.foods
'''

from chicken_turtle_util.test import assert_text_equals
from soylent_recipes import foods as foods_
from textwrap import dedent

def test_import_usda(usda_data_dir):
    '''
    Sample one food is correctly imported from USDA
    
    Meaning there should be: description, protein factor, fat factor,
    carbohydrate factor and a {internal_nutrient_name} column for each nutrient
    hardcoded in _mapping.
    '''
    foods = foods_.import_usda(usda_data_dir)
    expected = dedent('''\
        description                             Butter, salted
        Conversion factor: protein                        4270
        Conversion factor: fat                            8790
        Conversion factor: carbohydrate                   3870
        alpha linolenic acid                           0.00315
        calcium                                        0.00024
        carbohydrate                                    0.0006
        carotenoids                                   1.58e-06
        cholesterol                                    0.00215
        choline                                       0.000188
        copper                                               0
        energy                                            7170
        fat                                             0.8111
        fatty acids                                    0.54646
        fiber                                                0
        fluoride                                       2.8e-08
        folate                                           3e-08
        folate, added                                        0
        iron                                             2e-07
        linoleic acid                                  0.02728
        linoleic acid + alpha linolenic acid           0.03043
        magnesium                                        2e-05
        manganese                                            0
        niacin                                         4.2e-07
        pantothenic acid                               1.1e-06
        phosphorus                                     0.00024
        potassium                                      0.00024
        protein                                         0.0085
        riboflavin                                     3.4e-07
        selenium                                         1e-08
        sodium                                         0.00643
        sugars, added                                   0.0006
        thiamin                                          5e-08
        vitamin a                                     6.84e-06
        vitamin a, preformed                          6.71e-06
        vitamin b12                                    1.7e-09
        vitamin b6                                       3e-08
        vitamin c                                            0
        vitamin d                                            0
        vitamin e                                     2.32e-05
        vitamin e, added                                     0
        vitamin k                                        7e-08
        water                                           0.1587
        zinc                                             9e-07'''
    )
    assert_text_equals(foods.loc[1001].to_string(), expected)
