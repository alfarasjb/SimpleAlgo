import customtkinter as ctk


'''
LoginWindow
login form mt5 account

'''


class LoginWindow(ctk.CTkToplevel):
	def __init__(self):
		super().__init__()

		self.title('Login')
		self.geometry('310x200')
		self.maxsize(310, 200)

		self.acct_num = ''
		self.pwd = ''
		self.broker = ''
		
		self.inv_login_label = None

		self.acct_num_label = ctk.CTkLabel(self, text = 'Account Number: ', fg_color = 'transparent')
		self.acct_num_label.place(x = 20, y = 10)

		self.acct_num_entry = ctk.CTkEntry(self)
		self.acct_num_entry.place(x = 150, y = 10)

		self.pwd_label = ctk.CTkLabel(self, text = 'Password: ', fg_color = 'transparent')
		self.pwd_label.place(x = 20, y = 50)

		self.pwd_entry = ctk.CTkEntry(self, show = '*')
		self.pwd_entry.place(x = 150, y = 50)

		self.broker_label = ctk.CTkLabel(self, text = 'Broker: ', fg_color = 'transparent')
		self.broker_label.place(x = 20, y = 90)

		self.broker_dropdown = ctk.CTkOptionMenu(
			self, values = ['IC Markets', 'EightCap', 'Pepperstone'])
		self.broker_dropdown.place(x = 150, y = 90)


		self.confirm_button = ctk.CTkButton(self, text = 'Login', width = 270, command = self.close)
		self.confirm_button.place(x = 20, y = 130)


	def close(self):
		acct_num = self.acct_num_entry.get()
		pwd = self.pwd_entry.get()
		broker = self.broker_dropdown.get()	

		info.update_vals(acct_num, pwd, broker)
		# valid entry
		# acct num > 6
		# pwd > 6
		if (len(info.acct_num) > 6 and len(info.pwd) > 6):
			self.destroy()	
		else:
			if self.inv_login_label is None:
				self.inv_login_label = ctk.CTkLabel(self, text = 'INVALID LOGIN', text_color = 'red')
				self.inv_login_label.pack(side = tkinter.BOTTOM, pady = (0, 5))

			print('Invalid Login')
