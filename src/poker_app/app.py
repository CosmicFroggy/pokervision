import tkinter as tk
import cv2
from PIL import Image, ImageTk


from card_detection import analyse_frame


# main app class
class App:
	def __init__(self):
		self.root = tk.Tk()
		self.root.title("PokerVision")
		self.root.protocol("WM_DELETE_WINDOW", self.destroy)

		# create video panel
		self.video_panel = tk.Label(self.root)
		self.video_panel.pack()

		# create menu bar
		self.menu_bar = tk.Menu(self.root)
		self.menu_bar.add_command(label="Settings", command=self.open_settings_window)
		self.root.config(menu=self.menu_bar)

		# get camera feed
		self.cam = cv2.VideoCapture(0)

		# camera settings TODO: pull these from config file
		self.cam_settings = {
			cv2.CAP_PROP_AUTOFOCUS : tk.IntVar(value=1),
			cv2.CAP_PROP_FOCUS : tk.IntVar(value=0),
			cv2.CAP_PROP_BRIGHTNESS : tk.IntVar(value=137),
			cv2.CAP_PROP_EXPOSURE : tk.IntVar(value=-3),
			cv2.CAP_PROP_CONTRAST: tk.IntVar(value=50)
		}


	def update_cam_setting(self, setting):
		self.cam.set(setting, self.cam_settings[setting].get())


	def open_settings_window(self):
		# vv disable settings button
		self.menu_bar.entryconfig("Settings", state="disabled") 
		settings_window = tk.Toplevel(self.root)
		# vv reenable settings button on window close
		settings_window.protocol("WM_DELETE_WINDOW", 
			lambda: self.close_settings_window(settings_window))
		
		settings_window.title("Settings")
		settings_window.geometry("200x600")

		# settings to be configured
		# TODO: not sure that autofocus or contrast settings working properly!
		# TODO: have sliders update every so often, or asynchronously so that
		# changing settings doesn't slow the whole program down
		# TODO: add settings for clustering to settings window
		tk.Label(settings_window, text="Autofocus").pack()
		tk.Checkbutton(settings_window, 
				       variable=self.cam_settings[cv2.CAP_PROP_AUTOFOCUS],
					   onvalue=1, offvalue=0,
					   command= lambda : self.update_cam_setting(cv2.CAP_PROP_AUTOFOCUS)).pack()
		
		tk.Label(settings_window, text="Focus").pack()
		tk.Scale(settings_window, from_=0, to=255, 
		   		 resolution=5, orient="horizontal", 
				 variable=self.cam_settings[cv2.CAP_PROP_FOCUS],
				 command= lambda _ : self.update_cam_setting(cv2.CAP_PROP_FOCUS)).pack()
		
		tk.Label(settings_window, text="Brightness").pack()
		tk.Scale(settings_window, from_=0, to=255, 
		   		 resolution=5, orient="horizontal", 
				 variable=self.cam_settings[cv2.CAP_PROP_BRIGHTNESS],
				 command= lambda _ : self.update_cam_setting(cv2.CAP_PROP_BRIGHTNESS)).pack()
		
		tk.Label(settings_window, text="Exposure").pack()
		tk.Scale(settings_window, from_=-7, to=-1, 
		   		 resolution=1, orient="horizontal", 
				 variable=self.cam_settings[cv2.CAP_PROP_EXPOSURE],
				 command= lambda _ : self.update_cam_setting(cv2.CAP_PROP_EXPOSURE)).pack()
		
		tk.Label(settings_window, text="Contrast").pack()
		tk.Scale(settings_window, from_=0, to=255, 
		   		 resolution=5, orient="horizontal", 
				 variable=self.cam_settings[cv2.CAP_PROP_CONTRAST],
				 command= lambda _ : self.update_cam_setting(cv2.CAP_PROP_CONTRAST)).pack()


	def close_settings_window(self, window):
		self.menu_bar.entryconfig("Settings", state="normal")
		window.destroy()


	def update(self):
		# read image from camera
		_, frame = self.cam.read()

		# TODO: does the model expect rgb or bgr??? 
		# Tkinter needs rgb either way
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

		frame = analyse_frame(frame)

		# convert image to tkinter usable format
		frame = ImageTk.PhotoImage(image=Image.fromarray(frame))

		# update the video panel
		self.video_panel.frame = frame # store reference so not garb-collected
		self.video_panel.config(image=frame)

		# call update again after 10ms
		self.root.after(10, self.update)
		

	def run(self):
		self.update()
		self.root.mainloop()


	def destroy(self):
		self.cam.release()
		self.root.destroy()

