from time import sleep
from threading import Thread
import logging
import concurrent.futures
from datetime import datetime as dt


# Strategies will have a naming convention: Strat() class

class Strat():
	def __init__(self, enabled = False):
		# Required Attributes for strategy template
		self.name = 'Trend Follower'
		self.enabled = enabled
		self.timeframe = '' # timeframe (h1, h4, d1, w1, etc)
		self.symbols = [] # list of symbols to attach and request data

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
		self.ohlc = []
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
	def toggle_strat(self, value: bool):
		print('Toggle: ', value)
		self.enabled = value
		print('Enabled: ', self.enabled)

	def request_data(self):
		# request data helper function: performs mt5 queries
		pass 

	def send_order(self, order_package):
		# sends an order object (custom class) to trade handler class
		# expects to receive a confirmation that order was filled
		# store sent order on sql db 
		# returns a success or fail 
		pass

	def loop(self):
		# loop function, executes data request, processing, and send order 
		# runs on time intervals, depending on timeframe
		# trigger: time based
		# example, every 5 mins, if minutes = 5 or 0, trigger request, process, and send
		# condition: only 1 active position per algo per symbol
		# loop is called with thread
		if (dt.now().minute == 5):
			pass
		pass

	# ================= STRAT METHODS ===================# 
	# Build processing and packaging

	def process(self):
		# assumption: received data is last candle ohlc
		# processing: get last candle direction, and send similar order
		# ex: bullish: buy
		# order type: market order buy
		# all orders sent must be stored in sql db

		open_price = self.ohlc[0]
		close_price = self.ohlc[3]

		order_package = ''
		if close_price >= open_price:
			# long
			self.send_order(order_package)

		elif close_price < open_price:
			# short
			self.send_order(order_package)


'''
if __name__ == '__main__':
	pass
'''
