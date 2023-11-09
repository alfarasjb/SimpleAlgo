import importlib.util
import sys
import os
from threading import Thread
import logging

## CLASS FOR IMPORTING PYTHON STRATEGIES ## 


_log = logging.getLogger(__name__)


class Init_Strat():
	"""Main Class for handling strategies in strategy directory

	...

	Methods
	-------
	get_strats() - Main function call for building list of available strategies in directory
	check_class() - Searches line by line for classes in file
	load_module() - Helper function for loading module for valid strategies
	add_strat_to_table() - Adds selected strategy to strategies table
	remove_strat_from_table() - Removes selected strategy from strategies table
	running_strategy() - Triggers strategy thread and monitors running strategies
	"""
	def __init__(self, path = r'.'):
		# Directory 
		self.dir_path = path

		# Two Lists: Strat Class Instancem Filenames list
		#self.filenames, self.class_object = self.get_strats_list()
		
		self.filenames, self.class_object = self.get_strats()
		# STRATEGY HANDLING 
		self._strategies_in_table = [] # VECTORs
		self._running_strategies = []
	
	def get_strats(self):
		"""Main function call for building list of available strategies in directory

		Returns
		-------
		list -> res
			List of files

		obj -> dict
			Dictionary of available strategies
		"""
    	#objective: return list of files, and strategy objects
		this_file = os.path.basename(__file__)

		excluded_files = [this_file, '__init__.py']
		dir_files = []
		[dir_files.append(d) for d in os.listdir('.\strategies') if d.endswith('.py') and d not in excluded_files]

		res = []
		obj = {}
		for d in dir_files:
			#check classes
			#print(d)
			k, class_name = self.check_class(d)
			if  k is not None:
				res.append(class_name)
				obj[d] = k
		return res, obj

	def check_class(self, f):
		"""Searches line by line for classes in file

		Parameters
		----------
		f: str 
			Filename of python strategy

		Returns
		-------
		k - Class Module
		class_name: str
			Class name 
		"""
		with open(f'strategies/{f}', 'r') as file:
			lines = file.readlines()
			for line in lines: 
				class_name = ''
				if 'class' not in line or not line.startswith('class'):
					continue
				
				l = line.replace('class ', '')
				for c in l:
					if c == ':' or c == '(':
						break 
					class_name += c 
				try: 	
					k = self.load_module(f.replace('.py', ''), class_name)
					return k, class_name
				except AttributeError:
					return None, None

	@staticmethod
	def load_module(file_name, class_name):
		"""Helper function for loading module for valid strategies

		Parameters
		----------
		file_name: str
			File name of strategy to load

		class_name: str
			Class name of strategy

		Returns
		-------
		Module of selected strategy
		"""
    	
		spec = importlib.util.find_spec(f'strategies.{file_name}')
		module = importlib.util.module_from_spec(spec)
		sys.modules[file_name] = module 
		spec.loader.exec_module(module)
	
		k = getattr(module, class_name)
		return k
	
	'''
	def get_strats_list(self):
        # THIS IS A WORKING METHOD
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
	'''
	
	def add_strat_to_table(self, obj, timeframe, symbol, key, state = 0):
		"""Adds selected strategy to strategies table

		Parameters
		----------
		obj: Any
			Strategy Object
		
		timeframe: str
			Timeframe to execute the strategy

		symbol: str
			Symbol to execute the strategy

		key: str
			Name of strategy

		state: int 
			Enabled/Disabled

		Returns
		-------
		None -> if strategy is already in table
		"""
		for strat in self._strategies_in_table:
			data = (strat[0].name, strat[0].timeframe, strat[0].symbol)
			incoming = (key, timeframe, symbol)

			if incoming == data:
				_log.info('Cannot add strategy to table. Duplicate found.')
				return None

		strategy = obj(timeframe = timeframe, symbol = symbol)
		data = [strategy, state]
		self._strategies_in_table.append(data)
		_log.info(f'Strategies Table Updated to {len(self._strategies_in_table)}')

	def remove_strat_from_table(self, obj: list):
		"""Removes strategy from strategies table

		obj: list
			Strategy in strategy list
			Format: [Strategy, State]
		"""

		assert type(obj) == list, f'Invalid Object Type. Received Type: {type(obj)}'
		assert len(obj) == 2, f'Invalid Object Length. Received Length: {len(obj)}'
		self._strategies_in_table.remove(obj)

	def running_strategy(self, index, switch_state):
		"""Triggers strategy thread and monitors running strategies

		Parameters
		----------
		index: int 
			Strategy index in strategies in table (to update)

		switch_state: int
			Switch state (Enabled/Disabled)
		"""
		assert type(index) == int, 'Invalid Index Type'
		assert type(switch_state) == int, 'Invalid Switch Value Type'

		strategy = self._strategies_in_table[index][0]
		#print('STRATEGY TO UPDATE: ', strategy.name, strategy.timeframe, strategy.symbol)

		if switch_state == 1:
			self._running_strategies.append(strategy)
		elif switch_state == 0:
			self._running_strategies.remove(strategy)
		else:
			raise ValueError('Unknown Switch State')

		t = Thread(target = strategy.toggle_strat_state, daemon = True, args = [bool(switch_state)])

		t.start()

		#print('RUNNING STRATEGIES UPDATED', len(self._running_strategies))
