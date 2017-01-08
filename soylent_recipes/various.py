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

#TODO add to CTU        
import cProfile
import pyprof2calltree
import functools
class profile(object):
    
    def __call__(self, f):
        @functools.wraps(f)
        def profiled(*args, **kwargs):
            profile = cProfile.Profile()
            profile.enable()
            try:
                return f(*args, **kwargs)
            finally:
                profile.disable()
                profile.dump_stats('profile.cprofile')
                pyprof2calltree.convert(profile.getstats(), 'profile.kgrind')
                pyprof2calltree.visualize(profile.getstats())
        return profiled