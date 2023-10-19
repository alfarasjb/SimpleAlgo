import json


'''
Loading UI config, and path

'''

class Load_Config():
	def __init__(self):
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

	def load_json_file(self):
		# loads ui config json file
		with open(r'config//configs.json') as json_file:
			config = json.load(json_file)
			return config

	def load_settings_file(self):
		# loads mt5 path and strategies folder json file
		with open('config//settings.json') as json_file:
			cfg = json.load(json_file)
			return cfg

	def update_paths(self, path, strategies):
		# Updates settings on json file
		self._path = path
		self._strategies = strategies
		cfg = self.load_settings_file()

		cfg['settings']['path'] = path 
		cfg['settings']['strategies'] = strategies

		json_file = open('settings.json', 'w')
		json.dump(cfg, json_file)
		json_file.close()

