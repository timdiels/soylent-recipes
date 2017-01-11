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
Test soylent_recipes.mining.top_k
'''

from soylent_recipes.mining.top_k import TopK
import pytest
import attr

@attr.s()
class Object():
    score = attr.ib()
    
    def __lt__(self): # when key isn't used, order will be all whack and bug likely gets detected
        return False
    
@pytest.fixture
def top_k():
    practically_infinite = 999999
    return TopK(k=practically_infinite, key=lambda x: x.score)

def test_k_zero():
    with pytest.raises(ValueError):
        TopK(0, key=lambda x: x)
    
def test_k_negative():
    with pytest.raises(ValueError):
        TopK(-1, key=lambda x: x)
        
def test_push_and_iter():
    '''
    Test push and iter
    '''
    # Constructed empty
    top_k = TopK(k=2, key=lambda x: x.score)
    assert set(top_k) == set()
    
    # Push adds
    object_10 = Object(10)
    assert top_k.push(object_10) is None  # and its return is the popped object if any, else None
    assert set(top_k) == {object_10}
    object_20 = Object(20)
    assert top_k.push(object_20) is None
    assert set(top_k) == {object_10, object_20}
    
    # Cannot add object already in TopK
    with pytest.raises(ValueError):
        top_k.push(object_10)
        
    # Pushing when len == k, pops the object with lowest key
    object_30 = Object(30)
    assert top_k.push(object_30) == object_10  # when push with highest key
    assert set(top_k) == {object_20, object_30}
    assert top_k.push(object_10) == object_10  # when push lowest key
    assert set(top_k) == {object_20, object_30}
    object_25 = Object(25)
    assert top_k.push(object_25) == object_20  # when push somewhere in the middle
    assert set(top_k) == {object_25, object_30}
    
def test_k1():
    '''
    When k=1, ...
    '''
    top_k = TopK(k=1, key=lambda x: x)
    top_k.push(1)
    assert set(top_k) == {1}
    top_k.push(3)
    assert set(top_k) == {3}
    top_k.push(2)
    assert set(top_k) == {3}
    assert top_k.pop() == 3
    
def test_pop(top_k):
    # Pop pops the lowest object
    object_lowest = Object(10)
    top_k.push(object_lowest)
    top_k.push(Object(20))
    assert top_k.pop() == object_lowest
    
    # regardless of order in which they are pushed
    top_k.push(object_lowest)
    assert top_k.pop() == object_lowest
    
def test_len(top_k):
    # When pushing and popping, len is correct
    assert len(top_k) == 0
    top_k.push(Object(10))
    assert len(top_k) == 1
    top_k.push(Object(20))
    assert len(top_k) == 2
    top_k.pop()
    assert len(top_k) == 1
    top_k.pop()
    assert len(top_k) == 0
    
def test_bool(top_k):
    assert not top_k
    top_k.push(Object(10))
    assert top_k
    
def test_remove():
    # Raise when removing object not present in TopK
    top_k = TopK(k=3, key=lambda x: x.score)
    object_10 = Object(10)
    with pytest.raises(ValueError):
        top_k.remove(object_10)
        
    # When remove lowest keyed object,
    object_20 = Object(20)
    object_30 = Object(30)
    top_k.push(object_10)
    top_k.push(object_20)
    top_k.push(object_30)
    top_k.remove(object_10)
    assert set(top_k) == {object_20, object_30}  # no longer appear
    assert len(top_k) == 2  # not counted by len
    assert top_k.pop() == object_20  # not returned by pop
    assert top_k.pop() == object_30
    
    # When remove middle,
    top_k.push(object_10)
    top_k.push(object_20)
    top_k.push(object_30)
    top_k.remove(object_20)
    assert set(top_k) == {object_10, object_30}  # no longer appear
    assert len(top_k) == 2  # not counted by len
    assert top_k.pop() == object_10  # not returned by pop
    assert top_k.pop() == object_30
    
    # When remove highest,
    top_k.push(object_10)
    top_k.push(object_20)
    top_k.push(object_30)
    top_k.remove(object_30)
    assert set(top_k) == {object_10, object_20}  # no longer appear
    assert len(top_k) == 2  # not counted by len
    assert top_k.pop() == object_10  # not returned by pop
    assert top_k.pop() == object_20
    
    # When exceeding top k,
    top_k.push(object_10)
    top_k.push(object_20)
    top_k.push(object_30)
    top_k.remove(object_10)  # remove lowest
    assert top_k.push(Object(40)) is None
    assert top_k.push(Object(50)) == object_20  # exceeding top k
