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
Nutrition target configuration file

The defaults reflect the `Dietary Reference Intake`_
recommendations. Nutrient minima are set to the RDA if available and the AI
otherwise. The maxima are set to the UL. (RDA is the lowest intake amount at
which less than 2.5% of people have adverse effects. UL is the highest amount at
which less than 2.5% of people have adverse effects. An intake in range of [RDA,
UL] is perfectly healthy (97.5% of the population sample)).

The values used are for males aged between 19 and 30 (inclusive), taken at 2016-10-26. For other
values, adjust the values using these tables
https://ods.od.nih.gov/Health_Information/Dietary_Reference_Intakes.aspx

Body weight and daily energy intake can easily be set below 

.. _dietary reference intake: https://en.wikipedia.org/wiki/Dietary_Reference_Intake 
'''

import numpy as np

# All values are in grams (g) unless otherwise listed (in a comment that follows it)

# TODO The link to the tables also has a bunch of reports we forgot to look at.
# Searching these could clear up a bunch of things (e.g. macronutrients:
# different cal/g conversion factors perhaps)


#################
# Syntactic sugar
#
# These make the config easier but they're not needed

# Body weight (kg)
_weight = 87

# Energy intake target, calculate it with
# http://www.calculator.net/calorie-calculator.html.
#
# Due to limitations of the solver, it won't aim for this target, but you can
# limit the range of accepted intakes with ``extrema['energy']``. Further you
# can prefer either the lower or upper end of the range by adding 'energy' to
# `minimize` or `maximize` respectively.
_energy_target = 1750e3

# For each of the below nutrients, the min-max fraction it may make up of your
# energy_target. E.g. if the recipe is pure carbs, carbs will make up 100% of
# the total energy (though note you must enter values between 0 and 1 below).
# Only the below nutrients are supported (need to add calorie conversion factors
# in the code if you want more).
_energy_fractions = {
    'fat': (.20, .35),
    'protein': (.10, .35),
    'carbohydrate': (.45, .65),
    'linoleic acid': (.05, .10), 
    'alpha linolenic acid': (.006, .012),
    'linoleic acid + alpha linolenic acid': (0, .10), # Note: don't try this '+' magic with any other variables
    'sugars, added': (0, .25),
}


#########################################################################
# Required
#
# The only bits of the config that actually get used by soylent_recipes

# Extrema/bounds to set on nutrients. For each nutrient, its amount in the
# recipe needs to remain within bounds. E.g. when 'calcium' exceeds its bounds,
# the recipe is rejected.
#
# Values are in SI units. If the min or max is unknown, set it to ``np.nan``. If
# it's safe to eat any amount, think again, you never know for sure; set it to
# ``np.nan``. If it's not necessary to eat it, set ``min=0``. The range is
# inclusive, setting ``min=max`` is allowed.
#
# Minima are set to RDA or AI by default, maxima are set to UL.
extrema = {
    # Elements
    'calcium': (1000e-3, 2500e-3),
    'copper': (900e-6, 10000e-6),
    'fluoride': (4e-3, 10e-3),
    'iron': (8e-3, 45e-3),
    'magnesium': (400e-3, np.nan),
    'manganese': (2.3e-3, 11e-3),
    'phosphorus': (700e-3, 4),
    'selenium': (55e-6, 400e-6),
    'zinc': (11e-3, 40e-3),
    'potassium': (4.7, np.nan),
    'sodium': (1.5, 2.3),
    
    # Vitamins
    'vitamin a': (900e-6, np.nan),
    'vitamin a, preformed': (0, 3000e-6),
    'vitamin c': (90e-3, 2000e-3),
    'vitamin d': (15e-6, 100e-6),
    'vitamin e': (15e-3, np.nan),
    'vitamin e, added': (0, 1000e-3),
    'vitamin k': (120e-6, np.nan),
    'thiamin': (1.2e-3, np.nan),
    'riboflavin': (1.3e-3, np.nan),
    'niacin': (16e-3, np.nan),
    'vitamin b6': (1.3e-3, 100e-3),
    'folate': (400e-6, 1000e-6),
    'folate, added': (0, 1000e-6), 
    'vitamin b12': (2.4e-6, np.nan),
    'pantothenic acid': (5e-3, np.nan),
    'choline': (550e-3, 3.5), # "Although AIs have been set for choline, there are few data to assess whether a dietary supply of choline is needed at all stages of the life cycle, and it may be that the choline requirement can be met by endogenous synthesis at some of these stages."
    'carotenoids': (0, np.nan),
    
    # Water and macronutrients
    'water': (3.7, np.nan), # l. also includes water contained in food #TODO probably want to remove, trivial to achieve manually.
    'carbohydrate': (130, np.nan),
    'fiber': (38, np.nan),
    'linoleic acid': (17, np.nan),
    'alpha linolenic acid': (1.6, np.nan),
    'protein': (_weight*0.8, np.nan),
    'energy': (1750e3, 1800e3),
    'fatty acids': (0, np.nan),
    
    # Other
    'cholesterol': (0, 300e-3),
}

# Nutrients to minimize, weighted. Use a negative weight to maximize the nutrient.
# {nutrient :: str => weight : float}
# minimizes sum(weight*nutrient_in_recipe)
minimize = {
    # roughly no more than 20 g/day (source: google)
    'fatty acids': 1.0/13.0,
    
    # roughly no more than .3 g/day (source: google) 
    'cholesterol': 1.0/0.3,
    
    # foot note on carotenoids: "beta Carotene supplements are advised only to serve as a provitamin A source for individuals at risk of vitamin A deficiency."
    # roughly no more than 6e-3 g/day (source: google)
    'carotenoids': 1.0/6e-3,
}

# DRI recommendations not taken into account due to lacking any USDA nutrient data for them.
# Format: (name, min, max, unit).
#
# ('arsenic', 0, np.nan, 'g'), # not shown to be harmful, but there is no justification to add it to food
# ('silicon', 0, np.nan, 'g'), # not shown to be harmful, but there is no justification to add it to food
# ('vanadium', 0, 1.8e-3, 'g'), # not shown to be harmful, but there is no justification to add it to food
# ('boron', 0, 20e-3, 'g'),
#  
# ('chromium', 35e-6, np.nan, 'g'),
# ('iodine', 150e-6, 1100e-6, 'g'),
# ('magnesium, added', 0, 350e-3, 'g'), 
# ('molybdenum', 45e-6, 2000e-6, 'g'),
# ('nickel', 0, 1e-3, 'g'),
# ('chloride', 2.3, 3.6, 'g'),
#  
# ('niacin, added', 0, 35e-3, 'g'), #TODO could set regular niacin max to this
# ('biotin', 30e-6, np.nan, 'g'),

######################################################
# Internal
#
# Don't change this unless you know what you're doing
for nutrient, (min_, max_) in _energy_fractions.items():
    assert min_ >= 0, nutrient
    assert min_ <= max_, nutrient
    assert max_ <= 1, nutrient
    name = 'Energy from: {}'.format(nutrient)
    extrema[name] = (min_ * _energy_target, max_ * _energy_target)
