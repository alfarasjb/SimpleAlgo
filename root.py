import tkinter as tkinter
import tkinter.messagebox
import customtkinter as ctk
from CTkTable import *
from tkinter import ttk


# Local Imports
from gui.acct_info import Account_Info
from gui.login import LoginWindow
from gui.cfg_window import CfgWindow
from gui.abt_window import AbtWindow
from event.mt5 import MT5_Py
from config.load_cfg import Load_Config
from templates.trade_template import Trade_Package
from event.trade_handler import Trade_Handler
from strategies.init_strats import Init_Strat


ctk.set_appearance_mode('System')
ctk.set_default_color_theme('blue')


class App(ctk.CTk):


	def __init__(self):

		super().__init__()

		## CREATING INSTANCES OF MAIN CLASSES
		self.info = Account_Info()
		self.mt5_py = MT5_Py()
		self.config = Load_Config()
		self.init_strat = Init_Strat(self.config._strategies)

		# Data to display 
		self._hist_data = [] # Trade history - fetch from mt5, and restructure
		self._open_pos_data = [] # Open Positions - fetch from mt5 and restructure
		self._sidebar_elements = [] # Account Info sidebar elements
		self._strat_elements = [] # Strategies Sidebar elements
		self._pending_order_params = []
		self._market_order_params = []

		self._strat_instances = self.init_strat.strat_instance # list of strat

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
		self.header_frame.grid(row = 0, column = 1, padx = 30, pady = (10, 0))
		self.main_header = ctk.CTkLabel(self.header_frame, width = 250, height = 0, 
			text = self.config._root_title, font = ctk.CTkFont(size = 20, weight = 'bold'))
		self.main_header.grid(row = 0, column = 0, padx = 20, pady = 10, sticky = '')


	def build_mid_column(self):

		# Build Mid Column
		self.build_main_header()

		tab_names = ['Open Positions', 'History', 'Strategies', 
		'Correlation Matrix', 'Signals', 'Manual Trading']

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

		# Change Account Button
		self.change_account_button = ctk.CTkButton(self.sidebar_frame, 
			command = self.change_account_popup, text = self.config._chg_acct, state = 'disabled')
		self.change_account_button.grid(row = 5, column = 0, padx = 10, pady = 5)

		# Launch MT5 Button
		self.mt5_button = ctk.CTkButton(self.sidebar_frame, 
			command = self.launch_mt5, text = self.config._launch_mt5)
		self.mt5_button.grid(row = 6, column = 0, padx = 10, pady = 5)

		# Settings Button
		self.cfg_button = ctk.CTkButton(self.sidebar_frame, 
			command = self.cfg_popup, text = self.config._settings)
		self.cfg_button.grid(row = 7, column = 0, padx = 10, pady = 5)

		# About Button
		self.abt_button = ctk.CTkButton(self.sidebar_frame, 
			command = self.abt_popup, text = self.config._about)
		self.abt_button.grid(row = 8, column = 0, padx = 10, pady = (5, 10))

	def build_strat_sidebar_elements(self):

		# Strategy Sidebar

		# Strategies in strategies folder
		strats = self._strat_instances

		# Strategies Header
		header = ctk.CTkLabel(master = self.right_sb_frame,
			text = 'STRATEGIES', font = ctk.CTkFont(size = 14, weight = 'bold'))
		header.grid(row = 0, column = 0, columnspan = 2, padx = 40, pady = (20, 10))
		#header.grid_columnconfigure(0, weight = 1)

		# ALGO TRADING TOGGLE SWITCH
		algo_button_status, algo_button_clr = self.algo_trading_button_color()
		self.algo_trading_button = ctk.CTkButton(self.right_sb_frame, text = algo_button_status,
			fg_color = algo_button_clr, hover_color = algo_button_clr, command = self.toggle_algo_trading)
		self.algo_trading_button.grid(row = 1, column = 0, columnspan = 2, padx = 40, pady = (10, 20))

		# Build Strategies list (label + Switch) 
		for i, strat in enumerate(strats):

			#label = ctk.CTkLabel(master = self.right_sb_frame, text = strat.name)
			#label.grid(row = i + 2, column = 0, padx = (10, 0), pady = (0, 10))

			switch = ctk.CTkSwitch(master = self.right_sb_frame, text = strat.name, text_color = 'grey', width = 0,
				command = lambda button_index = i: self.toggle_strat(button_index))
			switch.grid(row = i + 2, column = 0, padx = (10, 10), pady = (0, 10))
			
			self._strat_elements.append((switch, strat))


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

	def build_manual_trading(self):
		# Manual Trading Page

		symbols_list = ['Symbols']
		self.symbol_frame = ctk.CTkFrame(self.tabview.tab('Manual Trading'))
		#self.symbol_frame.grid(row = 0, column = 0, columnspan = 2, padx = 10, pady = 10)
		self.symbol_frame.pack(fill = 'x')
		self.symbol_frame.grid_columnconfigure((0, 1), weight = 1)
		self.symbol_frame.grid_rowconfigure((0, 1), weight = 1)
		self.symbol_label = ctk.CTkLabel(self.symbol_frame, text = 'Symbol')
		self.symbol_label.grid(row = 0, column = 0, padx = 20, pady = (20, 10))

		option_menu_var = ctk.StringVar(value = 'Symbols')
		self.symbols_dropdown = ctk.CTkOptionMenu(self.symbol_frame, 
			values = symbols_list, variable = option_menu_var)
		self.symbols_dropdown.grid(row = 0, column = 1, padx = 20, pady = 20)

		# Pending Order Column
		po_params = ['Price', 'Stop Loss', 'Take Profit']
		self.po_frame = ctk.CTkFrame(self.symbol_frame)
		self.po_frame.grid(row = 1, column = 0, padx = 10, pady = 10)
		self.po_frame.grid_rowconfigure(4, weight = 1)

		self.po_header = ctk.CTkLabel(self.po_frame, text = 'PENDING ORDER')
		self.po_header.grid(row = 0, column = 0, columnspan = 2, padx = 20, pady = 10)

		# PRICE FIELDS
		for i, param in enumerate(po_params):
			self.po_label = ctk.CTkLabel(self.po_frame, text = param)
			self.po_label.grid(row = i + 1, column = 0, padx = 20, pady = 10)
			self.po_field = ctk.CTkEntry(self.po_frame)
			self.po_field.grid(row = i + 1, column = 1, padx = 20, pady = 10)
			self._pending_order_params.append((self.po_field))

		self.blim_button = ctk.CTkButton(self.po_frame, text ='Buy Limit', 
			command = lambda order_type = 'Buy Limit': self.send_pending_order(order_type))
		self.blim_button.grid(row = 4, column = 1, padx = 20, pady = 10)

		self.slim_button = ctk.CTkButton(self.po_frame, text = 'Sell Limit', 
			command = lambda order_type = 'Sell Limit' : self.send_pending_order(order_type))
		self.slim_button.grid(row = 4, column = 0, padx = 20, pady = 10)

		# Market Order Column
		self.manual_trading_frame = ctk.CTkFrame(self.symbol_frame)
		self.manual_trading_frame.grid(row = 1, column = 1, padx = 10, pady = 10)
		self.manual_trading_frame.grid_rowconfigure(4, weight = 1)

		self.manual_header = ctk.CTkLabel(self.manual_trading_frame, text = 'MARKET ORDER')
		self.manual_header.grid(row = 0, column = 0, columnspan = 2, padx = 20, pady = 10)




	# Buy Limit Sell Limit
	def send_pending_order(self, order_type: str):
		# Processing order form

		# Creates a list containing trade info to send to trade handler
		order_params = [self.symbols_dropdown.get(), order_type, 'Pending']
		
		for order in self._pending_order_params:
			price = float(order.get()) if order.get() != '' else 0
			order_params.append(price)

		# Process order send
		print(order_params)
		pending_order = Trade_Package(order_params) # repackaging

		'''
		Trade handler class, explore possibility of creating class instance 
		on init instead of internally.
		'''
		trade_handler = Trade_Handler()

		# Sends packaged order parameters to MT5 event handler
		trade_handler.send_order(pending_order, self.mt5_py) 


	# STRATEGY SWITCH
	def toggle_strat(self, button_index):

		obj = self._strat_elements[button_index]
		button = obj[0] # button
		toggled_strat = obj[1] # strategy object

		# shortened for readability
 
		toggled_strat.toggle_strat(button.get()) # toggle strat

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

	def update_account_data(self, data):

	# General Helper function for updating left sidebar (Can be called on change account)
		[self._sidebar_elements[i][1].configure(text = info_data) for i, info_data in enumerate(data)]

	def launch_mt5(self):

		# Launch MT5
		if self.mt5_py.launch_mt5():
			name, num, brkr, bal = self.mt5_py.fetch_account_info()
			self.update_account_data((num, brkr, bal)) # Updates account data on left sidebar
			self._symbols_list = self.mt5_py.fetch_symbols()
			print('launch symbols: ', self._symbols_list)

			self.tab_func() # Updates table elements on MT5 Launch
			

	def change_account_popup(self):

		# Creates Login popup window
		# TODO: Disable root window if this enabled (DONE)
		if self._loginWindow is None or not self._loginWindow.winfo_exists():		
			self._loginWindow = LoginWindow()
			self.lock_popup(self._loginWindow)
		else:
			self.loginWindow.focus()

	def cfg_popup(self):

		# Create Settings popup window
		if self._cfgWindow is None or not self._cfgWindow.winfo_exists():
			self._cfgWindow = CfgWindow()
			self.lock_popup(self._cfgWindow)
		else:
			self._cfgWindow.focus()

	def abt_popup(self):

		# Create about popup window
		if self._abtWindow is None or not self._abtWindow.winfo_exists():
			self._abtWindow = AbtWindow()
			self.lock_popup(self._abtWindow)
		else:
			self._abtWindow.focus()

	def lock_popup(self, window):

		window.attributes('-topmost','true')
		window.grab_set()

if __name__ == "__main__":
	
	
	app = App()
	app.mainloop()