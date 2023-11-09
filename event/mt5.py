import MetaTrader5 as mt5
from datetime import datetime as dt
import logging
import numpy as np 
import pandas as pd
# Local Imports
import templates
import config

_log = logging.getLogger(__name__)




class MT5_Py():
	"""Main class for handling MT5 operations

	...

	Methods
	-------
	launch_mt5() - Launches MetaTrader5 terminal
	check_connection_status() - Checks connection status
	fetch_account_info() - Fetches account info (acct num, server, balance, etc.)
	fetch_order_history() - Fetches order history
	fetch_open_positions() - Fetches current open positions
	fetch_symbols() - Fetches symbols
	request_price_data() - Requests Price Data
	send_order() - Sends Order


	"""

	def __init__(self):

		self.__source = 'MT5'

		self.path = config.cfg._path
		#self.path = 'C:/Program Files/MetaTrader 5 IC Markets (SC)/terminal64.exe'
		self.pl_hist = []
		self.symbols = self.fetch_symbols()
		self.connection_status =  'Disconnected'
		self._algo_trading_enabled = False

		

		

	def launch_mt5(self):
		"""Launches MT5 Terminal

		Returns
		-------
		True - MT5 initialized successfully
		False - MT5 launch failed.
		
		"""
		_log.info('Launching MT5')
		if not mt5.initialize(path = self.path):
			_log.error('MT5 Failed to initialize. Code: ', mt5.last_error())
			return False
		else:
			_log.info('MT5 Initialized Successfully.')
			self.fetch_account_info()
			self.check_connection_status()
			return True
	
	def check_connection_status(self):
		"""Checks MT5 connection status

		Returns
		-------
		MT5 connection status
		"""
    		
		if mt5.account_info() is None: 
			self.connection_status = 'Not Connected'
			return 'Not Connected'
		self.connection_status = 'Connected'
		return 'Connected'


	def fetch_account_info(self):
		"""Fetches account info from mt5 terminal. 

		Returns
		-------
		acct_name - MT5 Account Name
		acct_num - MT5 Account Num
		acct_server - MT5 Server 
		acct_bal - Current Balance
		"""

		acct_info = mt5.account_info()
		acct_info = acct_info._asdict()
		# keys: login, server, balance, equity

		acct_num = acct_info['login']
		acct_server = acct_info['server']
		acct_name = acct_info['name']
		acct_bal = acct_info['balance']
		if acct_info is not None:
			_log.info('%s : Connected To MT5 Account %s, Server %s', self.__source, acct_num, acct_server)
			self.connection_status = 'Connected'
		return acct_name, acct_num, acct_server, acct_bal

	def fetch_order_history(self):
		"""Fetches order history from mt5

		Returns
		-------
		list -> list of order history
		
		"""

		if mt5.account_info() == None:
			_log.info('%s : Not Connected to MT5', self.__source)
			return None, None
		deals = mt5.history_deals_get(0, dt.now())
		deals = deals[::-1]

		# filter orders only with pl 
		pl_hist = []

		for deal in deals:
			if deal.entry == 1:
				ticket = deal.order
				time = dt.fromtimestamp(deal.time).date()
				symbol = deal.symbol
				deal_type = 'Buy' if deal.type == 1 else 'Sell'
				price = 1.21212
				sl = 1.21212
				tp = 1.21212
				pl = deal.profit
				pl_hist.append([ticket, time, symbol, deal_type, price, sl, tp, pl])

		headers = ['Ticket', 'Date Opened', 'Symbol', 'Order Type',
			'Open Price', 'Stop Loss', 'Take Profit', 'Closed P/L']

		# return pl_hist[:10] if only last 10 hist items
		return headers, pl_hist[:10]

	def fetch_open_positions(self):
		"""Fetches open positions from MT5. 

		Returns
		-------
		list -> Open positions from mt5

		Notes
		-----
		Not Finished
		"""
		# FETCH FROM MT5
		# Dummy data
		if mt5.account_info() == None:
			_log.info('%s : Not Connected to MT5', self.__source)
			return None, None
		headers = ['ID', 'Ticket', 'Date Opened', 'Symbol', 'Order Type',
		'Open Price', 'Stop Loss', 'Take Profit', 'Open P/L']

		data = [[1, 12345, '10/16/2023', 'EURUSD', 'Buy', 1.05125, 1.05000, 1.05300, 100],
		[2, 12345, '10/16/2023', 'EURUSD', 'Buy', 1.05100, 1.05000, 1.05300, 100]]

		return headers, data[:10]

	def fetch_symbols(self):
		"""Fetches symbols from mt5 history
		
		Returns
		-------
		None - if not connected to mt5 terminal
		Symbols List - requested symbols


		Notes
		-----
		Currently hard coded to request FX majors and metals.
		"""
		# Fetch symbols
		fx_path = 'Majors'
		metals_path = 'Metals'
		if mt5.account_info() == None:
			_log.info('%s : Not Connected to MT5', self.__source)
			return None
		symbols = mt5.symbols_get()
		ret_symbols = [symbol.name for symbol in symbols if (fx_path in symbol.path) or
		 (metals_path in symbol.path)]
		return ret_symbols
		

	def request_price_data(self, timeframe: str, 
		symbol: str, request_type: str = 'pos', 
		start_date: dt = None, 
		end_date: dt = None, start_index: int = 1, num_bars: int = 1):
		"""Requests price data from MT5. 

		Parameters
		----------
		timeframe : str
			timeframe for requested data(m1,m5,m15,m30,h1,h4,d1,w1,mn1)
		
		symbol : str
			symbol for requested data

		request_type : str 
			Default: 'pos'

			option for requesting data from mt5 (pos, date, rates)

			pos - fetch based on position
			date - fetch based on start date 
			rates - fetch based on date range
		
		start_date: dt
			Default: None

			start date for requesting data from mt5. used when selecting
			'date' or 'rates' as request_type.

		end_date: dt
			Default: None

			end date for requesting data from mt5. used when 'rates' is 
			selected as request_type

		start_index: int
			Default: 1

			start index for requesting data from mt5. used when 'pos' is 
			selected as request_type
		
		num_bars: int
			Default: 1 

			number of bars to receive. used when selecting 'pos' or 'date'
			as request_type.

		Return
		------
		list
			list of received data, or empty list 
		"""
		timeframe_converter = {
			'm1' : mt5.TIMEFRAME_M1,
			'm5' : mt5.TIMEFRAME_M5,
			'm15' : mt5.TIMEFRAME_M15,
			'm30' : mt5.TIMEFRAME_M30,
			'h1' : mt5.TIMEFRAME_H1,
			'h4' : mt5.TIMEFRAME_H4,
			'd1' : mt5.TIMEFRAME_D1,
			'w1' : mt5.TIMEFRAME_W1,
			'mn1' : mt5.TIMEFRAME_MN1,
		}
		tf = timeframe_converter[timeframe]
		if request_type == 'pos':
			rates = mt5.copy_rates_from_pos(symbol, tf, start_index, num_bars)

		elif request_type == 'date':
			rates = mt5.copy_rates_from(symbol, tf, start_date, num_bars)

		elif request_type == 'rates':
			rates = mt5.copy_rates_range(symbol, tf, start_date, end_date)

		if rates is None:
			return []

		data = pd.DataFrame(data = rates)
		data['time'] = pd.to_datetime(data['time'], unit = 's')
		data = data.loc[:, ['time', 'open', 'high', 'low', 'close']]
		arr = np.array(data)
		return arr


	def send_order(self, request_form: dict):
		"""Sends order

		Parameters
		----------
		request_form: dict
			request form for sending MT5 orders.
		
		Returns
		-------
		mt5.OrderSendResult
			results in either success or fail. 

		Notes
		-----
		This method should only be called Trade Handler, which bridges multiple algos to MT5.
		Algos send an 'Order Package' to trade handler, and sent to this function.
		Algo -> Trade Handler -> send_order
		"""

		if mt5.account_info() == None:
			_log.info('%s : Not Connected to MT5', self.__source)
			return None 


		_log.info('%s : Sending Order: %s', self.__source, request_form)
		if self._algo_trading_enabled == False:
			# RETURN FAILED TO SEND
			_log.info('%s : Failed to send order. Algo trading disabled', self.__source)
			
		order = mt5.order_send(request_form)
		if order == None:
			_log.info('%s : Failed to Send Order.', self.__source)
			_log.info('Code: ', mt5.last_error())



		return order


