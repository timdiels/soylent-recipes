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

from ete3 import Tree, TreeStyle
import logging

_logger = logging.getLogger(__name__)

def draw(root):
    '''
    Draw food clustering tree
    '''
    # Convert to tree
    max_depth = 7
    _logger.info('Converting clustering to tree for drawing, max depth = {}'.format(max_depth))
    tree = Tree()
    root_ = tree.add_child(name=root.representative.name)
    _add_children(root, root_, max_depth=max_depth)
    
    # Render tree to file
    file = 'clustering.pdf'
    _logger.info('Rendering tree to {}'.format(file))
    style = TreeStyle()
    style.show_leaf_name = True
    style.show_branch_length = True
    tree.render(file, tree_style=style)
    
def _add_children(parent, parent_, max_depth):
    '''
    Add node's children to tree node (recursively)
    
    Parameters
    ----------
    parent : soylent_recipes.cluster.Node
        Node whose children to convert to TreeNode and add as children to `parent_`
    parent_ : ete3.TreeNode
        Tree node corresponding to `parent`
    '''
    for child in parent.children:
        child_ = parent_.add_child(name=child.representative.name, dist=parent.max_distance - child.max_distance)
        if max_depth > 0:
            _add_children(child, child_, max_depth-1)
