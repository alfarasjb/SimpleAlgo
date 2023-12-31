"""
Root App File
"""

import tkinter as tkinter
import tkinter.messagebox
import customtkinter as ctk
from CTkTable import *
from tkinter import ttk
from threading import Thread

import logging

# Local Imports
import gui # LoginWindow, Account Info, CFgWindow, About Window
import event # MT5_Py, Trade Handler
import config # Load_Config
import templates # Trade_Package
import strategies # Init_Strat
import signals

ctk.set_appearance_mode('System')
ctk.set_default_color_theme('blue')

_log = logging.getLogger(__name__)

class App(ctk.CTk):


	def __init__(self):

		super().__init__()

		## CREATING INSTANCES OF MAIN CLASSES
		self.info = gui.Account_Info()
		self.mt5_py = event.mt5_py
		self.config = config.cfg
		self.init_strat = strategies.Init_Strat(self.config._strategies)
		self.signals_handler = event.Signals_Handler()
		self.manual_trading = None
		self.strats_tab = None
		

		# Data to display 
		self._hist_data = [] # Trade history - fetch from mt5, and restructure
		self._open_pos_data = [] # Open Positions - fetch from mt5 and restructure
		self._sidebar_elements = [] # Account Info sidebar elements
		#self._strat_elements = [] # Strategies Sidebar elements
		#self._pending_order_params = []
		#self._market_order_params = []
		self._active_strats_switch = []

		self._strat_names = self.init_strat.filenames # list of strat


		self._loginWindow = None # Login window
		self._cfgWindow = None # Settings Window
		self._abtWindow = None # About Window

		self._algo_trading_enabled = False # Algo trading main state override all 

		# Dynamic Elements
		self._symbols_list = self.mt5_py.symbols
		#self.symbols_dropdown = None

		# Main window configuration
		self.title(self.config._root_title)
		self.geometry(f'{self.config._root_resolution[0]}x{self.config._root_resolution[1]}')
		self.maxsize(self.config._root_resolution[0], self.config._root_resolution[1])
		self.minsize(self.config._root_resolution[0], self.config._root_resolution[1])
		self.grid_columnconfigure(1, weight = 1)
		#self.grid_columnconfigure((2, 3), weight = 0)
		self.grid_rowconfigure(1, weight = 1)

		# Build main elements / columns
		self.build_left_sidebar()
		self.build_right_sidebar()
		self.build_mid_column()



	def build_mid_column(self):

		# Build Mid Column
		#self.build_main_header()

		#tab_names = ['Open Positions', 'History', 'Strategies', 
		#'Correlation Matrix', 'Signals', 'Manual Trading']

		#tab_names = ['Strategies', 'Manual Trading', 'Open Positions', 'History', 'Signals']
		#tab_names = ['Strategies', 'Manual Trading', 'Signals', 'Equities']
		tab_names = ['Strategies','Signals']
		# Builds Main Tabview ; command builds elements per tab
		self.tabview = ctk.CTkTabview(self, command = self.tab_func)
		self.tabview.grid(row = 1, column = 1, padx = 20, pady = 10, sticky = 'nsew') # Position in master 
		[self.tabview.add(tab_name) for tab_name in tab_names] # Creates individual tabs
		self.tab_func()
  
	def build_left_sidebar(self):

		# Left Sidebar
		self.sidebar_frame = ctk.CTkFrame(self, width = 200, corner_radius = 10)

		self.sidebar_frame.grid(row = 0, column = 0, rowspan = 4, sticky = 'nsew')
		self.sidebar_frame.grid_rowconfigure(4, weight = 1)
		self.build_sidebar_elements()

	def build_right_sidebar(self):

		# Right Sidebar
		self.right_sb_frame = ctk.CTkFrame(self, width = 200, corner_radius = 10)

		self.right_sb_frame.grid(row = 0, column = 2, columnspan = 2, rowspan = 4, sticky = 'nsew')
		#self.right_sb_frame.grid_columnconfigure(0, weight = 1)
		#self.build_strat_sidebar_elements()
		gui.Strat_Sidebar(self.right_sb_frame, self._strat_names, self._algo_trading_enabled)

	def build_sidebar_elements(self):

		# Build Left Sidebar Elements (Account Info, General Buttons)
		items = ['Account Number', 'Server', 'Balance']
		values = [self.info.acct_num, self.info.server, self.info.balance]
	
		for i, (item, value) in enumerate(zip(items, values)):
			text_to_display = f'{item}\n{value}'
			element = ctk.CTkLabel(master = self.sidebar_frame, 
				text = item.upper(),
				font = ctk.CTkFont(size = 14, weight = 'bold'))
			element.grid(row = i, column = 0, padx = 15, pady = (10, 0))

			val = ctk.CTkLabel(master = element,
				text = value)
			val.grid(row = i + 1, column = 0, padx = 15)

			self._sidebar_elements.append((element, val))

		self.change_account_button = ctk.CTkButton(self.sidebar_frame, 
			command = self.change_account_popup, text = self.config._chg_acct, state = 'disabled')
		self.mt5_button = ctk.CTkButton(self.sidebar_frame, 
			command = self.launch_mt5, text = self.config._launch_mt5)
		self.cfg_button = ctk.CTkButton(self.sidebar_frame, 
			command = self.cfg_popup, text = self.config._settings)
		self.abt_button = ctk.CTkButton(self.sidebar_frame, 
			command = self.abt_popup, text = self.config._about)

		self.change_account_button.grid(row = 5, column = 0, padx = 10, pady = 5)
		self.mt5_button.grid(row = 6, column = 0, padx = 10, pady = 5)		
		self.cfg_button.grid(row = 7, column = 0, padx = 10, pady = 5)		
		self.abt_button.grid(row = 8, column = 0, padx = 10, pady = (5, 10))


	def build_table(self, master, headers, data):

		# General Helper funcion for constructing tables
		table_data = data
		table_data.insert(0, headers)
		self.table = CTkTable(master, values = table_data)
		self.table.pack(expand = False, fill = 'x')
	

	# UI Operation and Logic (Dynamic Buttons, Table Updating)
	def update_table(self, header, data):

		# Update Table Values
		data.insert(0, header)
		self.table.configure(values = data)

	def tab_func(self):

		# Command for building elements under tabview
		name = self.tabview.get()
		if name == 'Open Positions':
			# Open Positions Tab
			header, data = self.mt5_py.fetch_open_positions()
			if data == None:
				return None
			elif ((len(data) != len(self._open_pos_data))):
				if len(self._open_pos_data) == 0:
					self._open_pos_data = data
					self.build_table(self.tabview.tab('Open Positions'), header, data)
				else:
					self.update_table(header, data)
			else:
				return None

		elif name == 'History':
			# History Tab
			header, data = self.mt5_py.fetch_order_history()
			if data == None:
				return None
			elif ((len(data) != len(self._hist_data))):
				if len(self._hist_data) == 0:
					self._hist_data = data 
					# when history = 0, on start of program
					self.build_table(self.tabview.tab('History'), header, data)
				else:
					self.update_table(header, data)
			else:
				return None

		elif name == 'Manual Trading':
			# Manual Trading Tab
			if self.manual_trading is None:
				self.manual_trading = gui.Manual_Trading(self.tabview.tab('Manual Trading'))
			else:
				if self._symbols_list is not None:
					self.manual_trading.update_symbols_dropdown(self._symbols_list)

		elif name == 'Strategies':
			# Strategies Tab
			if self.strats_tab is None:
				self.strats_tab = gui.Strats_Tab(self.tabview.tab('Strategies'), self.init_strat)
				self.strats_tab.build_active_strats()

			
		elif name == 'Signals':
			# Signals Tab
			self.signals_handler.create_signals_tab(self.tabview.tab('Signals'))
		
		elif name == 'Equities':
			# Equities tab goes here
			pass
		# BUTTON COMMANDS

	def update_account_data(self, data):
	# General Helper function for updating left sidebar (Can be called on change account)
		[self._sidebar_elements[i][1].configure(text = info_data) for i, info_data in enumerate(data)]

	def launch_mt5(self):
		# Launch MT5
		if self.mt5_py.launch_mt5():
			name, num, brkr, bal = self.mt5_py.fetch_account_info()
			self.update_account_data((num, brkr, bal)) # Updates account data on left sidebar
			self._symbols_list = self.mt5_py.fetch_symbols()

			self.tab_func() # Updates table elements on MT5 Launch
			# TEMPORARILIY DISABLED
			#self.signals_handler.update_signals()
			

	def change_account_popup(self):
		# Creates Login popup window
		# TODO: Disable root window if this enabled (DONE)
		if self._loginWindow is None or not self._loginWindow.winfo_exists():		
			self._loginWindow = gui.LoginWindow()
			self.lock_popup(self._loginWindow)
		else:
			self.loginWindow.focus()

	def cfg_popup(self):
		# Create Settings popup window
		if self._cfgWindow is None or not self._cfgWindow.winfo_exists():
			self._cfgWindow = gui.CfgWindow()
			self.lock_popup(self._cfgWindow)
		else:
			self._cfgWindow.focus()

	def abt_popup(self):
		# Create about popup window
		if self._abtWindow is None or not self._abtWindow.winfo_exists():
			self._abtWindow = gui.AbtWindow()
			self.lock_popup(self._abtWindow)
		else:
			self._abtWindow.focus()

	def lock_popup(self, window):

		window.attributes('-topmost','true')
		window.grab_set()

if __name__ == "__main__":

	format = '%(asctime)s: %(message)s'
	logging.basicConfig(format = format, level = logging.INFO, datefmt = '%H:%M:%S')
	logging.info('Launching PyAlgo v0.0.1')
	app = App()
	app.mainloop()