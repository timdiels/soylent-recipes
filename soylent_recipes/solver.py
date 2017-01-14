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
Diet problem solver
'''

import numpy as np
import logging
import ecyglpki

_logger = logging.getLogger(__name__)

#TODO make class with nutrition_target in ctor and transform it to the perfect representation for perf here
def solve(nutrition_target, foods):
    '''
    Calculate food amounts to reach the nutrition target
    
    Parameters
    ----------
    nutrition_target : soylent_recipes.nutrition_target.NormalizedNutritionTarget
        The desired nutrition
    foods : np.array
        The foods to use to achieve the nutrition target. Contains exactly the
        nutrients required by the nutrition target in the exact same order. Rows
        represent foods, columns represent nutrients.
        
    Returns
    -------
    amounts : np.array(int) or None
        The amounts of each food to use to optimally achieve the nutrition
        target. ``amounts[i]`` is the amount of the i-th food to use. If the
        nutrition target cannot be achieved, returns None.
    '''
    # Implementation: using the GLPK C library via ecyglpki Python library binding
    # GLPK documentation: http://kam.mff.cuni.cz/~elias/glpk.pdf
    # GLPK wikibook: https://en.wikibooks.org/wiki/GLPK
    # ecyglpki documentation: http://pythonhosted.org/ecyglpki/
    #
    # GPLK lingo: rows and columns refer to Ax=b where b_i are auxiliary
    # variables, x_i are structural variables. Setting constraints on rows, set
    # constraints on b_i, while column constraints are applied to x_i.
    
    # Note: glpk is powerful. We're using mostly the default settings.
    # Performance likely can be improved by tinkering with the settings; or even
    # by providing the solution to the least squares equivalent, with amounts
    # rounded afterwards, as starting point could improve performance.
    
    nutrition_target = nutrition_target.values
    
    problem = ecyglpki.Problem()
    problem.add_rows(len(nutrition_target))
    problem.add_cols(len(foods))
    
    # Fill nan with None
    mask = np.isnan(nutrition_target)
    nutrition_target = nutrition_target.astype(object)
    nutrition_target[mask] = None
    
    # Configure columns/amounts
    for i in range(len(foods)):
        problem.set_col_kind(i+1, 'integer')  # int
        problem.set_col_bnds(i+1, 0, None)  # >=0
    
    # Configure rows/nutrients
    for i, extrema in enumerate(nutrition_target):
        problem.set_row_bnds(i+1, *extrema)
        
    # Load A of our Ax=b
    A = dict(((index[1]+1,index[0]+1), value) for index, value in np.ndenumerate(foods))
    problem.load_matrix(A)
    
    # Solve
    int_opt_options = ecyglpki.IntOptControls()
    int_opt_options.presolve = True  # without this, you have to provide an LP relaxation basis
    int_opt_options.msg_lev = 'no'  # be quiet, no stdout
    try:
        problem.intopt(int_opt_options)
    except ValueError:
        return None
    if not np.isclose(problem.check_kkt('intopt', 'bounds')['abs'][0], 0.0):
        return None
    amounts = np.fromiter((problem.mip_col_val(i+1) for i in range(len(foods))), int)
    
    return amounts
