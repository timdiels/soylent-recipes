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

import logging
import pandas as pd

_logger = logging.getLogger(__name__)

def import_usda(usda_directory):
    '''
    Import foods from USDA data files
    
    Parameters
    ----------
    usda_directory : Path
    
    Returns
    -------
    pd.DataFrame
        Index:
        
        food_id : int
            USDA food id
        
        Columns:
        
        description : str
        protein_factor, fat_factor, carbohydrate_factor : float
            Conversion factors in cal/g. Can be ``NaN``.
        {nutrient name} : float
            A column per nutrient. It's the `SI-unit` amount of the nutrient
            present in a gram of the food. E.g. `x` g of fluoride in 1g of
            sausage. Can be ``NaN``.
    '''
    csv_style = dict(
        sep='^',
        quotechar='~',
        encoding='latin1'
    )
    
    _logger.info('Loading food data')
    
    # Load nutrients
    nutrients = pd.read_csv(
        (usda_directory / 'NUTR_DEF.txt'),
        usecols=(0, 1, 3),
        names=('id', 'unit', 'name'),
        **csv_style
    )
    nutrients = nutrients[nutrients['id'] != 268]  # Energy appears twice in sr28, don't use the one with id 268
    
    # Drop unused nutrients
    used_nutrients = set.union({'Protein', 'Adjusted Protein'}, *_mapping.values())
    used_nutrients = {x for x in used_nutrients if not x.endswith(': energy')}
    nutrients = nutrients[nutrients['name'].isin(used_nutrients)]
    
    # Load food nutrient values
    nutrient_values = pd.read_csv(
        (usda_directory / 'NUT_DATA.txt'),
        usecols=(0, 1, 2),
        names=('food_id', 'nutrient_id', 'value'),
        **csv_style
    )
    
    # Merge in nutrient names
    nutrient_values = pd.merge(nutrients, nutrient_values, left_on='id', right_on='nutrient_id')
    del nutrient_values['id']
    del nutrient_values['nutrient_id']
    
    # Normalise values: transform ``value / (100 unit)`` to ``value/SI_unit``
    units = {
        'g': 1,
        'mg': 1e-3,
        'µg': 1e-6,
        'kg': 1e3,
        'l': 1,
        'cal': 1,
        'kcal': 1e3,
    }
    nutrient_values['unit'] = nutrient_values['unit'].apply(lambda x: units[x])
    nutrient_values['value'] = nutrient_values['value'] * nutrient_values['unit'] / 100
    del nutrient_values['unit']
    
    # Give each nutrient its own column
    nutrient_values = nutrient_values.pivot(index='food_id', columns='name', values='value')
    _logger.debug('Non-null value counts by USDA nutrient column:\n{}'.format(nutrient_values.count().to_string()))
    
    # Map to internal nutrient names
    for name, usda_names in _mapping.items():
        usda_names = list(usda_names)
        sub_values = nutrient_values[usda_names].dropna(how='all')
        nan_counts = sub_values.isnull().sum()
        if nan_counts.any():
            sub_values = sub_values.fillna(0)
            nan_counts = '; '.join('{} ({} filled)'.format(nutrient, count) for nutrient, count in nan_counts.iteritems())
            _logger.warning('Filled NaN values with 0 for partially NaN rows in columns {}'.format(nan_counts))
        nutrient_values[name] = sub_values.sum(axis=1)
    
    # Map special case: protein
    nutrient_values['protein'] = nutrient_values['Adjusted Protein'].fillna(nutrient_values['Protein'])
    assert nutrient_values['protein'].notnull().all()
    
    # Drop usda nutrient columns, leaving just the internal ones
    nutrient_values = nutrient_values.drop(used_nutrients, axis=1)
    nutrient_values = nutrient_values.sort_index(axis=1)
    
    # Load and merge in food descriptions
    foods = pd.read_csv(
        (usda_directory / 'FOOD_DES.txt'),
        index_col=0,
        usecols=(0, 2, 4, 11, 12, 13),
        names=('food_id', 'long_description', 'common_name', 'Conversion factor: protein', 'Conversion factor: fat', 'Conversion factor: carbohydrate'),
        **csv_style
    )
    for column in foods.columns:
        if column.startswith('Conversion factor:'):
            foods[column] *= 1e3
    foods = foods.join(nutrient_values)
    foods = foods.rename(columns={'long_description': 'description'})
    
    # description = '{long_desc} ({common_name})'
    foods['common_name'] = (' (' + foods['common_name'] + ')').fillna('')
    foods['description'] += foods['common_name']
    del foods['common_name']
    
    return foods

# Nutrient name mapping to internal names.
# Note: some mappings are special cases, not handled by `mapping`, e.g. 'protein'
_mapping = {
    # Elements
    'calcium': {'Calcium, Ca'},
    'copper': {'Copper, Cu'},
    'fluoride': {'Fluoride, F'},
    'iron': {'Iron, Fe'},
    'magnesium': {'Magnesium, Mg'},
    'manganese': {'Manganese, Mn'},
    'phosphorus': {'Phosphorus, P'},
    'selenium': {'Selenium, Se'},
    'zinc': {'Zinc, Zn'},
    'potassium': {'Potassium, K'},
    'sodium': {'Sodium, Na'},
    
    # Vitamins
    'vitamin a': {'Vitamin A, RAE'},  # Note: this includes Retinol
    'vitamin a, preformed': {'Retinol'},
    'vitamin c': {'Vitamin C, total ascorbic acid'},
    'vitamin d': {'Vitamin D (D2 + D3)'},
    'vitamin e': {'Vitamin E (alpha-tocopherol)'},
    'vitamin e, added': {'Vitamin E, added'},
    'vitamin k': {'Vitamin K (phylloquinone)'},
    'thiamin': {'Thiamin'},
    'riboflavin': {'Riboflavin'},
    'niacin': {'Niacin'},
    'vitamin b6': {'Vitamin B-6'},
    'folate': {'Folate, DFE'},
    'folate, added': {'Folic acid'},
    'pantothenic acid': {'Pantothenic acid'},
    'choline': {'Choline, total'},
    'carotenoids': {'Carotene, beta', 'Carotene, alpha', 'Cryptoxanthin, beta', 'Lycopene', 'Lutein + zeaxanthin'},
    
    # Note: though 'Vitamin B-12, added' sometimes exceeds 'Vitamin B-12'
    # slightly, the former is included in the latter, the latter being the
    # total vitamin B12 regardless of whether it was added or not. We
    # consider those slight excesses to be minor errors in the USDA data
    # files
    'vitamin b12': {'Vitamin B-12'},
    
    # Macronutrients and other
    'energy': {'Energy'},
    'water': {'Water'},
    'carbohydrate': {'Carbohydrate, by difference'},
    'fiber': {'Fiber, total dietary'},
    'fat': {'Total lipid (fat)'},
    'linoleic acid': {'18:2 undifferentiated'},
    'alpha linolenic acid': {'18:3 n-3 c,c,c (ALA)'},
    'linoleic acid + alpha linolenic acid': {'18:2 undifferentiated', '18:3 n-3 c,c,c (ALA)'},
    'cholesterol': {'Cholesterol'},
    'fatty acids': {'Fatty acids, total trans', 'Fatty acids, total saturated'},
    'sugars, added': {'Sugars, total'},  # we assume the worst by using total sugars as "[added] sugar is chemically indistinguishable from naturally-occurring sugars" https://en.wikipedia.org/wiki/Added_sugar
}
    