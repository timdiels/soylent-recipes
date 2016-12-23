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
import attr
import logging

_logger = logging.getLogger(__name__)

def agglomerative_euclidean(foods):
    _logger.info('Clustering foods using agglomerative_euclidean')
    
    # Note: there is no squared euclidean
    # Note: n_clusters has no effect on clustering.children_, so we don't use it
    distances = pairwise_distances(foods.values, metric='euclidean')
    clustering = AgglomerativeClustering(linkage='complete', affinity='precomputed', compute_full_tree=True)
    clustering.fit(distances)
    return _convert_clustering(foods, clustering.children_, distances)  # we assume children_ are such that row i only references node ids < i+len(foods)
    
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
        nodes[id_] = Node(id_, representative=food, max_distance=0.0, children=())
        
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
        
        # Get representative: the representative of the leaf with the least max distance to other leafs
        representative_leaf_id = leaf_ids[leaf_distances.max(axis=1).argmin()]
        representative = nodes[representative_leaf_id].representative
        
        # Create Node
        nodes[id_] = Node(id_, representative, max_distance, children=children_)

def _validate_not_none(self, attribute, value):
    if value is None:
        raise ValueError("{} musn't be None".format(attribute.name))
    
def _validate_float_positive(self, attribute, value):
    if not (value >= 0.0):
        raise ValueError('{} should be >= 0.0. Instead got {!r}'.format(attribute.name, value))
    
def _validate_children(self, attribute, value):
    for child in value:
        if child is None:
            raise ValueError('`children` contains a None value, this is not allowed. children={!r}'.format(value))
    _validate_not_none(self, attribute, value)
    
@attr.s(frozen=True, repr=False)  # Note: slots=True might improve performance
class Node(object):
    
    '''
    Node of a hierarchical clustering
    
    Parameters
    ----------
    id_ : int
        Unique node id
    representative : pd.Series
        Food that represents the cluster. This is an actual food, e.g. the food
        nearest to the center, not some made-up food such as the average of all
        foods. If None, derive from children.
    max_distance : float
        Least upper bound to the distance between any 2 foods in the cluster. If
        None, derive from children.
    children : iterable(Node)
        Children of the cluster.
        
    Attributes
    ----------
    children : tuple(Node)
    representative : pd.Series
    max_distance : float
    '''
    
    id_ = attr.ib(validator=_validate_not_none)
    representative = attr.ib(validator=_validate_not_none, cmp=False, hash=False)
    max_distance = attr.ib(validator=_validate_float_positive, convert=float, cmp=False, hash=False)
    children = attr.ib(validator=_validate_children, convert=tuple, cmp=False, hash=False)
    
    @property
    def is_leaf(self):
        return not self.children
    
    def __repr__(self):
        return 'Node(id_={!r}, representative={!r}, max_distance={!r}, children={!r})'.format(self.id_, self.representative.name, self.max_distance, self.children)
        
    def assert_equals(self, other):
        '''
        For debugging, recursively check whether truly equal to other node
        
        Parameters
        ----------
        other : _Node
        '''
        # id_
        assert self.id_ == other.id_
        
        # representative
        for representative in other.representatives:
            try:
                series_.assert_equals(self.representative, representative)
                break
            except AssertionError:
                pass
        else:
            raise
        
        # max_distance
        np.testing.assert_approx_equal(self.max_distance, other.max_distance)
        
        # children
        children = {child.id_: child for child in self.children}
        other_children = {child.id_: child for child in other.children}
        assert children.keys() == other_children.keys()
        for id_ in children.keys():
            children[id_].assert_equals(other_children[id_])
