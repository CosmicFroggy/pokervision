import tkinter as tk

from widgets import SettingsWindow


class MenuBar(tk.Menu):
	def __init__(self, master):
		super().__init__(master)
		self.master = master

		# spawn the settings window when clicked
		self.add_command(label="Settings", command= lambda : SettingsWindow(master))