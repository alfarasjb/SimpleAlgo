
class Account_Info():
	# handle account info from mt5
	def __init__(self, acct_num = '', pwd = '', broker = ''):
		self.acct_num = acct_num
		self.pwd = pwd
		self.broker = broker
		self.server = broker
		self.balance = ''
		self.equity = ''
		
	def update_vals(self, acct_num, pwd = '', broker = 'IC Markets'):
		self.acct_num = acct_num
		self.pwd = pwd
		self.broker = broker
		self.server = broker


