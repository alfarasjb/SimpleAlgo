


class Trade_Package():
	"""
	Trade_Package - Holds a trade template containing required trade information.
	
	...
	Attributes
	----------
	src: str
		Source of order: Manual Trading or Alpha
		Used for logging

	symbol: str
		Order Symbol
		MT5 Request Key: symbol

	price: float
		Order Open Price (0 for market order)
		MT5 Request Key: price

	sl: float
		Order Stop Loss (0 for no stop loss)
		MT5 Request Key: tp
		
	tp: float
		Order Take Profit (0 for no take profit)
		MT5 Request Key: tp

	comment: str
		Comment: Source Algo or Manual Trading
		MT5 Request Key: comment
		
	order_type: str
		Order Type: (Buy Limit, Sell Limit, Market Buy, Market Sell)
		MT5 Request Key: type

	volume: float
		Trade Volume
		MT5 Request Key: volume

	deal: str
		Deal Type: (Pending, Market)
		MT5 Request Key: action

	magic: int
		Magic Number
		MT5 Request Key: magic
	"""


	def __init__(self, 
	      src: str,
		  symbol: str,
		  price: float,
		  sl: float,
		  tp: float,
		  comment: str,
		  order_type: str,
		  volume: float, 
		  deal: str,
		  magic: int, 
		  attribs: list = []):
		
		### REVISION 
		self.order_source = src 
		self.order_symbol = symbol 
		self.order_price = price 
		self.order_sl = sl 
		self.order_tp = tp 
		self.order_comment = comment 
		self.order_type = order_type 
		self.order_volume = volume 
		self.order_deal = deal 
		self.order_magic = magic