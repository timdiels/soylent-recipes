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

from chicken_turtle_util.exceptions import InvalidOperationError
import heapq

class _Item(object):
    
    '''
    Internal to TopK
    '''
    
    def __init__(self, key, object_):
        self._key = key
        self._object = object_
        self._removed = False
        
    @property
    def object_(self):
        return self._object
    
    @property
    def removed(self):
        return self._removed
    
    @removed.setter
    def removed(self, removed):
        self._removed = removed
    
    def __lt__(self, other):
        return self._key < other._key
    
    def __eq__(self, other):
        return other is not None and self._key == other._key
    
    def __repr__(self):
        return '_Item(key={!r}, object_={!r}, removed={!r})'.format(
            self._key, self.removed, self.object_
        )
    
class TopK(object):
    
    '''
    A collection of at most k objects
    
    Parameters
    ----------
    k : int
        Max objects to keep
    key : object -> comparable
        Function which returns a comparable value corresponding to the
        object by which it will be ordered in the top k
    '''
    def __init__(self, k, key):
        if k <= 0:
            raise ValueError('k must be > 0. Got: {!r}'.format(k))
        self._k = k
        self._key = key
        self._items_heap = []  # heapq of _Item
        self._items_dict = {}  # {object_ :: any => _Item}
        
    def push(self, object_):
        '''
        Push object and pop one if top k is full
        
        Formally, push and if len(self)==k: self.pop()
        
        Returns
        -------
        popped : any or None
            The popped object, if len(self) was k, else None. The popped object
            can be `object_`.
        '''
        if object_ is None:
            raise ValueError('Object to push cannot be None.')
        if object_ in self._items_dict:
            raise ValueError(
                'Object already in TopK. Cannot push again. Object: {!r}'
                .format(object_)
            )
        
        # Update heap
        item = _Item(self._key(object_), object_)
        if len(self) >= self._k:
            # Push and pop
            popped = heapq.heappushpop(self._items_heap, item)
            
            # If it's an already removed item, pop again as it doesn't count
            # towards len(self). Otherwise we'd exceed the top k
            while popped.removed:
                popped = heapq.heappop(self._items_heap)
        else:
            popped = None
            heapq.heappush(self._items_heap, item)
        pushed = popped != item
        
        # Update dict
        if pushed:
            if popped is not None:
                del self._items_dict[popped.object_]
            self._items_dict[object_] = item
        
        # Return
        return popped.object_ if popped is not None else None
    
    def pop(self):
        '''
        Pop the object with the lowest key
        '''
        if not len(self):
            raise InvalidOperationError('TopK is empty. Cannot pop as there is nothing to pop.')
        while True:
            item = heapq.heappop(self._items_heap)
            if not item.removed:
                object_ = item.object_
                del self._items_dict[object_]
                return object_
    
    def remove(self, object_):
        '''
        Remove object
        '''
        try:
            item = self._items_dict.pop(object_)
        except KeyError:
            raise ValueError('Object not found: {!r}. Could not remove.'.format(object_))
        item.removed = True
    
    def __len__(self):
        return len(self._items_dict)
    
    def __bool__(self):
        return bool(self._items_dict)
    
    def __iter__(self):
        '''
        Yield all objects in TopK (in no particular order)
        '''
        yield from (item.object_ for item in self._items_heap if not item.removed)
    