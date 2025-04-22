import tkinter as tk

from widgets import SettingsWindow


class MenuBar(tk.Menu):
	"""
	Menu bar used to access the settings window.
	"""

	def __init__(self, master):
		"""
		Initialise Instance of MenuBar.

		Args:
			master (App, or similar tk object): The parent of the menu bar.
		"""
		
		super().__init__(master)
		self.master = master

		# spawn the settings window when clicked
		self.add_command(label="Settings", command= lambda : SettingsWindow(master))