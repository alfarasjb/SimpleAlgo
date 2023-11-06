import event

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
		self.signals_main = {}


	def request_data(self):
		pass 

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
		d_12, d_8, d_4, d_0 = [directions[i] for i in range(4)]
		h_12, h_8, h_4, h_0 = [data[i][2] for i in range(1, 5)]
		l_12, l_8, l_4, l_0 = [data[i][3] for i in range(1, 5)]

		if ((d_12 == d_8 == 1) and (h_12 > h_8)) or \
		((d_12 == d_8 == 0) and (l_8 > l_12)):
			self.signals_main[symbol] = 'counter'

		elif ((d_12 == 1 and d_8 == 0) and (h_12 > h_8)) or \
			((d_12 == 0 and d_8 == 1) and (l_8 > l_12)):
			self.signals_main[symbol] = 'external'



