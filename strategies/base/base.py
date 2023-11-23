import logging
from threading import Thread, Event 
from datetime import datetime as dt
from datetime import timezone as tz
from datetime import timedelta
import MetaTrader5 as mt5
import event
import pytz

_log = logging.getLogger(__name__)

tf_converter = {
	'm1' : 1, 
	'm5' : 5,
	'm15' : 15,
	'm30' : 30,
	'h1' : 60,
}

class Base:
	"""Strategy Base Class

	...

	Methods
	-------
	log() - Logging method

	toggle_strat_state() - Toggles strategy (enabled or disabled)

	request_data() - Requests data from MT5 Class

	get_next_interval() - Get next interval based on timeframe
	"""


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

		self.magic = 0

	def log(self, message: str):
		"""Logging Method

		Parameters
		----------
		message: str
			Message to print on logs
		"""
		

		# LOGGING
		assert type(message) == str, 'Invalid Message Type'
		try:
			_log.info('Server: %s | ALPHA: %s | SYMBOL: %s | TIMEFRAME: %s | %s', self.get_last_server_timestamp().strftime('%H:%M'), self.name, self.symbol, self.timeframe, message)
		except ConnectionError:
			_log.info('NOT CONNECTED TO MT5')

	def toggle_strat_state(self, value: bool):
		"""Enables/disables trading on this strategy

		Parameters
		----------
		value: bool 
			Strategy enabled or disabled
		"""
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
				#self.running_thread.join()
				self.threads.clear()
				self.log('THREAD CLEARED')

		else:
			raise ValueError('Invalid Switch Value')

	def request_data(self, tf: str = '', request_type: str = 'pos', start_index: int = 0, num_bars: int = 1, start_date: str = '', end_date: str = ''):
		"""Requests price data from MT5_Py Class

		Parameters
		----------
		request_type: str
			Default: 'pos'

			option for requesting data from mt5 (pos, date, rates)

			pos - fetch based on position
			date - fetch based on start date 
			rates - fetch based on date range
		
		start_index: int
			Default: 1

			start index for requesting data from mt5. used when 'pos' is 
			selected as request_type

		num_bars: int
			Default: 1 

			number of bars to receive. used when selecting 'pos' or 'date'
			as request_type.

		start_date: str
			Default: None

			start date for requesting data from mt5. used when selecting
			'date' or 'rates' as request_type.

		end_date: str
			Default: None

			end date for requesting data from mt5. used when 'rates' is 
			selected as request_type

		Returns
		-------
		list -> list of received data or None
		"""
		timeframe = self.timeframe if tf == '' else tf
		ohlc_list = self.mt5.request_price_data(timeframe = timeframe, 
			symbol = self.symbol, request_type = request_type, start_date = start_date, end_date = end_date,
			start_index = start_index, num_bars = num_bars)
		if ohlc_list is None:
			return None
		return ohlc_list

	def get_next_interval(self):
		"""Get next time interval for price data request

		Returns
		-------
		dt -> next_interval
			Local Time of next interval

		int -> ts
			Timestamp of next interval (Local)

		dt -> server_time
			Server time of next interval
		"""
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
		if not self.mt5.is_connected():
			print('fetching server time from calculation')
			server_time = utc_now + timedelta(hours = 3)
			server_time = server_time.replace(minute = min, second = 0, microsecond = 0)
		else:	
			print('fetching server time from terminal')
			timezone = pytz.timezone('Etc/UTC')
			last_server_datetime = dt.fromtimestamp(mt5.symbol_info(self.symbol)._asdict()['time'], tz = timezone)
			svr_hours = last_server_datetime.hour - 8

			if svr_hours < 0:
				svr_hours += 24
			if min == 0: 
				svr_hours += 1
			
			last_server_time = last_server_datetime.replace(hour = last_server_datetime.hour, second = 0, microsecond = 0)
			server_time = last_server_time.replace(minute = min)
		return next_interval, ts, server_time
	

	def start_thread(self, loop_function: callable):
		"""Starts algo thread

		Parameters
		---------
		loop_function: callable
			Thread target function, algo main loop function		
		"""
		self.log('STARTING THREAD')
		self.running_thread = Thread(target = loop_function, daemon = True)
		self.running_thread.start()
		self.threads.append(self.running_thread)

	### ====== PROVISIONAL ====== ### 
	def get_last_server_timestamp(self):
		if not self.mt5.is_connected():
			raise ConnectionError
		
		timezone = pytz.timezone('Etc/UTC')
		last_timestamp = dt.fromtimestamp(mt5.symbol_info(self.symbol)._asdict()['time'], tz = timezone)
		last_server_time = dt.now().replace(hour = last_timestamp.hour, second = 0, microsecond = 0)
	
		return last_server_time
