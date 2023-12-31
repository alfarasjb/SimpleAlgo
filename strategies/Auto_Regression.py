from .base import Base
from threading import Thread
from datetime import datetime as dt, timezone as tz, timedelta
import pause

import templates
class Auto_Regression(Base):

	def __init__(self, symbol: str, timeframe: str, enabled: bool = False, volume: float = 0.01):
		super().__init__('Auto_Regression', timeframe, symbol, enabled)
		self.volume = volume
		self.magic = self.trade_handler.register_magic('Auto_Regression')
		
	def loop(self):

		while self.enabled:
			self.log('RUNNING LOOP')

			next_interval, ts, server = self.get_next_interval()
			pause.until(ts)

			if self.exit_event.is_set():
				break

			data = self.request_data(request_type = 'date', start_index = 1, 
				num_bars = 1, start_date = server)

			if len(data) > 0:
				self.process(data)

	def start_strat(self):

		self.log('STARTING THREAD')
		self.running_thread = Thread(target = self.loop, daemon = True)
		self.running_thread.start()
		self.threads.append(self.running_thread)

	def process(self, rcv_data):
		data = rcv_data[0] # first element of vector
		self.log('PROCESSING OHLC')
		open_price = data[1]
		close_price = data[4]
		comment = f'{self.name} | {self.timeframe}'

		if close_price > open_price:
			self.log('LONG')
			order_package = templates.Trade_Package(
				src = self.name,
				symbol = self.symbol,
				price = 0,
				sl = 0.0,
				tp = 0.0, 
				comment = comment,
				order_type = 'Market Buy',
				volume = self.volume,
				magic = self.magic,
				deal = 'Market'
			)
			self.trade_handler.close_pos(self.symbol)
			self.trade_handler.send_order(order_package)

		elif close_price <= open_price:
			self.log('SHORT')
			order_package = templates.Trade_Package(
				src = self.name,
				symbol = self.symbol,
				price = 0,
				sl = 0.0,
				tp = 0.0, 
				comment = comment,
				order_type = 'Market Sell',
				volume = self.volume,
				magic = self.magic,
				deal = 'Market'
			)
			self.trade_handler.close_pos(self.symbol)
			self.trade_handler.send_order(order_package)

		else:
			raise ValueError('Invalid Pricing')
