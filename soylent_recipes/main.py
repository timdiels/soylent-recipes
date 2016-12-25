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
from pathlib import Path
from chicken_turtle_util import click as click_, logging as logging_
import click
from soylent_recipes import __version__
from soylent_recipes import nutrition_target as nutrition_target_, foods as foods_, miner, cluster as cluster_, tree
import asyncio
import signal

_logger = logging.getLogger(__name__)

@click.command(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(version=__version__)
@click_.option('--usda-data', 'usda_directory', type=click.Path(exists=True, file_okay=False), help='USDA data directory to mine')
def main(usda_directory):
    '''
    To run, e.g.: soylent --usda-data data/usda_nutrient_db_sr28
    '''
    logging_.configure('soylent.log')
    logging.getLogger().setLevel(logging.DEBUG)
    _logger.info('Hi!!! This is version none!')
    nutrition_target = nutrition_target_.from_config()
    foods = foods_.import_usda(Path(usda_directory))
    foods = handle_nans(foods, nutrition_target, 10)
    foods = add_energy_components(foods)
    foods = as_floats(foods)
    foods = foods.set_index('description')
    root_node = cluster_.agglomerative_euclidean(foods)
    tree.draw(root_node)
    mine(root_node, nutrition_target)

# TODO not hardcoding conversion factors could easily be achieved by moving this to config.py 
# Conversion factors (cal/g) to default to when NaN on a food
# {factor_name :: str => (conversion_factor :: float, nutrient :: str)}
_conversion_factors = {
    'protein': 4e3,
    'carbohydrate': 4e3,
    'fat': 9e3,
    'sugars, added': 3.95e3,  # according to https://www.ars.usda.gov/ARSUserFiles/80400525/Data/Classics/ah74.pdf
        
    # Source of factor:
    # - Both these fatty acids have 18 carbon, making them a long-chain fatty acid (https://en.wikipedia.org/wiki/Fatty_acid#Length_of_free_fatty_acid_chains)
    # - conversion factor for long-chain fatty acids is found here https://books.google.be/books?id=kwzrBwAAQBAJ&pg=PA265&lpg=PA265&dq=long-chain+fatty+acids+cal/g&source=bl&ots=SEUxiMtqkd&sig=bP98Jz4NwkHJNEx48aKuhYTlDTY&hl=en&sa=X&ved=0ahUKEwiNm4G7-v_PAhXJDcAKHXwiDzgQ6AEIJjAB#v=onepage&q=long-chain%20fatty%20acids%20cal%2Fg&f=false
    'linoleic acid': 9e3,
    'alpha linolenic acid': 9e3,
    'linoleic acid + alpha linolenic acid': 9e3,
}
_conversion_factors = {'Conversion factor: {}'.format(nutrient): (value, nutrient) for nutrient, value in _conversion_factors.items()}

def handle_nans(foods, nutrition_target, risky_fill_count):
    '''
    Handle NaN values in foods
    
    Parameters
    ----------
    foods : pd.DataFrame
    nutrition_target : soylent_recipes.nutrition_target.NutritionTarget
    risky_fill_count : int
        Number of nutrients to fillna(0) despite them having a max or are
        required to be minimized according to the nutrition target.
    '''
    original_food_count = len(foods)
    
    # Fillna conversion factors
    for factor, (value, _) in _conversion_factors.items():
        if factor in foods:
            count = foods[factor].isnull().sum()
            foods[factor] = foods[factor].fillna(value)
            _logger.info('Filled {} NaNs with {} (average across foods as derived by "Agriculture Handbook 74") in {}'.format(count, value, factor))
        else:
            foods[factor] = value
        
    #
    _logger.debug('Non-null value counts by column:\n{}'.format(foods.count().to_string()))
        
    # Fillna(0) for harmless nutrients
    nutrients = set(foods.columns) - {'description'} - _conversion_factors.keys()
    for nutrient in nutrients:
        if nutrient not in nutrition_target.maxima and nutrient not in nutrition_target.minimize and nutrient not in nutrition_target.targets:
            count = foods[nutrient].isnull().sum()
            if count:
                foods[nutrient] = foods[nutrient].fillna(0)
                _logger.info('Filled {} NaNs with 0 in {} (harmless)'.format(count, nutrient))
    _logger.debug('Non-null counts now are:\n{}'.format(foods.count().to_string()))
    
    # Fillna(0) for the most NaN ridden nutrients
    for nutrient, count in foods.isnull().sum().sort_values(ascending=False).iloc[:risky_fill_count].iteritems():
        foods[nutrient] = foods[nutrient].fillna(0)
        _logger.warning('Filled {} NaNs with 0 in {} (may cause resulting recipes to exceed the nutrient target)'.format(count, nutrient))
    _logger.debug('Non-null counts now are:\n{}'.format(foods.count().to_string()))
    
    # Drop rows with unknown values. With even a single unknown value we can no
    # longer guarantee meeting the nutrition target (provided the mapping is
    # minimal with respect to the nutrition target)
    dropped_foods = foods[foods.isnull().any(axis=1)]
    foods = foods.dropna()
    
    _logger.info('{} out of {} foods remain after dropping foods with (still) incomplete nutrition data'.format(len(foods), original_food_count))
    _logger.debug('Dropped foods:\n{}'.format(dropped_foods['description'].sort_values().to_string(index=False)))
    _logger.debug('Kept foods:\n{}'.format(foods['description'].sort_values().to_string(index=False)))
    
    return foods

def add_energy_components(foods):
    '''
    Replace 'Conversion factor:' columns with 'Energy from:' columns
    
    E.g. 'Energy from: protein' is the amount of calories per gram of food
    coming from protein.
    '''
    # Add energy components
    for factor, (_, nutrient) in _conversion_factors.items():
        foods['Energy from: {}'.format(nutrient)] = foods[nutrient] * foods[factor]
        
    # Drop conversion factors
    foods = foods.drop(_conversion_factors, axis=1)
    
    return foods

def as_floats(foods):
    '''
    Change dtype of numeric columns to float (in-place)
    '''
    # make foods as floaty as possible
    mask = foods.columns != 'description'
    foods.loc[:,mask] = foods.loc[:,mask].astype(float)
    return foods

def mine(root_node, nutrition_target):
    loop = asyncio.get_event_loop()
    k = 100
    top_recipes = miner.TopK(k)
    def cancel():
        # Note: cancelling an executor does not cancel the thread running inside
        _logger.info('Cancelling')
        miner.cancel = True
    loop.add_signal_handler(signal.SIGHUP, cancel)
    loop.add_signal_handler(signal.SIGINT, cancel)
    loop.add_signal_handler(signal.SIGTERM, cancel)
    
    loop.run_until_complete(loop.run_in_executor(None, miner.mine, root_node, nutrition_target, top_recipes))
    loop.close()
    
    # Print top k long format
    def format_recipe(recipe):
        food_names = (cluster.representative.name for cluster in recipe.clusters)
        if recipe.solved:
            lines = ('{} - {}'.format(amount, food_name) for amount, food_name in zip(recipe.amounts, food_names))
        else:
            lines = food_names
        return '{}\n{}'.format(recipe.score, '\n'.join(lines))
    with open('recipes_top_{}.txt'.format(k), 'w') as f:
        f.write(('\n' + '-'*60 + '\n').join(format_recipe(recipe) for recipe in top_recipes))
    
    # Print top k short format
    _logger.info('\n'.join(map(str, top_recipes)))
    
    # Print top k stats
    _logger.info(top_recipes.format_stats())
    