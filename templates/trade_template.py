
'''
Custom Class - Trade Package
- receives a list of data and reformats it into readable and easily accessible attributes

'''

class Trade_Package():


	def __init__(self, attribs: list):
		# pass in a list of len = 5
		self.__order_keys = ['Symbol', 'Order Type', 'Comment', 'Price', 'SL', 'TP']
		self.__order_values = attribs

		self.__order_dict = {k:v for k, v in zip(self.__order_keys, self.__order_values)}

		# Attributes to access by trade handler
		self.order_symbol = self.__order_dict['Symbol'] # Symbol to trade
		self.order_price = self.__order_dict['Price'] # Order Open Price (0 for market order)
		self.order_sl = self.__order_dict['SL'] # Order Sl (0 for no sl)
		self.order_tp = self.__order_dict['TP'] # Order TP (0 for no TP)
		self.order_comment = self.__order_dict['Comment'] # Comment (Source algo / manual trading)
		self.order_type = self.__order_dict['Order Type'] # Order Type (Buy, Sell, Buy Limit, Sell Limit)