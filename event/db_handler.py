


'''
Custom class for receiving trade data from trade handler 

Receives successfully executed trade / order and stores in to sql db 

HANDLES SQL AND CSV


Attributes:


Methods:


'''


import sqlalchemy as db
import pandas as pd
from datetime import datetime as dt


class DB_Handler():
	"""
	Handles and manages queries to SQL database.
	"""
	def __init__(self):
		database = 'pyalgo' # put this in a different file
		password = '123456789' # put this in a different file
		self.engine = db.create_engine(f'mysql://root:{password}@localhost:3306/{database}') # if database is sql (settings)
		self.connection = self.engine.connect() # if database is sql

	def fetch_sql(self, table: str) -> pd.DataFrame:
		# Fetch is called everytime trade handler wants to store to db (execution or closed)
		# args: table 

		from_sql = pd.read_sql(f'SELECT * FROM {table}', self.engine, index_col = 'TradeID')
		from_sql['Date'] = pd.to_datetime(from_sql['Date'])
		#from_sql = from_sql.set_index('Date')

		return from_sql # DataFrame
		


	def store_sql(self, type: str, order_form: list) -> bool:
		# args: order in list form, table name to append
		# types: execution or closed
		# items = [date, 123456, 'Buy', 'GBPUSD', price, price, price, 0.01]
		table = 'executed_trades' if type == 'execution' else 'closed_trades'
		from_sql = self.fetch_sql(table)

		# construct dataframe to store to sql
		cols = from_sql.columns
		items = [order_form]
		df = pd.DataFrame(data = items, columns = cols)
		main = pd.concat([from_sql, df])
		val = main.to_sql(table, self.engine, if_exists = 'replace', index = 'TradeID')

		return True if val is not None else False