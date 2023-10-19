import importlib.util
import sys
import os

## CLASS FOR IMPORTING PYTHON STRATEGIES ## 

class Init_Strat():
	def __init__(self, path = r'.'):
		# Directory 
		self.dir_path = path

		# Two Lists: Strat Class Instancem Filenames list
		self.strat_instance, self.filenames = self.get_strats_list()


	def get_strats_list(self):
		this_file = os.path.basename(__file__) # This file name
		res = [] 
		strat = []

		for path in os.listdir(self.dir_path):
			raw_path = self.dir_path + '/' + path
			if os.path.isfile(os.path.join(self.dir_path, path)) and (path != this_file) and ('.py' in path):
			
				spec = importlib.util.spec_from_file_location(path, raw_path)
				foo = importlib.util.module_from_spec(spec)
				spec.loader.exec_module(foo)

				strat.append(foo.Strat())
				res.append(path)

		return strat, res


'''
init_strat = Init_Strat()
print(init_strat.strat_instance[0].name)
'''
