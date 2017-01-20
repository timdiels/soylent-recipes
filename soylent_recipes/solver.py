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
import swiglpk as glp

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
    # GLPK documentation: download it and look inside the package (http://ftp.gnu.org/gnu/glpk/)
    # GLPK wikibook: https://en.wikibooks.org/wiki/GLPK
    #
    # GPLK lingo: rows and columns refer to Ax=b where b_i are auxiliary
    # variables, x_i are structural variables. Setting constraints on rows, set
    # constraints on b_i, while column constraints are applied to x_i.
    
    # Note: glpk is powerful. We're using mostly the default settings.
    # Performance likely can be improved by tinkering with the settings; or even
    # by providing the solution to the least squares equivalent, with amounts
    # rounded afterwards, as starting point could improve performance.
    
    nutrition_target = nutrition_target.values
    
    problem = glp.glp_create_prob()
    try:
        glp.glp_add_rows(problem, len(nutrition_target))
        glp.glp_add_cols(problem, len(foods))
        
        # Configure columns/amounts
        for i in range(len(foods)):
            glp.glp_set_col_kind(problem, i+1, glp.GLP_IV)  # int
            glp.glp_set_col_bnds(problem, i+1, glp.GLP_LO, 0.0, np.nan)  # >=0
        
        # Configure rows/nutrients
        for i, extrema in enumerate(nutrition_target):
            if np.isnan(extrema[0]):
                bounds_type = glp.GLP_UP
            elif np.isnan(extrema[1]):
                bounds_type = glp.GLP_LO
            else:
                # Note: a nutrition target has either min, max or both and min!=max
                bounds_type = glp.GLP_DB
            glp.glp_set_row_bnds(problem, i+1, bounds_type, *extrema)
            
        # Load A of our Ax=b
        non_zero_count = foods.size
        row_indices = glp.intArray(non_zero_count+1)  # +1 because (insane) 1-indexing
        column_indices = glp.intArray(non_zero_count+1)
        values = glp.doubleArray(non_zero_count+1)
        for i, ((row, column), value) in enumerate(np.ndenumerate(foods.transpose())):
            row_indices[i+1] = row+1
            column_indices[i+1] = column+1
            values[i+1] = value
        glp.glp_load_matrix(problem, non_zero_count, row_indices, column_indices, values)
        
        # Solve
        int_opt_args = glp.glp_iocp()
        glp.glp_init_iocp(int_opt_args)
        int_opt_args.presolve = glp.GLP_ON  # without this, you have to provide an LP relaxation basis
        int_opt_args.msg_lev = glp.GLP_MSG_OFF  # be quiet, no stdout
        glp.glp_intopt(problem, int_opt_args)  # returns an error code; can safely ignore
        
        # Check we've got a valid solution
        #
        # Note: glp_intopt returns whether the algorithm completed successfully.
        # This does not imply you've got a good solution, it could even be
        # infeasible. glp_mip_status returns whether the solution is optimal,
        # feasible, infeasible or undefined. An optimal/feasible solution is not
        # necessarily a good solution. An optimal solution may even violate
        # bounds constraints. The thing you actually need to use is
        # glp_check_kkt and check that the solution satisfies KKT.PB (all within
        # bounds)
        max_error = glp.doubleArray(1)
        glp.glp_check_kkt(problem, glp.GLP_MIP, glp.GLP_KKT_PB, max_error, None, None, None)
        if not np.isclose(max_error[0], 0.0):
            # A row/column value exceeds its bounds
            return None
        
        # Return solution
        amounts = np.fromiter((glp.glp_mip_col_val(problem, i+1) for i in range(len(foods))), int)
        
        return amounts
    finally:
        glp.glp_delete_prob(problem)
