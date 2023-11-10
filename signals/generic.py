import event
import pandas as pd
from datetime import datetime as dt
'''
Methods: 
- Request Data from MT5 (Return a vector of shape (3, 4) 3 rows, 4 columns)
- Parse patterns based on predefined patterns
'''

patterns = {
	1 : 'counter',
	2 : 'internal',
	3 : 'external', 
	4 : 'fill',
	5 : 'follow'
}

class Signals:


	def __init__(self):

		self.mt5 = event.mt5_py
		self.patterns = []

	def update(self):
		pass

	def get_data(self):
		symbols =  ['EURUSD','AUDUSD','GBPUSD','USDCHF','USDCAD','USDJPY']

		if self.mt5.check_connection_status() == 'Not Connected':
			self.mt5.launch_mt5()
		
		for symbol in symbols:
			data = self.mt5.request_price_data(timeframe = 'h4', symbol = symbol, 
				      request_type = 'pos', start_index = 1, num_bars = 4)

			signals = self.parse_pattern(data, symbol)
			#[patter, bias, open]
			pat = Pattern(symbol, signals[0], signals[1], signals[2], signals[3].strftime("%Y-%m-%d %H:%M"))
			self.patterns.append(pat)

		return self.patterns

	def parse_pattern(self, data, symbol):
		# data is a vector
		# receive 0, 4, 8, 12
		directions = []

		for ohlc in data:
			# indexes: 0 - date, 1 - open, 2 - high, 3 - low, 4 - close
			o, h, l, c = [ohlc[i] for i in range(1, 5)]
			direction = 1 if c > o else 0  
			# 1 denotes long, 0 denotes short
			# review sequence  
			directions.append(direction)

		# expected output: 1d vector of integers = [1, 0, 0, 1]

		# conditions:
		d_0, d_4, d_8, d_12 = [directions[i] for i in range(4)]
		h_0, h_4, h_8, h_12 = [data[i][2] for i in range(4)]
		l_0, l_4, l_8, l_12 = [data[i][3] for i in range(4)]
		o_0, o_4, o_8, o_12 = [data[i][1] for i in range(4)]
		c_0, c_4, c_8, c_12 = [data[i][4] for i in range(4)]
		t_0, t_4, t_8, t_12 = [data[i][0] for i in range(4)]
		#data[i] = candle
		#data[i][0] = timestamp
		#print(dt.fromtimestamp(t_12))
		
		if ((d_8 == 1 and d_12 == 0 and l_12 > o_0)) or \
			((d_8 == 0 and d_12 == 1 and h_12 < o_0)):
			bias = 'Long' if d_12 == 1 else 'Short'
			return ['Fill', bias, o_0, t_12]
		
		elif((d_8 == 1 and d_12 == 0 and o_0 > l_12)) or \
			((d_8 == 0 and d_12 == 1 and h_12 > o_0)):
			bias = 'Short' if d_12 == 1 else 'Long'
			return ['Internal', bias, o_0, t_12]

		elif ((d_12 == d_8 == 1) and (h_12 > h_8)) or \
		((d_12 == d_8 == 0) and (l_8 > l_12)):
			bias = 'Short' if d_12 == 1 else 'Long'
			return ['Counter', bias, o_0, t_12]

		elif ((d_12 == 1 and d_8 == 0) and (h_12 > h_8)) or \
			((d_12 == 0 and d_8 == 1) and (l_8 > l_12)):
			bias = 'Short' if d_12 == 1 else 'Long'
			return ['External', bias, o_0, t_12]

		else:
			return ['Unknown', 'Unknown', o_0, t_12]



class Pattern:
	"""Pattern Object
	"""

	def __init__(self, symbol: str, pattern: str, bias: str, open: float, last_updated: str):
		self.symbol = symbol
		self.pattern = pattern
		self.bias = bias
		self.open = open
		self.last_updated = last_updated