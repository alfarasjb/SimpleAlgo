import json
import logging

'''
Loading UI config, and path

'''

_log = logging.getLogger(__name__)

class Load_Config():
	"""Loads UI config, mt5 path, and strategies path from json file.

	...

	Methods
	-------
	load_json_file() - Loads UI config json file containing window size
	load_settings_file() - Loads MT5 path and strategies folder
	update_paths - Updates mt5 and strategies path
	"""
	def __init__(self):

		self.__source = 'CONFIG'
		self.config = self.load_json_file()
		self.settings = self.load_settings_file()

		# --- ATTRIBUTES ---

		# Settings
		self._path = self.settings['settings']['path']
		self._strategies = self.settings['settings']['strategies']

		# UI
		self.ui = self.config['ui']
		self._root_title = self.ui['root_title']
		self._version = self.ui['version']
		self._appearance_mode = self.ui['appearance_mode']
		self._default_color_scheme = self.ui['default_color_theme']
		self._root_resolution = self.ui['root_resolution']
		self._login_resolution = self.ui['login_resolution']
		self._about_resolution = self.ui['about_resolution']
		self._cfg_resolution = self.ui['cfg_resolution']

		# UI - Button Labels
		self.button_labels = self.ui['button_labels']
		self._chg_acct = self.button_labels['chg_acct']
		self._launch_mt5 = self.button_labels['launch_mt5']
		self._settings = self.button_labels['settings']
		self._about = self.button_labels['about']

		_log.info('%s : MT5 PATH: %s', self.__source, self._path)
		_log.info('%s : STRATEGIES PATH: %s', self.__source, self._strategies)

	@staticmethod
	def load_json_file():
		"""Loads UI config JSON file containing window size
		"""
		try:
			with open(r'config//configs.json') as json_file:
				config = json.load(json_file)
				return config
		except Exception:
			_log.info('CFG: Config File is Missing.')

	@staticmethod
	def load_settings_file():
		"""Loads MT5 path and Strategies folder
		
		"""
		try:
			with open('config//settings.json') as json_file:
				cfg = json.load(json_file)
				return cfg
		except Exception:
			_log.info('CFG: Config File is Missing.')

	def update_paths(self, path: str, strategies: str):
		"""Updates mt5 and strategies path.
	
		Parameters
		----------
		path: str
			MT5 executable path

		strategies: str 
			Strategies folder path. The program will look for strategies here.
		
		"""
		# Updates settings on json file
		self._path = path
		self._strategies = strategies
		cfg = self.load_settings_file()

		cfg['settings']['path'] = path 
		cfg['settings']['strategies'] = strategies
		_log.info('Updating Path')
		_log.info('MT5 Executable: %s', path)
		_log.info('Strategies Directory: %s', strategies)

		json_file = open('config//settings.json', 'w')
		json.dump(cfg, json_file)
		json_file.close()

