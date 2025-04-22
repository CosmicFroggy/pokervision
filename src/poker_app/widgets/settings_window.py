import tkinter as tk


class SettingsWindow(tk.Toplevel):
	"""
	Pop-out window used to adjust the settings.
	"""

	def __init__(self, master):
		"""
		Initialise instance of SettingsWindow.
		
		Args:
			master (App, or similar tk object): The parent of the window.
		"""

		super().__init__(master)
		self.master = master
		self.title("Settings")
		self.geometry("200x600")

		#disable settings menu button
		self.master.menu_bar.entryconfig("Settings", state="disabled")

		# reenable it on close
		self.protocol("WM_DELETE_WINDOW", lambda: self.close())

		# layout
		tk.Label(self, text="Autofocus").pack()
		tk.Checkbutton(self, 
				       variable=self.master.settings["CAMERA"]["AUTOFOCUS"][0],
					   onvalue=1, offvalue=0, command= lambda : self.master.setting_update_notify("CAMERA", "AUTOFOCUS")).pack()
		
		tk.Label(self, text="Focus").pack()
		tk.Scale(self, from_=0, to=255, 
		   		 resolution=5, orient="horizontal", 
				 variable=self.master.settings["CAMERA"]["FOCUS"][0],
				 command= lambda _ : self.master.setting_update_notify("CAMERA", "FOCUS")).pack()
		
		tk.Label(self, text="Brightness").pack()
		tk.Scale(self, from_=0, to=255, 
		   		 resolution=5, orient="horizontal", 
				 variable=self.master.settings["CAMERA"]["BRIGHTNESS"][0], command= lambda _ : self.master.setting_update_notify("CAMERA", "BRIGHTNESS")).pack()
		
		# TODO: add settings for clustering to settings window

	def close(self):
		"""
		Close the window.
		"""

		self.master.menu_bar.entryconfig("Settings", state="normal")
		self.destroy()
