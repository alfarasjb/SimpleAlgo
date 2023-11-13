from time import sleep
from threading import Thread
from threading import Event
import logging
import concurrent.futures
from datetime import datetime as dt
from datetime import timezone as tz
from datetime import timedelta
import logging
import pause

import MetaTrader5 as mt5
import event
import templates

# Strategies will have a naming convention: Strat() class

### ===== TODO ===== ###
'''



### ===== COMPLETED ===== ###
- scheduler 
1. use dt.now to get current time
2. find the next timeframe period (ex: m5, next minute value divisble by 5)
3. use that specified time to use pause until.

'''

_log = logging.getLogger(__name__)

tf_converter = {
	'm1' : 1, 
	'm5' : 5,
	'm15' : 15,
	'm30' : 30,
	'h1' : 60,
}


class Auto_Regression_Original:


	def __init__(self, enabled: bool = False, timeframe: str = 'm5', symbol: str = 'BTCUSD', volume: float = 0.01):
		# Required Attributes for strategy template
		self.name = 'Auto_Regression'
		self.enabled = enabled
		self.timeframe = timeframe # timeframe (h1, h4, d1, w1, etc)
		self.symbol = symbol # list of symbols to attach and request data
		self.mt5 = event.mt5_py
		self.trade_handler = event.trade_handler
		self.last_candle_date = None
		
		self.running_thread = None
		self.threads = []
		self.exit_event = Event()

		format = '%y-%m-%d %H:%M:%S'
		_log.info('%s Instance Created for SYMBOL: %s, TIMEFRAME: %s', self.name, self.symbol, self.timeframe)
		'''
		TEMPLATE ATTRIBUTES
		1. name
		2. enabled


		required: 
		1. prev candle direction ( prev open & prev close)
		2. period / timeframe

		TODO: 
		1. process prev open and close
		2. process timeframe
		'''
	# Required Methods for strategy template
	'''
	Global Methods
	1. Toggle Strat
	2. Request Data
	3. Send Order


	Private Methods
	- Methods specific to strategy processing
	'''

	# ================== GLOBAL METHODS ===================== # 
	def log(self, message: str): 
		assert type(message) == str, 'Invalid Message Type'
		_log.info('STRAT : %s | SYMBOL: %s | TIMEFRAME: %s | %s', self.name, self.symbol, self.timeframe, message)

	def toggle_strat_state(self, value: bool):
		assert type(value) == bool, 'Invalid Switch Type'

		self.enabled = value
		if self.enabled:
			self.log('STRATEGY ENABLED')
			# Start thread
			self.exit_event = Event()
			if len(self.threads) == 0: 
				self.start_strat() # Triggers Thread
			else: 
				self.log('THREAD IS BUSY')
				

		elif not self.enabled:
			if len(self.threads) > 0:
				self.log('STRATEGY DISABLED')
				# KILL THREAD HERE
				self.exit_event.set()
				self.running_thread.join()
				self.threads.clear()
				self.log('THREAD CLEARED')

		else:
			raise ValueError('Invalid Switch Value')

	def request_data(self):
		# request data helper function: performs mt5 queries
		### === UPDATE === ### Request data using index (from datetime)
	

		ohlc_list = self.mt5.request_price_data(timeframe = self.timeframe, 
			symbol = self.symbol, request_type = 'pos', start_index = 1)
		if ohlc_list is None:
			return None

		return ohlc_list[0]


	def send_order(self, order_package):
		# sends an order object (custom class) to trade handler class
		# expects to receive a confirmation that order was filled
		# store sent order on sql db 
		# returns a success or fail 

		# IF ORDER IS EXECUTED SUCCESSFULLY
		self.log('ORDER FILLED')

		# ADD FILLED ORDER INFO TO LOG
		pass

	def loop(self):
		# loop function, executes data request, processing, and send order 
		# runs on time intervals, depending on timeframe
		# trigger: time based
		# example, every 5 mins, if minutes = 5 or 0, trigger request, process, and send
		# condition: only 1 active position per algo per symbol
		# loop is called with thread

		# do 1 call to get last candle
		# this will only run once to get a reference date
		# Test = One second loop
		divisor = tf_converter[self.timeframe]
		sleep_time = (divisor * 60) - 10

		# GET NEXT INTERVAL
		while self.enabled:
			self.log('RUNNING LOOP')
			
			utc_now = dt.now(tz.utc)
			next_interval, ts = self.get_next_interval()
			pause.until(ts)
			if self.exit_event.is_set():
				break
				
			data = self.request_data()	

			if len(data) > 0:
				self.process(data)
			
			# CALL PROCESS AS A THREAD

		self.log('ENDING THREAD')


	def get_next_interval(self):
		divisor = tf_converter[self.timeframe]
		now = dt.now()
		min = now.minute
		'''

		if min % divisor == 0 and min == now.minute:
			min += divisor 
			next_interval = now.replace(minute = min, second = 0, microsecond = 0)
			ts = int(next_interval.timestamp())
			return next_interval, ts

		while min % divisor != 0:
			min += 1

		next_interval = now.replace(minute = min, second = 0, microsecond = 0)
		ts = int(next_interval.timestamp())
		'''

		while min % divisor != 0:
			min += 1 

		if min % divisor == 0 and min == now.minute:
			min += divisor

		min = 0 if min == 60 else min 

		delta = timedelta(hours = 1) if min == 0 else timedelta(hours = 0)
		next_interval = now.replace(minute = min, second = 0, microsecond = 0)
		next_interval = next_interval + delta 
		ts = int(next_interval.timestamp())
		self.log(f'NEXT INTERVAL: {next_interval}')
		return next_interval, ts



	def start_strat(self):
		# start thread here
		self.log('STARTING THREAD')
		self.running_thread = Thread(target = self.loop, daemon = True)
		self.running_thread.start()
		self.threads.append(self.running_thread)
		## SOLUTION 2: Call loop, and create a thread in the loop function 

	# ================= STRAT METHODS ===================# 
	# Build processing and packaging

	def process(self, data: list):
		# assumption: received data is last candle ohlc
		# processing: get last candle direction, and send similar order
		# ex: bullish: buy
		# order type: market order buy
		# all orders sent must be stored in sql db
		#_log.info('STRAT : %s Processing OHLC | SYMBOL: %s | TIMEFRAME: %s', self.name, self.symbol, self.timeframe)
		self.log('PROCESSING OHLC')
		open_price = data[1]
		close_price = data[4]
		print('OPEN: ', open_price, ' CLOSE: ', close_price)
		#order_package = ''
		# MUST PASS RISK MANAGEMENT FIRST
		if close_price >= open_price:
			# long
			#self.send_order(order_package)
			#_log.info('STRAT : %s LONG | SYMBOL: %s | TIMEFRAME: %s', self.name, self.symbol, self.timeframe)
			self.log('LONG')
			order_form = [self.name, self.symbol, 'Market Buy', 'Market', 0, 0.0, 0.0, 0.01]
			# PACKAGING
			order_package = templates.Trade_Package(order_form)
			#self.trade_handler.close_trade(order_package)
			self.trade_handler.close_pos(self.symbol)
			self.trade_handler.send_order(order_package)

		elif close_price < open_price:
			# short
			#self.send_order(order_package)
			#_log.info('STRAT : %s SHORT | SYMBOL: %s | TIMEFRAME: %s', self.name, self.symbol, self.timeframe)
			self.log('SHORT')
			order_form = [self.name, self.symbol, 'Market Sell', 'Market', 0, 0.0, 0.0, 0.01]

			order_package = templates.Trade_Package(order_form)

			# if market sell, close all buys
			# iterate through all active orders
			#self.trade_handler.close_trade(order_package)
			self.trade_handler.close_pos(self.symbol)
			self.trade_handler.send_order(order_package)

		else:
			raise ValueError('Invalid Pricing')


'''
if __name__ == '__main__':
	pass
'''
