
import MetaTrader5 as mt5
import logging
from datetime import datetime as dt
import numpy as np
# Local Imports

import templates
import event

_log = logging.getLogger(__name__)

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
	"""Main class for handling trade operations.

	...

	Methods
	-------
	send_order() - Send order to MT5_Py Class
	close_trade()
	close_pos() - Closes Trades
	store_to_csv() - Stores filled trade to CSV
	store_to_sql() - Stores filled trade to SQL database

	"""


	def __init__(self):

		self.mt5_object = event.mt5_py
		#self.db = event.db # temporarily disabled

		self.__source = 'TRADE HANDLER'
		self.active_magic = []

	def send_order(self, trade: templates.Trade_Package):
		"""Method for sending order via MT5_Py
		
		Parameters
		----------
		trade: Trade_Package
			trade package object, converted to request dict accepted by MT5 class

		Returns
		-------
		bool - false if trade failed

		Notes 
		-----
		1. Run mt5.symbol_select
			this adds symbol to market watch (trade would fail otherwise)
			provides access to tick data

		2. Building Trade Request:
			keys: description
			action: 
				TRADE_ACTION_DEAL - market order
				TRADE_ACTION_PENDING - pending order
				TRADE_ACTION_SLTP - change sl/tp
				TRADE_ACTION_MODIFY - change parameters of prev placed order
				TRADE_ACTION_REMOVE - remove pending order
		
		"""
		
		_log.info('%s : Processing Order', self.__source)

		# REQUIRED: To access tick data, must add symbol to market watch 
		# DO NOT TOUCH THIS LINE
		selected = mt5.symbol_select(trade.order_symbol)
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

		# ===== MAIN REQUEST TEMPLATE ===== # 
		order_action = deal_converter[trade.order_deal]
		symbol = trade.order_symbol
		order_type = order_converter[trade.order_type]

		if trade.order_deal == 'Pending':
			price = trade.order_price

		elif trade.order_deal == 'Market':
			if trade.order_type == 'Market Buy':
				price = mt5.symbol_info_tick(trade.order_symbol).ask

			elif trade.order_type == 'Market Sell':
				price = mt5.symbol_info_tick(trade.order_symbol).bid

		request = {
		    'action' : order_action,
		    'symbol' : symbol,
		    'volume' : trade.order_volume,
		    'type' : order_type,
		    'price' : float(price),
		    'sl' : float(trade.order_sl),
		    'tp' : float(trade.order_tp),
		    'deviation' : 30, #slippage
		    'magic' : trade.order_magic,
		    'comment' : trade.order_comment,
		    'type_time' : mt5.ORDER_TIME_GTC,
		    'type_filling' : mt5.ORDER_FILLING_IOC
		}
		# ===== MAIN REQUEST TEMPLATE ===== #

		# BUY AT ASK, SELL AT BID
		# PROCESS RETURN TYPE FROM ORDER REQUEST
		# IF ORDER IS SUCCESSFUL, STORE TO SQL AND RETURN SUCCESS
		# RETURN WILL BE RECEIVED BY STRATEGY
		# LOG SUCCESSFUL TRADE
		order_request = self.mt5_object.send_order(request)
		if order_request.retcode == mt5.TRADE_RETCODE_DONE:
			# return trade format
			# migrated trade validation from mt5 class
			_log.info('%s : Order Filled', self.__source)
			sql = self.store_to_sql(order_request, trade.order_source)
			if sql:	
				_log.info('%s : Updated SQL DB', self.__source)
				return True
			else:
				_log.info('%s : Failed to update SQL DB', self.__source)
				return False
		else:
			_log.info('%s : Order Failed. Code: %i', self.__source, order_request.retcode)
			return False
	
	def close_trade(self, trade: templates.Trade_Package):
		"""
		Returns
		-------
		bool
		"""
		# what to close
		# incoming order if sell, close buys and vice versa
		# how to process closing
		_log.info('%s : Closing Trades', self.__source)
		action = mt5.TRADE_ACTION_DEAL
		symbol = trade.order_symbol
		positions = mt5.positions_get(symbol = symbol)
		order_type = mt5.ORDER_TYPE_SELL if trade.order_type == 'Market Sell' else mt5.ORDER_TYPE_BUY
		close_price = mt5.symbol_info_tick(symbol).bid if trade.order_type == 'Market Sell' else \
			mt5.symbol_info_tick(symbol).ask
		deviation = 30 
		'''
		FIXED
		order type
		price
		deviation
		magic
		comment
		type time
		fillinf

		DYNAMIC
		volume
		ticket
		'''
		# volume fetch from each trade
		# order type: opposite to trade.order_type
		# position: ticket
		# price : bid for closing buys, ask for closing sells
		# deviation: slippage
		# magic: fetch from each trade
		# comment: close
		# type time: gtc
		# filling: return or ioc
		for position in positions:
			# iterate through open positions
			# send request, successful close create a vector, to send to trade handler for sql
			order = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_SELL else mt5.ORDER_TYPE_BUY 
			close_price = mt5.symbol_info_tick(symbol).bid if trade.order_type == 'Market Sell' else \
				mt5.symbol_info_tick(symbol).ask
			request = {
				'action' : action,
				'symbol' : symbol,
				'volume' : position.volume,
				'type' : order_type,
				'position' : position.ticket,
				'price' : close_price,
				'deviation' : deviation,
				'magic' : position.magic,
				'comment' : 'Close',
				'type_time' : mt5.ORDER_TIME_GTC,
				'type_filling' : mt5.ORDER_FILLING_IOC
			}
			
			#if position.type != order_type:
			close_request = self.mt5_object.send_order(request)

		return True


	def close_pos(self, symbol: str, strat_comment: str = ''):
		"""Closes trades for requested symbol

		Parameters
		----------
		symbol: str
			Orders on this symbol will be closed. Requested by strategy.
		
		"""
		_log.info('%s : Closing Trades', self.__source)
		action = mt5.TRADE_ACTION_DEAL
		symbol = symbol
		positions = mt5.positions_get(symbol = symbol)
		deviation = 30

		for position in positions:
			if position.type == mt5.ORDER_TYPE_SELL:
				order_type = mt5.ORDER_TYPE_BUY
				close_price = mt5.symbol_info_tick(symbol).ask  
			elif position.type == mt5.ORDER_TYPE_BUY:
				order_type = mt5.ORDER_TYPE_SELL 
				close_price = mt5.symbol_info_tick(symbol).bid

			if position.comment != strat_comment:
				continue 

			request = {
				'action' : action,
				'symbol' : symbol,
				'volume' : position.volume,
				'type' : order_type,
				'position' : position.ticket,
				'price' : close_price,
				'deviation' : deviation,
				'magic' : position.magic,
				'comment' : 'Close',
				'type_time' : mt5.ORDER_TIME_GTC,
				'type_filling' : mt5.ORDER_FILLING_IOC
			}
			
			#if position.type != order_type:
			close_request = self.mt5_object.send_order(request)

	def store_to_csv(self):
		"""Stores trade to CSV
		"""
		# send info to csv
		# create csv storage class, use pandas to process
		# create a dataframe and append to csv
		raise NotImplementedError

	def store_to_sql(self, order: mt5.OrderSendResult, src: str):
		"""Stores trade to SQL Database

		Parameters
		----------
		order: mt5.OrderSendResult
			Stores to SQL if trade is filled.

		src: str
			Strategy that called this trade

		Returns
		-------
		bool - True if successfully executed

		Notes
		-----
		Temporarily Disabled
		"""
		# send info to db handler
		
		format = '%Y-%m-%d %H:%M:%S'
		date = dt.now().strftime(format)
		order_converter = {
			0 : 'Buy',
			1 : 'Sell',
			2 : 'Buy Limit',
			3 : 'Sell Limit'
		}
		items = [src, date, order.order, order.request.symbol, order_converter[order.request.order], order.price, order.request.sl, order.request.tp, order.volume]
		# TEMPORARILY DISABLED
		#sql = self.db.store_sql('execution', items)
		
		return True
	
	def register_magic(self, alpha):
		# checks pool for registered magic number
		# generate magic number
		while True:
			magic = np.random.randint(100000, 999999, 1)
			if magic not in self.active_magic:
				self.active_magic.append(magic)
				_log.info('%s : Registered Magic Number %i for %s', self.__source, magic, alpha)
				return magic[0]
			 

	def remove_magic(self, magic, alpha):
		self.active_magic.remove(magic)
		_log.info('%s : Removed Magic Number %i for %s', self.__source, magic, alpha)
			
		# call this when strategy is removed from table
	


	### ======= PROVISIONAL ======= ###

	def close_by_order_package(self, order_package: templates.Trade_Package):
    		
		### NOT WORKING !! ###
		_log.info('%s : Closing Trades', self.__source)
		action = mt5.TRADE_ACTION_DEAL
		positions = mt5.positions_get()

		for position in positions:
			pass

	def close_all_by_magic(self, magic_number: int):
    	### WORKING ###
		_log.info('%s : Closing Trades by Magic', self.__source)
		action = mt5.TRADE_ACTION_DEAL
		#symbol = symbol
		positions = mt5.positions_get()
		deviation = 30

		for position in positions:
    		
			if position.magic != magic_number:
					continue

			if position.type == mt5.ORDER_TYPE_SELL:
				order_type = mt5.ORDER_TYPE_BUY
				close_price = mt5.symbol_info_tick(position.symbol).ask  

			elif position.type == mt5.ORDER_TYPE_BUY:
				order_type = mt5.ORDER_TYPE_SELL 
				close_price = mt5.symbol_info_tick(position.symbol).bid



			request = {
				'action' : action,
				'symbol' : position.symbol,
				'volume' : position.volume,
				'type' : order_type,
				'position' : position.ticket,
				'price' : close_price,
				'deviation' : deviation,
				'magic' : position.magic,
				'comment' : 'Close',
				'type_time' : mt5.ORDER_TIME_GTC,
				'type_filling' : mt5.ORDER_FILLING_IOC
			}
			
			#if position.type != order_type:
			close_request = self.mt5_object.send_order(request)