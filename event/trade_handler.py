
import MetaTrader5 as mt5

# Local Imports
from templates.trade_template import Trade_Package
from event.mt5 import MT5_Py



'''
Receives trades / orders from multiple algos, reformats, and sends to mt5

Expected input 
symbol, order type, price, sl, tp, comment (source algo: which algo called this trade)

packaging options: 
custom trade class(Trade_Package Class)

ATTRIBUTES:

METHODS
1. send_order() - converts from Trade_Package class to mt5 request format
2. store_to_sql() - stores executed trades to local sql server 

'''


class Trade_Handler():
	def __init__(self):
		pass

	def send_order(self, trade: Trade_Package, mt5_py: MT5_Py):

		order_converter = {
			'Buy Limit' : mt5.ORDER_TYPE_BUY_LIMIT,
			'Sell Limit' : mt5.ORDER_TYPE_SELL_LIMIT,
			'Market Buy' : mt5.ORDER_TYPE_BUY,
			'Market Sell' : mt5.ORDER_TYPE_SELL
		}

		deal_converter = {
			'Pending' : mt5.TRADE_ACTION_PENDING,
			'Market' : mt5.TRADE_ACTION_DEAL
		}

		'''
		BUILDING TRADE REQUEST
		keys : description

		action: 
			TRADE_ACTION_DEAL - market order
			TRADE_ACTION_PENDING - pending order
			TRADE_ACTION_SLTP - change sl/tp
			TRADE_ACTION_MODIFY - change parameters of prev placed order
			TRADE_ACTION_REMOVE - remove pending order
		'''
		request = {
		    'action' : deal_converter[trade.order_comment],
		    'symbol' : trade.order_symbol,
		    'volume' : 0.01,
		    'type' : order_converter[trade.order_type],
		    'price' : trade.order_price,
		    'sl' : trade.order_sl,
		    'tp' : trade.order_tp,
		    'deviation' : 30, #slippage
		    'magic' : 234564,
		    'comment' : trade.order_comment,
		    'type_time' : mt5.ORDER_TIME_GTC,
		    'type_filling' : mt5.ORDER_FILLING_IOC
		}
		mt5_py.send_order(request)


	def store_to_sql(self):
		# send info to db handler
		pass