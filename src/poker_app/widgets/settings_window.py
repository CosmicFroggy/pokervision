import tkinter as tk


class SettingsWindow(tk.Toplevel):
	"""
	Pop-out window used to adjust the settings.
	"""

	def __init__(self, app, master):
		"""
		Initialise instance of SettingsWindow.
		
		Args:
			app (App): Reference to main App instance.
			master (some tk object): The parent of the SettingsWindow.
		"""

		super().__init__(master)
		self.app = app
		self.master = master
		self.title("Settings")
		self.geometry("200x600")

		#disable settings menu button
		self.app.menu_bar.entryconfig("Settings", state="disabled")

		# reenable it on close
		self.protocol("WM_DELETE_WINDOW", lambda: self.close())

		# layout
		tk.Label(self, text="Autofocus").pack()
		tk.Checkbutton(self, 
				       variable=self.app.settings["CAMERA"]["AUTOFOCUS"][0],
					   onvalue=1, offvalue=0, command= lambda : self.app.setting_update_notify("CAMERA", "AUTOFOCUS")).pack()
		
		tk.Label(self, text="Focus").pack()
		tk.Scale(self, from_=0, to=255, 
		   		 resolution=5, orient="horizontal", 
				 variable=self.app.settings["CAMERA"]["FOCUS"][0],
				 command= lambda _ : self.app.setting_update_notify("CAMERA", "FOCUS")).pack()
		
		tk.Label(self, text="Brightness").pack()
		tk.Scale(self, from_=0, to=255, 
		   		 resolution=5, orient="horizontal", 
				 variable=self.app.settings["CAMERA"]["BRIGHTNESS"][0], command= lambda _ : self.app.setting_update_notify("CAMERA", "BRIGHTNESS")).pack()
		
		# TODO: add settings for clustering to settings window

	def close(self):
		"""
		Close the window.
		"""

		self.app.menu_bar.entryconfig("Settings", state="normal")
		self.destroy()
