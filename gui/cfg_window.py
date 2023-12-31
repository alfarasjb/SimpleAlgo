import customtkinter as ctk 
import tkinter as tk 
import logging

# Local Imports
#from config.load_cfg import Load_Config
import config
'''
Config / Settings window
Configure MT5 Path and strategies folder
MT5 Path - executable
Strategies Folder - contains python formatted trading strategies



'''

_log = logging.getLogger(__name__)


class CfgWindow(ctk.CTkToplevel):
	"""Config Window - input fields for configuring path

	...
	
	Methods
	-------
	path_dialog() - File explorer popup dialog for browsing mt5 executable path
	strat_dialog() - File explorer popup dialog for browsing strategies directory
	open_file_dialog() 
	close() - Closes window on pressing 'Save' button
	
	"""

	def __init__(self):

		super().__init__()

		self.config = config.Load_Config()
		self.path = self.config._path
		self.strats = self.config._strategies


		self.title(self.config._settings)
		self.geometry(f'{self.config._cfg_resolution[0]}x{self.config._cfg_resolution[1]}')
		self.maxsize(self.config._cfg_resolution[0], self.config._cfg_resolution[1])
		self.minsize(self.config._cfg_resolution[0], self.config._cfg_resolution[1])
	
		# MT5 PATH 
		self.path_label = ctk.CTkLabel(self, text = 'MT5 Path', fg_color = 'transparent')
		self.path_label.place(x = 10, y = 10)

		self.path_str = ctk.CTkLabel(self, text = self.config._path)
		self.path_str.place(x = 110, y = 10)

		self.path_label_button = ctk.CTkButton(self,
			text = '...', width = 20, height = 25, command = self.path_dialog)
		self.path_label_button.place(x = 470, y = 10)

		# STRATEGIES PATH 
		self.strat_path_label = ctk.CTkLabel(self, 
			text = 'Strategies Path', fg_color = 'transparent')
		self.strat_path_label.place(x = 10, y = 50)


		self.strat_str = ctk.CTkLabel(self, text = self.config._strategies)
		self.strat_str.place(x = 110, y = 50)

		self.strat_path_button = ctk.CTkButton(self,
			text = '...', width = 20, height = 25, command = self.strat_dialog)
		self.strat_path_button.place(x = 470, y = 50)

		self.save_button = ctk.CTkButton(self, 
			text = 'Save', width = 460, command = self.close)
		self.save_button.place(x = 20, y = 150)

		
	def path_dialog(self):
		"""File explorer popup dialog for browsing mt5 executable path
		"""
		file = tk.filedialog.askopenfile()
		self.path_str.configure(text = file.name)
		self.path = file.name

	def strat_dialog(self):
		"""File explorer popup dialog for browsing strategies directory
		"""
		file = tk.filedialog.askdirectory()
		self.strat_str.configure(text = file)
		self.strats = file

	def open_file_dialog(self):

		file = 	tk.filedialog.askopenfile()
		name = file.name if file != None else None
		return name

	def close(self):
		"""Saves path to JSON and closes the config window
		"""
		self.config.update_paths(self.path, self.strats)
		self.destroy()
