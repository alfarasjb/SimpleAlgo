import customtkinter as ctk 


# Local Imports
from config.load_cfg import Load_Config


'''
About Window:
Project Details Here

1. Project Info
2. Repository

etc 

'''

class AbtWindow(ctk.CTkToplevel):
	def __init__(self):
		super().__init__()

		self.config = Load_Config()

		self.title(self.config._about)
		self.geometry(f'{self.config._about_resolution[0]}x{self.config._about_resolution[1]}')
		self.maxsize(self.config._about_resolution[0], self.config._about_resolution[1])
		self.minsize(self.config._about_resolution[0], self.config._about_resolution[1])