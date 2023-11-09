import customtkinter as ctk 
# Local Imports
import config

class AbtWindow(ctk.CTkToplevel):
	"""Creates window displaying project information

	Info
	----
	Project Details
	Github Repository

	Notes
	-----
	Not Finished
	"""
	def __init__(self):
		super().__init__()

		self.config = config.Load_Config()

		self.title(self.config._about)
		self.geometry(f'{self.config._about_resolution[0]}x{self.config._about_resolution[1]}')
		self.maxsize(self.config._about_resolution[0], self.config._about_resolution[1])
		self.minsize(self.config._about_resolution[0], self.config._about_resolution[1])