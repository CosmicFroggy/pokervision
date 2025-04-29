import tkinter as tk

from poker_app.widgets import SettingsWindow


class MenuBar(tk.Menu):
	"""
	Menu bar used to access the settings window.
	"""

	def __init__(self, app, master):
		"""
		Initialise Instance of MenuBar.

		Args:
			app (App): Reference to main App instance.
			master (some tk object): The parent of the MenuBar.
		"""
		
		super().__init__(master)
		self.app = app
		self.master = master

		# spawn the settings window when clicked
		self.add_command(label="Settings", command= lambda : SettingsWindow(app, app))