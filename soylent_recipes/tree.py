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

_rectangular_style = TreeStyle()
_rectangular_style.show_leaf_name = True
_rectangular_style.show_branch_length = True

_circular_style = TreeStyle()
_circular_style.mode = 'c'
_circular_style.show_leaf_name = True
_circular_style.show_branch_length = True
_circular_style.force_topology = True  # at full branch lengths, text becomes really tiny in circular style

_styles = {
    'rectangular': _rectangular_style,
    'circular_topology': _circular_style
}

def write(root):
    '''
    Write out food clustering tree files
    '''
    # Find tree depth
    tree_depth = _tree_depth(root)
    
    # Write at various depths
    max_depth = 2
    while max_depth < tree_depth:
        _write(root, max_depth)
        max_depth *= 2
    _write(root, tree_depth)
            
def _write(root, max_depth):
    '''
    Parameters
    ----------
    root : soylent_recipes.cluster.Node
        Root node of tree to write to files
    max_depth : int
        Length of longest path from root to leaf in drawn tree. I.e. cuts the
        actual tree short at max_depth.
    '''
    # Convert to tree
    tree = Tree()
    root_ = tree.add_child(name=root.representative.name)
    _add_children(root, root_, max_depth=max_depth-1)
    
    # Render tree to file
    for style_name, style in _styles.items():
        file = 'clustering_depth{}_{}.pdf'.format(max_depth, style_name)
        _logger.info('Writing clustering tree to file {}'.format(file))
        tree.render(file, tree_style=style)
    
def _tree_depth(node):
    '''
    Get length of longest path from node to leaf (node and leaf included)
    
    Parameters
    ----------
    node : soylent_recipes.cluster.Node
    
    Returns
    -------
    int
        Length, i.e. number of nodes in path.
    '''
    if node.children:
        return 1 + max(_tree_depth(child) for child in node.children)
    else:
        return 1

def _add_children(parent, parent_, max_depth):
    '''
    Add node's children to tree node (recursively)
    
    Parameters
    ----------
    parent : soylent_recipes.cluster.Node
        Node whose children to convert to TreeNode and add as children to `parent_`
    parent_ : ete3.TreeNode
        Tree node corresponding to `parent`
    max_depth : int
        Number of levels deep to add children. E.g. if max_depth==0, no children
        are added. E.g. if max_depth==1, children are added, but not
        grandchildren.
    '''
    if max_depth == 0:
        return
    for child in parent.children:
        child_ = parent_.add_child(name=child.representative.name, dist=parent.max_distance - child.max_distance)
        _add_children(child, child_, max_depth-1)
