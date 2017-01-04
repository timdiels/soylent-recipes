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
Test soylent_recipes.cluster
'''

from soylent_recipes import cluster as cluster_
import pandas as pd
import numpy as np
import attr

#TODO test Branch, Leaf

@attr.s()
class ExpectedNode(object):
    
    '''
    assert_node_equals input data class
    '''
    
    id_ = attr.ib()
    foods = attr.ib(cmp=False, hash=False)  # set of acceptable foods
    leaf_node_ids = attr.ib(cmp=False, hash=False)  # set of acceptable leaf node ids
    max_distance = attr.ib(cmp=False, hash=False)
    children = attr.ib(cmp=False, hash=False)

def assert_node_equals(actual, expected):
    '''
    Recursively check whether nodes truly equal
    
    Parameters
    ----------
    actual : soylent_recipes.cluster.Node
    expected : ExpectedNode
    expected_nodes : {id : int => ExpectedNode}
    '''
    # id_
    assert actual.id_ == expected.id_
    
    # leaf_node
    assert actual.leaf_node.id_ in expected.leaf_node_ids
    
    # food
    assert any(actual.food.equals(food) for food in expected.foods), '\nActual:\n{}\n\nExpected one of:\n{}\n'.format(actual.food, expected.foods)
    
    # max_distance
    np.testing.assert_approx_equal(actual.max_distance, expected.max_distance)
    
    # children
    children = {child.id_: child for child in actual.children}
    expected_children = {child.id_: child for child in expected.children}
    assert children.keys() == expected_children.keys()
    for id_ in children.keys():
        assert_node_equals(children[id_], expected_children[id_])

def test_convert_cluster():
    foods = pd.DataFrame(
        [
            [1, 2],  # 0
            [3, 4],  # 1
            [5, 7],  # 2
            [6, 8],  # 3
            [1, 0],  # 4
        ],
        index=['food0', 'food1', 'food2', 'food3', 'food4'],
        columns=['nutr0', 'nutr1'],
        dtype=float
    )
    
    distances = np.array([
        [0, 8, 4, 8, 9],
        [0, 0, 4, 2, 8],
        [0, 0, 0, 4, 4],
        [0, 0, 0, 0, 8],
        [0, 0, 0, 0, 0]
    ], dtype=float)
    distances += distances.transpose()  # make symmetric
    
    children = np.array([
        [1, 3],  # 5
        [2, 0],  # 6
        [6, 5],  # 7
        [7, 4],  # 8
    ])
    
    expected = (
        ExpectedNode(id_=8, foods=[foods.iloc[2]], leaf_node_ids=[2], max_distance=9.0, children=(
            ExpectedNode(id_=4, foods=[foods.iloc[4]], leaf_node_ids=[4], max_distance=0.0, children=()),
            ExpectedNode(id_=7, foods=[foods.iloc[2]], leaf_node_ids=[2], max_distance=8.0, children=(
                ExpectedNode(id_=6, foods=[foods.iloc[0], foods.iloc[2]], leaf_node_ids=[0, 2], max_distance=4.0, children=(
                    ExpectedNode(id_=0, foods=[foods.iloc[0]], leaf_node_ids=[0], max_distance=0.0, children=()),
                    ExpectedNode(id_=2, foods=[foods.iloc[2]], leaf_node_ids=[2], max_distance=0.0, children=())
                )),
                ExpectedNode(id_=5, foods=[foods.iloc[1], foods.iloc[3]], leaf_node_ids=[1, 3], max_distance=2.0, children=(
                    ExpectedNode(id_=1, foods=[foods.iloc[1]], leaf_node_ids=[1], max_distance=0.0, children=()),
                    ExpectedNode(id_=3, foods=[foods.iloc[3]], leaf_node_ids=[3], max_distance=0.0, children=())
                ))
            ))
        ))
    )
    
    root = cluster_._convert_clustering(foods, children, distances)
    assert_node_equals(root, expected)
