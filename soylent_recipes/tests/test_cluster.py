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
from . import mocks
import pandas as pd
import numpy as np

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
        mocks.Node(id_=8, representatives=[foods.iloc[2]], max_distance=9.0, children=(
            mocks.Node(id_=4, representatives=[foods.iloc[4]], max_distance=0.0, children=()),
            mocks.Node(id_=7, representatives=[foods.iloc[2]], max_distance=8.0, children=(
                mocks.Node(id_=6, representatives=[foods.iloc[0], foods.iloc[2]], max_distance=4.0, children=(
                    mocks.Node(id_=0, representatives=[foods.iloc[0]], max_distance=0.0, children=()),
                    mocks.Node(id_=2, representatives=[foods.iloc[2]], max_distance=0.0, children=())
                )),
                mocks.Node(id_=5, representatives=[foods.iloc[1], foods.iloc[3]], max_distance=2.0, children=(
                    mocks.Node(id_=1, representatives=[foods.iloc[1]], max_distance=0.0, children=()),
                    mocks.Node(id_=3, representatives=[foods.iloc[3]], max_distance=0.0, children=())
                ))
            ))
        )
    ))
    
    root = cluster_._convert_clustering(foods, children, distances)
    root.assert_equals(expected)
