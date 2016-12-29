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
from soylent_recipes import miner

@attr.s()
class Node(object):
    
    '''
    Mock of soylent_recipes.cluster.Node
    '''
    
    id_ = attr.ib()
    representatives = attr.ib(cmp=False, hash=False)
    max_distance = attr.ib(cmp=False, hash=False)
    children = attr.ib(cmp=False, hash=False)
    
    def __repr__(self):
        return 'Node(id_={!r}, representatives={!r}, max_distance={!r}, children={!r})'.format(self.id_, [r.name for r in self.representatives], self.max_distance, self.children)
    
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
    
    __lt__ = miner.Recipe.__lt__
    __len__ = miner.Recipe.__len__
    __eq__ = miner.Recipe.__eq__
    __hash__ = miner.Recipe.__hash__