import tkinter as tk
import cv2
from PIL import Image, ImageTk

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
			cv2.CAP_PROP_AUTOFOCUS : tk.IntVar(value=0),
			cv2.CAP_PROP_FOCUS : tk.IntVar(value=100),
			cv2.CAP_PROP_BRIGHTNESS : tk.IntVar(value=100)
		}
		self.update_cam_settings() # init these settings

	def update_cam_settings(self):
		for setting, value in self.cam_settings.items():
			self.cam.set(setting, value.get())

	def open_settings_window(self):
		# vv disable settings button
		self.menu_bar.entryconfig("Settings", state="disabled") 
		settings_window = tk.Toplevel(self.root)
		# vv reenable settings button on window close
		settings_window.protocol("WM_DELETE_WINDOW", 
			lambda: self.close_settings_window(settings_window))
		settings_window.title("Settings")
		settings_window.geometry("200x600")

	def close_settings_window(self, window):
		self.menu_bar.entryconfig("Settings", state="normal")
		window.destroy()

	def update(self):
		# read image from camera
		_, frame = self.cam.read()

		# convert image to tkinter usable format
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
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


if __name__ == "__main__":
	app = App()
	app.run()