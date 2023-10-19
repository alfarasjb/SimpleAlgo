'''
Objective: 
1. view python files in specific directory
2. explore possibility of importing modules in specific directory
3. access attributes and methods
'''

from os.path import dirname, basename, isfile, join
import glob
import os

import importlib.util
import sys
'''
modules = glob.glob(join(dirname(__file__), '*.py'))
__all__ = [basename(f)[::-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]

print(__all__)
'''

dir_path = r'.'
res = []
strats = []
this_file = os.path.basename(__file__)
for path in os.listdir(dir_path):
	if os.path.isfile(os.path.join(dir_path, path)) and (path != this_file):
		spec = importlib.util.spec_from_file_location(path, path)
		foo = importlib.util.module_from_spec(spec)
		spec.loader.exec_module(foo)
		strats.append(foo.Strat())
		res.append(path)

print('Res: ', res)
[print(strat.name) for strat in strats]
'''
#print(os.path.basename(__file__))
spec = importlib.util.spec_from_file_location(res[0], res[0])
foo = importlib.util.module_from_spec(spec)
#sys.modules[res[0]] = foo
spec.loader.exec_module(foo)

print(foo.Strat().name)
'''
