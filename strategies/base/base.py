import logging
from threading import Thread, Event 
from datetime import datetime as dt
from datetime import timezone as tz
from datetime import timedelta
import MetaTrader5 as mt5
import event

_log = logging.getLogger(__name__)

tf_converter = {
	'm1' : 1, 
	'm5' : 5,
	'm15' : 15,
	'm30' : 30,
	'h1' : 60,
}

class Base:


	def __init__(self, name: str, timeframe: str, symbol: str, enabled: bool):
		
		self.name = name
		self.timeframe = timeframe
		self.symbol = symbol
		self.enabled = enabled

		self.running_thread = None
		self.threads = []
		self.exit_event = Event()
		self.trade_handler = event.trade_handler

		self.mt5 = event.mt5_py
		self.divisor = tf_converter[self.timeframe]

	def log(self, message: str):
		# LOGGING
		assert type(message) == str, 'Invalid Message Type'
		_log.info('STRAT: %s | SYMBOL: %s | TIMEFRAME: %s | %s', self.name, self.symbol, self.timeframe, message)
		
	def toggle_strat_state(self, value: bool):
		# toggles strat state (enabled or disabled)
		assert type(value) == bool, 'Invalid Switch Type'
		self.enabled = value

		if self.enabled:
			self.log('STRATEGY ENABLED')
			self.exit_event = Event()

			if len(self.threads) == 0:
				self.start_strat()
			else:
				self.log('THREAD IS BUSY')

		elif not self.enabled:
			if len(self.threads) > 0:
				self.log('STRATEGY DISABLED')

				self.exit_event.set()
				self.running_thread.join()
				self.threads.clear()
				self.log('THREAD CLEARED')

		else:
			raise ValueError('Invalid Switch Value')

	def request_data(self, request_type: str = 'pos', start_index: int = 0, num_bars: int = 1, start_date: str = '', end_date: str = ''):
		# call mt5 

		ohlc_list = self.mt5.request_price_data(timeframe = self.timeframe, 
			symbol = self.symbol, request_type = request_type, start_date = start_date, 
			start_index = start_index, num_bars = num_bars)
		if ohlc_list is None:
			return None
		return ohlc_list

	def get_next_interval(self):
		# get next time interval for price data request
		# return time, and timestamp
		now = dt.now()
		utc_now = dt.now(tz.utc)
		min = now.minute

		while min % self.divisor != 0:
			min += 1 

		if min % self.divisor == 0 and min == now.minute:
			min += self.divisor 

		server_min = min - self.divisor # place server_min here to avoid issues with using different timeframes

		min = 0 if min == 60 else min 

		delta = timedelta(hours = 1) if min == 0 else timedelta(hours = 0)
		next_interval = now.replace(minute = min, second = 0, microsecond = 0)
		next_interval += delta 
		ts = int(next_interval.timestamp())


		#server_delta = self.divisor if now.second == 0 else 0
		
		#server_time = utc_now - timedelta(minutes = server_delta)
		server_time = utc_now + timedelta(hours = 3)
		server_time = server_time.replace(minute = server_min, second = 0, microsecond = 0)

		return next_interval, ts, server_time