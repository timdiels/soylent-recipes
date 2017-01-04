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
Clustering functions
'''

from chicken_turtle_util import series as series_
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import pairwise_distances
import numpy as np
import logging

_logger = logging.getLogger(__name__)

# Note: might squeeze out some performance by only using lower/upper triangle of `distances`.

def agglomerative_euclidean(foods):
    _logger.info('Clustering foods using agglomerative_euclidean')
    
    # Note: there is no squared euclidean
    # Note: n_clusters has no effect on clustering.children_, so we don't use it
    distances = pairwise_distances(foods.values, metric='euclidean')
    foods, distances = _remove_duplicate_foods(foods, distances)
    clustering = AgglomerativeClustering(linkage='complete', affinity='precomputed', compute_full_tree=True)
    clustering.fit(distances)
    return _convert_clustering(foods, clustering.children_, distances)  # we assume children_ are such that row i only references node ids < i+len(foods)

def _remove_duplicate_foods(foods, distances):
    '''
    Remove duplicate foods (keeping one of each group of duplicates)
    '''
    mask = distances == 0.0
    mask[np.tril_indices_from(mask)] = False  # only consider upper triangle
    mask = mask.any(axis=0)  # collapse rows, now we have a row vector, a mask of foods to remove
    mask = ~mask  # mask of foods to keep
    foods = foods[mask]
    distances = distances[np.ix_(mask, mask)]
    assert len(foods) == len(distances)  # sanity check
    assert distances.shape[0] == distances.shape[1]  # sanity check
    return foods, distances
    
    
def _convert_clustering(foods, children, distances):
    '''
    Convert hierarchical clustering to Node representation
    
    Parameters
    ----------
    foods : pd.DataFrame
        The foods that were clustered.
    children : expr(sklearn.cluster.AgglomerativeClustering.children_)
        Clustering hierarchy as 2D array of children. Each row i may only
        reference node ids < i+len(foods).
    distances : np.array(shape=(len(foods), len(foods)))
        Distance matrix. distances[i,j] is distance between i-th and j-th food.
        
    Returns
    -------
    Node
        Root node
    '''
    # Leaf and branch nodes
    # nodes[i] corresponds to foods.iloc[i] and distances[i] for i < len(foods)
    nodes = np.empty(len(foods) + len(children), dtype=object)
    
    # Add leaf nodes
    for id_, (_, food) in enumerate(foods.iterrows()):
        nodes[id_] = Leaf(id_, food)
        
    # Add branch nodes
    _add_branch_nodes(nodes, children, distances)
    
    # Get root
    root = nodes[-1]
    
    return root

def _add_branch_nodes(nodes, children, distances):
    def _leaf_ids(nodes):
        '''
        Get the id of each leaf descendant of nodes (inclusive)
        '''
        leafs = []
        for node in nodes:
            if not node.children:
                leafs.append(node.id_)
            else:
                leafs.extend(_leaf_ids(node.children))
        return leafs
        
    # Add nodes
    food_count = len(distances)
    for id_, children_ in enumerate(children):
        # Get id_
        id_ += food_count
        
        # Get children_
        children_ = [nodes[j] for j in children_]
        
        # Get max distance
        leaf_ids = _leaf_ids(children_)
        leaf_distances = distances[np.ix_(leaf_ids, leaf_ids)]
        max_distance = leaf_distances.max()  # Note: np.triu_indices_from(arr) might be faster by checking only half a square 
        
        # Get leaf_node: the leaf with the least max distance to other leafs
        leaf_id = leaf_ids[leaf_distances.max(axis=1).argmin()]
        leaf_node = nodes[leaf_id]
        
        # Create branch
        nodes[id_] = Branch(id_, leaf_node, max_distance, children_)

class Node(object):
    
    '''
    Node of a hierarchical clustering
    
    This documents the Node interface, do not instantiate, use Leaf and/or
    Branch instead.
    
    All attributes are read-only. Hash and equality are by id.
    
    Attributes
    ----------
    id_ : int
        Unique node id
    food : pd.Series
        The food that the the node represents (best). If a branch, this is the
        the food nearest to its average food; a branch actually represents
        multiple foods.
    leaf_node : Node
        Leaf node to which self.food belongs. This is a descendant of the
        current node if a branch node and self otherwise.
    max_distance : float
        Least upper bound to the distance between any 2 foods in the cluster. 0
        iff leaf.
    children : tuple(Node)
        Children of the node. Empty if is_leaf.
    is_leaf : bool
        True iff is leaf node, i.e. iff self.children
    '''
    
class Branch(object):  # No inherit from Node as inheritance is evil, a circular dependency.
    
    '''
    Branch node
    
    See Node for attributes.
    
    Parameters
    ----------
    id_ : int
        Unique node id
    leaf_node : Node
        Leaf node which best represents the node. This is a descendant of the
        current node.
    max_distance : float
        Least upper bound to the distance between any 2 foods in the cluster. 0
        iff leaf.
    children : iterable(Node)
        Children of the node. Empty if is_leaf.
    '''
    
    def __init__(self, id_, leaf_node, max_distance, children):
        # Validate ...
        _validate_not_none('id_', id_)
        _validate_not_none('leaf_node', leaf_node)
        if not (max_distance > 0.0):
            raise ValueError('max_distance should be > 0.0. Got {!r}'.format(max_distance))
        
        # Validate children
        children_ = children
        children = tuple(children)
        if not children:
            raise ValueError('children must not be empty or None. Got: {!r}'.format(children_))
        for child in children:
            if child is None:
                raise ValueError('`children` contains a None value, this is not allowed. children={!r}'.format(children_))
        
        # Set self
        self._id = id_
        self._leaf_node = leaf_node
        self._max_distance = float(max_distance)
        self._children = children
        
    @property
    def id_(self):
        return self._id
    
    @property
    def food(self):
        return self._leaf_node.food
    
    @property
    def leaf_node(self):
        return self._leaf_node
    
    @property
    def max_distance(self):
        return self._max_distance
    
    @property
    def children(self):
        return self._children
    
    @property
    def is_leaf(self):
        return False
    
    def __repr__(self):
        return (
            'Branch(id_={!r}, food={!r}, max_distance={!r}, children={!r})'
            .format(self.id_, self.food.name, self.max_distance, self.children)
        )
        
    def __eq__(self, other):
        return other is not None and self.id_ == other.id_
    
    def __hash__(self):
        return hash(self.id_)
        
class Leaf(object):
    
    '''
    Leaf node
    
    See Node for attributes.
    
    Parameters
    ----------
    id_ : int
        Unique node id
    food : pd.Series
        The food that the node represents.
    '''
    
    def __init__(self, id_, food):
        # Validate
        _validate_not_none('id_', id_)
        _validate_not_none('food', food)
        
        # Set self
        self._id = id_
        self._food = food.copy()
        
    @property
    def id_(self):
        return self._id
    
    @property
    def food(self):
        return self._food
    
    @property
    def leaf_node(self):
        return self
    
    @property
    def max_distance(self):
        return 0.0
    
    @property
    def children(self):
        return ()
    
    @property
    def is_leaf(self):
        return True
    
    def __repr__(self):
        return (
            'Leaf(id_={!r}, food={!r})'
            .format(self.id_, self.food.name)
        )
        
    def __eq__(self, other):
        return other is not None and self.id_ == other.id_
    
    def __hash__(self):
        return hash(self.id_)

def _validate_not_none(attribute, value):
    if value is None:
        raise ValueError("{} musn't be None".format(attribute))