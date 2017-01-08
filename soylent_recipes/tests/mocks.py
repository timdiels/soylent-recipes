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

import attr
from soylent_recipes.mining.recipes import Recipe as _Recipe

@attr.s(cmp=False, hash=False)
class Recipe(object):
    
    '''
    Mock of soylent_recipes.miner.Recipe
    '''
    
    clusters = attr.ib(default=())
    score = attr.ib(default=(False, 0.0))
    solved = attr.ib(default=False)
    amounts = attr.ib(default=None)
    next_cluster = attr.ib(default=None)
    max_distance = attr.ib(default=0.0)
    is_leaf = attr.ib(default=True)
    
    __lt__ = _Recipe.__lt__
    __len__ = _Recipe.__len__
    __eq__ = _Recipe.__eq__
    __hash__ = _Recipe.__hash__