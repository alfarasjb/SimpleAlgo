import MetaTrader5 as mt5
from datetime import datetime as dt
import logging
import numpy as np 
import pandas as pd
# Local Imports
import templates
import config
'''
Custom MT5 Class for handling MT5 calls

ATTRIBUTES:
1. Path = MT5 executable path 
2. pl_hist = Profit / Loss history
3. Symbols = symbols in mt5 terminal


METHODS:
1. launch_mt5() - launches MT5 terminal
2. fetch_account_info() - fetches account info (acct num, server, balance, etc)
3. fetch_order_history() - cancelled orders
4. fetch_open_positions() - fetches current open positions
5. fetch_symbols() - fetches available symbols and stores in symbols attribute
6. request_price_data() - requests price data and returns it to algo
7. send_order() - trade request from order package from trade handler
'''

_log = logging.getLogger(__name__)




class MT5_Py():


	def __init__(self):

		self.__source = 'MT5'

		self.path = config.cfg._path
		#self.path = 'C:/Program Files/MetaTrader 5 IC Markets (SC)/terminal64.exe'
		self.pl_hist = []
		self.symbols = self.fetch_symbols()
		self.connection_status =  'Disconnected'
		self._algo_trading_enabled = False

		

		

	def launch_mt5(self):

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
    		
		if mt5.account_info() is None: 
			self.connection_status = 'Not Connected'
			return 'Not Connected'
		self.connection_status = 'Connected'
		return 'Connected'


	def fetch_account_info(self):

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
		end_date: dt = None, start_index: int = 1, num_bars: int = 1) -> list:
		# requests price data from mt5 
		# returns price data
		# can receive list of symbols, process individually
		# may return a list of price data to return to strat
		# each individual strat may request different price data at different points in time
		
		# GET BY INDEX
		#rates = mt5.copy_rates_from_pos('EURUSD', mt5.TIMEFRAME_D1, 0, 10)
		#print(rates)

		
		#print('MT5 TF: ', timeframe)
		#print('CONVERTED: ', timeframe_converter[timeframe])

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

		

		#print(rates)
		#print(rates.shape)
		#arr = np.array(rates)
		#arr[:, :1] = dt.fromtimestamp(arr[:, :1])
		#print(arr)

		# TRY: format rates into a numpy array,
		# columns to drop from last: 3
		# number of columns = arr.shape[1]
		# SLICE: arr[:,:arr.shape[1] - 3]

		data = pd.DataFrame(data = rates)
		data['time'] = pd.to_datetime(data['time'], unit = 's')
		data = data.loc[:, ['time', 'open', 'high', 'low', 'close']]
		arr = np.array(data)
		#rates = [list(rate) for rate in rates]
		#arr = np.array(rates)
		#arr = arr[:,:arr.shape[1] - 3]
		
		return arr


	def send_order(self, request_form: dict) -> mt5.OrderSendResult:
		'''
		expecting this function to be called from trade handler. 
		trade handler is the bridge from multiple algos to mt5. 
		algos send an order package to trade handler, and sent to this function 
		algo -> trade handler - > send_order

		returns confirmation to return to trade handler, uploads successful
		trade to sql db for storage

		TODO: 
		1. Execution validation: success / fail

		'''

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


