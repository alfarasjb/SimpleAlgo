import MetaTrader5 as mt5
from datetime import datetime as dt


# Local Imports
from templates.trade_template import Trade_Package


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


class MT5_Py():


	def __init__(self):

		self.path = 'C:/Program Files/MetaTrader 5 IC Markets (SC)/terminal64.exe'
		self.pl_hist = []
		self.symbols = self.fetch_symbols()


	def launch_mt5(self):

		print('Initializing MT5')
		if not mt5.initialize(path = self.path):
			print('MT5 failed to initialize. Code: ', mt5.last_error())
			return False
		else:
			print('MT5 initialized successfully.')
			self.fetch_account_info()
			return True


	def fetch_account_info(self):

		acct_info = mt5.account_info()
		acct_info = acct_info._asdict()
		# keys: login, server, balance, equity

		acct_num = acct_info['login']
		acct_server = acct_info['server']
		acct_name = acct_info['name']
		acct_bal = acct_info['balance']
		print(acct_num, acct_server)
		return acct_name, acct_num, acct_server, acct_bal

	def fetch_order_history(self):

		if mt5.account_info() == None:
			print('Not Connected')
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
		return headers, pl_hist

	def fetch_open_positions(self):
		# FETCH FROM MT5
		# Dummy data
		if mt5.account_info() == None:
			print('Not Connected')
			return None, None
		headers = ['ID', 'Ticket', 'Date Opened', 'Symbol', 'Order Type',
		'Open Price', 'Stop Loss', 'Take Profit', 'Open P/L']

		data = [[1, 12345, '10/16/2023', 'EURUSD', 'Buy', 1.05125, 1.05000, 1.05300, 100],
		[2, 12345, '10/16/2023', 'EURUSD', 'Buy', 1.05100, 1.05000, 1.05300, 100]]

		return headers, data[:10]

	def fetch_symbols(self):
		# Fetch symbols
		print('Fetch Symbols')
		fx_path = 'Majors'
		metals_path = 'Metals'
		if mt5.account_info() == None:
			print('Not Connected')
			return None
		symbols = mt5.symbols_get()
		ret_symbols = [symbol.name for symbol in symbols if (fx_path in symbol.path) or
		 (metals_path in symbol.path)]
		return ret_symbols
		
	def request_price_data(self):
		# requests price data from mt5 
		# returns price data
		# can receive list of symbols, process individually
		# may return a list of price data to return to strat
		# each individual strat may request different price data at different points in time
		pass


	def send_order(self, request_form: dict):
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
		


		order = mt5.order_send(request_form)