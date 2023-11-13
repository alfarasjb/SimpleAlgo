
from .base import Base
from threading import Thread
from datetime import datetime as dt 
from datetime import timezone as tz
from datetime import timedelta
import pause

class Trend_Follower(Base):


	def __init__(self, symbol: str, timeframe: str, enabled: bool = False, volume: float = 0.01):
		super().__init__('Trend_Follower', timeframe, symbol, enabled)
		

	def loop(self):

		while self.enabled:
			self.log('RUNNING LOOP')
				
			utc_now = dt.now(tz.utc)
			next_interval, ts, server = self.get_next_interval()
			pause.until(ts) #PAUSE HERE SO PROGRAM WILL NOT REQUEST ON FIRST PASS
			if self.exit_event.is_set():
				break	
			data = self.request_data(request_type = 'date', start_index = 1, num_bars = 3, start_date = server)

			if len(data) > 0:
				self.process(data)

			

	def start_strat(self):

		self.log('STARTING THREAD')
		self.running_thread = Thread(target = self.loop, daemon = True)
		self.running_thread.start()
		self.threads.append(self.running_thread)

	def process(self, data):
		self.log('PROCESS')
		print(data)
