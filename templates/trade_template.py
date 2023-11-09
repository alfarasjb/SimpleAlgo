


class Trade_Package():
	"""
	Trade_Package - Holds a trade template containing required trade information.
	"""


	def __init__(self, attribs: list):
		# pass in a list of len = 5
		self.__order_keys = ['Source', 'Symbol', 'Order Type', 'Deal', 'Comment', 'Price', 'SL', 'TP', 'Volume']
		self.__order_values = attribs

		self.__order_dict = {k:v for k, v in zip(self.__order_keys, self.__order_values)}

		# Attributes to access by trade handler
		self.order_source = self.__order_dict['Source'] # Source of order, manual trading / strategy
		self.order_symbol = self.__order_dict['Symbol'] # Symbol to trade
		self.order_price = self.__order_dict['Price'] # Order Open Price (0 for market order)
		self.order_sl = self.__order_dict['SL'] # Order Sl (0 for no sl)
		self.order_tp = self.__order_dict['TP'] # Order TP (0 for no TP)
		self.order_comment = self.__order_dict['Comment'] # Comment (Source algo / manual trading)
		self.order_type = self.__order_dict['Order Type'] # Order Type (Buy, Sell, Buy Limit, Sell Limit)
		self.order_volume = self.__order_dict['Volume'] # Order Volume
		self.order_deal = self.__order_dict['Deal'] # Order Deal