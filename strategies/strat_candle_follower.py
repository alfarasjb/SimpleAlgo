from time import sleep
from threading import Thread
import logging
import concurrent.futures
from datetime import datetime as dt
from datetime import timezone as tz
from datetime import timedelta
import logging

import MetaTrader5 as mt5
import event
import templates

# Strategies will have a naming convention: Strat() class


_log = logging.getLogger(__name__)

tf_converter = {
	'm1' : 1, 
	'm5' : 5,
	'm15' : 15,
	'm30' : 30,
	'h1' : 60,
}



class Strat():


	def __init__(self, enabled: bool = False, timeframe: str = 'm5', symbol: str = 'BTCUSD'):
		# Required Attributes for strategy template
		self.name = 'Auto_Regression'
		self.enabled = enabled
		self.timeframe = timeframe # timeframe (h1, h4, d1, w1, etc)
		self.symbol = symbol # list of symbols to attach and request data
		self.mt5 = event.mt5_py
		self.trade_handler = event.trade_handler
		self.last_candle_date = None
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
	def toggle_strat_state(self, value: bool):

		self.enabled = value
		if self.enabled:
			_log.info('STRAT : %s Enabled', self.name)
			# Start thread
			self.start_strat() # Triggers Thread
		elif not self.enabled:
			_log.info('STRAT : %s Disabled', self.name)

	def request_data(self, datetime):
		# request data helper function: performs mt5 queries

		

		ohlc_list = self.mt5.request_price_data(self.timeframe, 
			self.symbol, 'date', datetime)
		if ohlc_list is None:
			return None
		return ohlc_list
		#print(f'{date} {o} {h} {l} {c}')


	def send_order(self, order_package):
		# sends an order object (custom class) to trade handler class
		# expects to receive a confirmation that order was filled
		# store sent order on sql db 
		# returns a success or fail 

		# IF ORDER IS EXECUTED SUCCESSFULLY
		_log.info('STRAT : %s - ORDER FILLED', self.name)

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

		'''
		Solutions for data request:
		1. request with fixed time: get timestamp of last data, 
		compare with current datetime, increment based on timeframe,
		pass result datetime as argument to request_data function
		'''

		
		while self.enabled:
			utc_now = dt.now(tz.utc)
			if utc_now.second == 0:
				if (utc_now.minute % divisor == 0):
					server_time = utc_now + timedelta(hours = 3) - timedelta(minutes = divisor)
					
					data = self.request_data(server_time)
				#if data is not None:
					self.process(data)
					sleep(sleep_time)

		_log.info('STRAT : %s Ending Thread', self.name)

	def start_strat(self):
		# start thread here
		_log.info('STRAT : %s Starting Thread', self.name)
		Thread(target = self.loop).start()

	# ================= STRAT METHODS ===================# 
	# Build processing and packaging

	def process(self, data: list):
		# assumption: received data is last candle ohlc
		# processing: get last candle direction, and send similar order
		# ex: bullish: buy
		# order type: market order buy
		# all orders sent must be stored in sql db
		_log.info('STRAT : %s Processing OHLC', self.name)
		open_price = data[1]
		close_price = data[4]

		#order_package = ''
		# MUST PASS RISK MANAGEMENT FIRST
		if close_price >= open_price:
			# long
			#self.send_order(order_package)
			_log.info('STRAT : %s LONG ', self.name)
			order_form = [self.name, self.symbol, 'Market Buy', 'Market', 0, 0.0, 0.0, 0.01]
			# PACKAGING
			order_package = templates.Trade_Package(order_form)
			self.trade_handler.close_trade(order_package)
			self.trade_handler.send_order(order_package)

		elif close_price < open_price:
			# short
			#self.send_order(order_package)
			_log.info('STRAT : %s SHORT ', self.name)
			order_form = [self.name, self.symbol, 'Market Sell', 'Market', 0, 0.0, 0.0, 0.01]

			order_package = templates.Trade_Package(order_form)

			# if market sell, close all buys
			# iterate through all active orders
			self.trade_handler.close_trade(order_package)
			self.trade_handler.send_order(order_package)



'''
if __name__ == '__main__':
	pass
'''
