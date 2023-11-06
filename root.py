

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
		self.fcast = signals.Forecast()


		# Data to display 
		self._hist_data = [] # Trade history - fetch from mt5, and restructure
		self._open_pos_data = [] # Open Positions - fetch from mt5 and restructure
		self._sidebar_elements = [] # Account Info sidebar elements
		self._strat_elements = [] # Strategies Sidebar elements
		self._pending_order_params = []
		self._market_order_params = []
		self._active_strats_switch = []

		self._strat_names = self.init_strat.filenames # list of strat
		self._strat_objects = self.init_strat.class_object


		self._loginWindow = None # Login window
		self._cfgWindow = None # Settings Window
		self._abtWindow = None # About Window

		self._algo_trading_enabled = False # Algo trading main state override all 

		# Dynamic Elements
		self._symbols_list = self.mt5_py.symbols
		self.symbols_dropdown = None


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


	def build_main_header(self):

		# Header and Title
		self.header_frame = ctk.CTkFrame(self, border_color = 'white')
		self.main_header = ctk.CTkLabel(self.header_frame, width = 250, height = 0, 
			text = self.config._root_title, font = ctk.CTkFont(size = 20, weight = 'bold'))


		self.header_frame.grid(row = 0, column = 1, padx = 30, pady = (10, 0))
		self.main_header.grid(row = 0, column = 0, padx = 20, pady = 10, sticky = '')


	def build_mid_column(self):

		# Build Mid Column
		self.build_main_header()

		#tab_names = ['Open Positions', 'History', 'Strategies', 
		#'Correlation Matrix', 'Signals', 'Manual Trading']

		tab_names = ['Strategies', 'Manual Trading', 'Open Positions', 'History', 'Signals']

		# Builds Main Tabview ; command builds elements per tab
		self.tabview = ctk.CTkTabview(self, command = self.tab_func)
		self.tabview.grid(row = 1, column = 1, padx = 20, pady = 10, sticky = 'nsew') # Position in master 
		[self.tabview.add(tab_name) for tab_name in tab_names] # Creates individual tabs

		#self.open_pos_label = ctk.CTkLabel(self.tabview.tab(tab_names[0]), text = 'CONNECT TO MT5', 
		#	text_color = 'grey', font = ctk.CTkFont(size = 16, weight = 'bold'))
		#self.open_pos_label.pack(padx = 20, pady = 50)

		#self.hist_label = ctk.CTkLabel(self.tabview.tab(tab_names[1]), text = 'CONNECT TO MT5',
		#	text_color = 'grey', font = ctk.CTkFont(size = 16, weight = 'bold'))
		#self.hist_label.pack(padx = 20, pady = 50)

		# tab 3
		self.tab3_label = ctk.CTkLabel(self.tabview.tab(tab_names[2]), text = f'{tab_names[2]} Label')
		
		self.tab4_label = ctk.CTkLabel(self.tabview.tab(tab_names[3]), text = f'{tab_names[3]} Label')
		
		self.tab5_label = ctk.CTkLabel(self.tabview.tab(tab_names[3]), text = f'{tab_names[3]} Label')
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
		self.build_strat_sidebar_elements()

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

	def build_strat_sidebar_elements(self):

		# Strategies in strategies folder
		strats = self._strat_names
		algo_button_status, algo_button_clr = self.algo_trading_button_color()

		header = ctk.CTkLabel(master = self.right_sb_frame,
			text = 'STRATEGIES', font = ctk.CTkFont(size = 14, weight = 'bold'))
		self.algo_trading_button = ctk.CTkButton(self.right_sb_frame, text = algo_button_status,
			fg_color = algo_button_clr, hover_color = algo_button_clr, command = self.toggle_algo_trading)

		header.grid(row = 0, column = 0, columnspan = 2, padx = 30, pady = (20, 10))
		self.algo_trading_button.grid(row = 1, column = 0, columnspan = 2, padx = 30, pady = (10, 20))

		# Build Strategies list (label + Switch) 
		for i, strat in enumerate(strats):
			strat_name = ctk.CTkLabel(self.right_sb_frame, text = strat.replace('.py', ''))
			strat_name.grid(row = i + 2, column = 0, padx = (10, 10), pady = (0, 10))


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
			if len(self._pending_order_params) == 0:
				self.build_manual_trading()
			else:
				if self._symbols_list is not None:
					self.symbols_dropdown.configure(values = self._symbols_list)

		elif name == 'Strategies':
			# Strategies Tab
			self.build_strategies_tab()
			self.build_active_strats()

		elif name == 'Signals':
			# Signals Tab
			self.build_signals_tab()

	
	def build_signals_tab(self):
		signals = self.fcast.read_data()
		self.gui = gui.Signals_Tab(self.tabview.tab('Signals'), signals)

		
		# BUILD UI 

	def build_strategies_tab(self):

		strat_names = list(self._strat_objects.keys())
		symbols_list = ['Symbols']
		timeframes = ['m1', 'm5', 'm15', 'm30']
		strat_menu_var = ctk.StringVar(value = 'Strategies')
		tf_menu_var = ctk.StringVar(value = 'Timeframe')
		symbols_menu_var = ctk.StringVar(value = 'Symbols')
		# invoke this class
		#self._strat_objects[0](timeframe = 'm15', symbol = 'GBPUSD')

		# HEADER FRAME (For input feels and dropdown menu)
		self.strat_hdr_frame = ctk.CTkFrame(self.tabview.tab('Strategies'))
		self.strats_dropdown = ctk.CTkOptionMenu(self.strat_hdr_frame,
			values = strat_names, variable = strat_menu_var)
		self.tf_dropdown = ctk.CTkOptionMenu(self.strat_hdr_frame,
			values = timeframes, variable = tf_menu_var)
		self.target_symbol = ctk.CTkEntry(self.strat_hdr_frame, placeholder_text = 'Symbol')
		self.add_button = ctk.CTkButton(self.strat_hdr_frame, text = 'Confirm',
			command = self.add_strat, width = 70)

		self.strat_hdr_frame.grid(row = 0, column = 0, padx = 20, pady = 10)
		self.strats_dropdown.grid(row = 0, column = 0, padx = 20, pady = 10)
		self.tf_dropdown.grid(row = 0, column = 1, padx = 20, pady = 10)
		self.target_symbol.grid(row = 0, column = 2)
		self.add_button.grid(row = 0, column = 3, padx = 20, pady = 10)

		### TIMEFRAME

		#self.tf_entry = ctk.CTkEntry(self.strat_hdr_frame, placeholder_text = 'Timeframe')
		#self.tf_entry.grid(row = 0, column = 1, padx = 10, pady = 10)

		#self.target_symbol = ctk.CTkOptionMenu(self.strat_hdr_frame,
		#	values = symbols_list, variable = symbols_menu_var)
		#self.target_symbol.grid(row = 0, column = 2, padx = 10, pady = 10)

		### SYMBOLS AS ENTRY

		

		
	def build_active_strats(self):
		pady = (5, 0)
		self._active_strats_switch = []
		labels = ['Strategy', 'Symbol', 'Timeframe', 'Toggle', '']
		### ===== ACTIVE STRATEGIES LIST ===== ### 
		self.scroll_frame = ctk.CTkScrollableFrame(self.tabview.tab('Strategies'), width = 650, fg_color = 'transparent')
		self.scroll_frame.grid(row = 1, column = 0, columnspan = 3, padx = 10)
		self.scroll_frame.grid_columnconfigure(3, weight = 1)
		
		for j, label in enumerate(labels):
			self.header_label = ctk.CTkLabel(self.scroll_frame, text = label)
			self.header_label.grid(row = 0, column = j, padx = 40, pady = pady)

		## BUILD HEADER
		for i, st in enumerate(self.init_strat._strategies_in_table):
			self.build_strat_row(st[0].name, st[0].timeframe, st[0].symbol, i)

	def switch_strat(self, index):
		strategy = self.init_strat._strategies_in_table[index]
		switch = self._active_strats_switch[index]
		self.init_strat.running_strategy(index, switch.get())
		self.init_strat._strategies_in_table[index][1] = switch.get() # EDIT SWITCH STATE

	def add_strat(self):
		'''
		CHECKS: 
		1. Existing instances for same symbol and timeframe
		'''
		key = self.strats_dropdown.get() # name of the strategy
		obj = self._strat_objects[key] if key in list(self._strat_objects.keys()) else None
		strats_in_table = len(self.init_strat._strategies_in_table)
		timeframe = self.tf_dropdown.get()
		symbol = self.target_symbol.get()

		if obj != None:
			# INIT STRAT - ADD STRAT TO TABLE
			self.init_strat.add_strat_to_table(obj, timeframe, symbol, key)
			self.build_strat_row(key, timeframe, symbol, strats_in_table)
		else: 
			print(key)


	def build_strat_row(self, strat_name, timeframe, symbol, i):

		state = self.init_strat._strategies_in_table[i][1]
		pady = (5, 0)
		padx = (20, 0)
		self.st_label = ctk.CTkLabel(self.scroll_frame, text = strat_name)
		self.st_symbol = ctk.CTkLabel(self.scroll_frame, text = symbol)
		self.st_tf = ctk.CTkLabel(self.scroll_frame, text = timeframe)
		self.st_switch = ctk.CTkSwitch(self.scroll_frame, text = '',
		 command = lambda index = i : self.switch_strat(index))
		self.st_cancel_button = ctk.CTkButton(self.scroll_frame, text = 'X',
			command = lambda index = i : self.remove_strat(index), width = 20, height = 20)

		self.st_label.grid(row = i + 1, column = 0, padx = padx, pady = pady)
		self.st_symbol.grid(row = i + 1, column = 1, padx = padx, pady = pady)
		self.st_tf.grid(row = i + 1, column = 2, padx = padx, pady = pady)
		self.st_switch.grid(row = i + 1, column = 3, padx = (50, 5), pady = pady)
		self.st_cancel_button.grid(row = i + 1, column = 4, padx = 0, pady = pady)


		if state == 1:
			self.st_switch.select()
		elif state == 0:
			self.st_switch.deselect()

		self._active_strats_switch.append(self.st_switch)

	def remove_strat(self, i):
		# REMOVE FROM LIST AND REDRAW
		strat_to_remove = self.init_strat._strategies_in_table[i]
		switch_to_remove = self._active_strats_switch[i]

		if strat_to_remove[1] == 1:
			self.init_strat.running_strategy(i, 0)
		self.init_strat.remove_strat_from_table(strat_to_remove)
		self._active_strats_switch.remove(switch_to_remove)
		self.build_active_strats()

	def build_manual_trading(self):
		# Manual Trading Page

		symbols_list = ['Symbols']
		option_menu_var = ctk.StringVar(value = 'Symbols')
		po_params = ['Price', 'Stop Loss', 'Take Profit', 'Volume']

		self.symbol_frame = ctk.CTkFrame(self.tabview.tab('Manual Trading'))
		#self.symbol_frame.grid(row = 0, column = 0, columnspan = 2, padx = 10, pady = 10)
		self.symbol_label = ctk.CTkLabel(self.symbol_frame, text = 'Symbol')
		self.symbols_dropdown = ctk.CTkOptionMenu(self.symbol_frame, 
			values = symbols_list, variable = option_menu_var)
		self.po_frame = ctk.CTkFrame(self.symbol_frame)
		self.po_header = ctk.CTkLabel(self.po_frame, text = 'PENDING ORDER')


		self.symbol_frame.pack(fill = 'x')
		self.symbol_frame.grid_columnconfigure((0, 1), weight = 1)
		self.symbol_frame.grid_rowconfigure((0, 1), weight = 1)
		self.symbol_label.grid(row = 0, column = 0, padx = 20, pady = (20, 10))
		self.symbols_dropdown.grid(row = 0, column = 1, padx = 20, pady = 20)
		self.po_frame.grid(row = 1, column = 0, padx = 10, pady = 10)
		self.po_frame.grid_rowconfigure(4, weight = 1)
		self.po_header.grid(row = 0, column = 0, columnspan = 2, padx = 20, pady = 10)

		# PRICE FIELDS
		for i, param in enumerate(po_params):
			self.po_label = ctk.CTkLabel(self.po_frame, text = param)
			self.po_field = ctk.CTkEntry(self.po_frame)

			self.po_label.grid(row = i + 1, column = 0, padx = 20, pady = 10)
			self.po_field.grid(row = i + 1, column = 1, padx = 20, pady = 10)

			self._pending_order_params.append((self.po_field))

		self.blim_button = ctk.CTkButton(self.po_frame, text ='Buy Limit', 
			command = lambda order_type = 'Buy Limit': self.send_pending_order(order_type))
		self.slim_button = ctk.CTkButton(self.po_frame, text = 'Sell Limit', 
			command = lambda order_type = 'Sell Limit' : self.send_pending_order(order_type))
		self.manual_trading_frame = ctk.CTkFrame(self.symbol_frame)
		self.manual_header = ctk.CTkLabel(self.manual_trading_frame, text = 'MARKET ORDER')

		self.blim_button.grid(row = 5, column = 1, padx = 20, pady = 10)
		self.slim_button.grid(row = 5, column = 0, padx = 20, pady = 10)		
		self.manual_trading_frame.grid(row = 1, column = 1, padx = 10, pady = 10)
		self.manual_trading_frame.grid_rowconfigure(4, weight = 1)
		self.manual_header.grid(row = 0, column = 0, columnspan = 2, padx = 20, pady = 10)



	# Buy Limit Sell Limit
	def send_pending_order(self, order_type: str):
		# Processing order form

		# Creates a list containing trade info to send to trade handler
		order_params = ['Manual', self.symbols_dropdown.get(), order_type, 'Pending']
		
		for order in self._pending_order_params:
			price = float(order.get()) if order.get() != '' else 0
			order_params.append(price)

		# Process order send
		pending_order = templates.Trade_Package(order_params) # repackaging

		'''
		Trade handler class, explore possibility of creating class instance 
		on init instead of internally.
		'''
		trade_handler = event.trade_handler

		# Sends packaged order parameters to MT5 event handler
		trade_handler.send_order(pending_order) 

		# BUTTON COMMANDS
	def algo_trading_button_color(self):

		# Returns algo trading button color
		status = 'Enabled' if self._algo_trading_enabled else 'Disabled'
		color = 'green' if self._algo_trading_enabled else 'grey'
		ret_str = f'Algo Trading {status}'
		return ret_str, color
	
	def toggle_algo_trading(self):

		# Toggle algo trading status, and updates algo trading button color
		self._algo_trading_enabled = not self._algo_trading_enabled
		algo_status, algo_clr = self.algo_trading_button_color()
		self.algo_trading_button.configure(text = algo_status, fg_color = algo_clr, hover_color = algo_clr)
		state = 'normal' if self._algo_trading_enabled else 'disabled'
		for element in self._strat_elements:
			# element - tuple object containing switch and class instance
			# element [0] - switch
			element[0].configure(state = state)

		enabled = 'Enabled' if self._algo_trading_enabled else 'Disabled'
		_log.info('ROOT : Algo Trading %s', enabled)
		self.mt5_py._algo_trading_enabled = self._algo_trading_enabled
		# Toggle strategy switches

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
			self.fcast.update()

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