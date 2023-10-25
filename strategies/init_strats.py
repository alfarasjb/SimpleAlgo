import importlib.util
import sys
import os
from threading import Thread

## CLASS FOR IMPORTING PYTHON STRATEGIES ## 

class Init_Strat():
	def __init__(self, path = r'.'):
		# Directory 
		self.dir_path = path

		# Two Lists: Strat Class Instancem Filenames list
		self.filenames, self.class_object = self.get_strats_list()
		

		# STRATEGY HANDLING 
		self._strategies_in_table = [] # VECTOR
		self._running_strategies = []


	def get_strats_list(self):
		this_file = os.path.basename(__file__) # This file name
		res = [] 
		obj = {}

		for path in os.listdir(self.dir_path):
			raw_path = self.dir_path + '/' + path
			if os.path.isfile(os.path.join(self.dir_path, path)) \
			and (path != this_file) \
			and ('.py' in path)\
			and ('__init__' not in path): 
				file = path.replace('.py', '')
				
				spec = importlib.util.find_spec(f'strategies.{file}')
				module = importlib.util.module_from_spec(spec)
				sys.modules[file] = module 
				spec.loader.exec_module(module)
				k = getattr(module, file)
				#instance = k()
				#strat.append(instance)
				res.append(path)
				obj[file] = k


		return res, obj


	def add_strat_to_table(self, obj, timeframe, symbol, key, state = 0):
		for strat in self._strategies_in_table:
			data = (strat[0].name, strat[0].timeframe, strat[0].symbol)
			incoming = (key, timeframe, symbol)

			if incoming == data:
				print('DUPLICATE FOUND')
				return None

		strategy = obj(timeframe = timeframe, symbol = symbol)
		data = [strategy, state]
		self._strategies_in_table.append(data)
		print('STRATEGIES TABLE UPDATED: ', len(self._strategies_in_table))

	def remove_strat_from_table(self, obj):
		print('REMOVE STRAT')
		self._strategies_in_table.remove(obj)

	def running_strategy(self, index, switch_state):
		strategy = self._strategies_in_table[index][0]
		print('STRATEGY TO UPDATE: ', strategy.name, strategy.timeframe, strategy.symbol)
		
		if switch_state == 1:
			self._running_strategies.append(strategy)
		elif switch_state == 0:
			self._running_strategies.remove(strategy)

		t = Thread(target = strategy.toggle_strat_state, daemon = True, args = [switch_state])

		t.start()

		print('RUNNING STRATEGIES UPDATED', len(self._running_strategies))
