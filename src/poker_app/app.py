import tkinter as tk
import cv2
from PIL import Image, ImageTk

from card_detection import analyse_frame
from widgets import Viewport, CardDisplay, MenuBar
from utils import Camera, load_sprites


# main app class
class App(tk.Tk):
	def __init__(self, title):
		super().__init__()
		self.title(title)
		self.protocol("WM_DELETE_WINDOW", self.close)

		# TODO: Lock the window size

		# get access to camera
		self.cam = Camera()

		# load assets
		self.card_sprites = load_sprites("./res/sprites/atlas.txt")

		# initialise settings
		# this is a dict of lists [settingVar, changed]
		# changed refers to whether it has been modified this frame
		self.settings = {  # TODO: pull settings from config file, probably JSON
			"CAMERA": { 
				"AUTOFOCUS": [tk.IntVar(self.cam.get_cam_prop("AUTOFOCUS")), False],
				"FOCUS": [tk.IntVar(self.cam.get_cam_prop("FOCUS")), False],
				"BRIGHTNESS": [tk.IntVar(self.cam.get_cam_prop("BRIGHTNESS")), False]
				},
			"CLUSTERING": {
			}
		}
		
		# layout
		self.viewport = Viewport(self)  # create video panel
		self.viewport.pack()

		self.card_display = CardDisplay(self)  # create area to display cards
		self.card_display.pack(fill="both")

		self.menu_bar = MenuBar(self)  # create menu bar
		self.config(menu=self.menu_bar)

	def setting_update_notify(self, subject, setting):
		self.settings[subject][setting][1] = True

	def update_settings(self):
		# update the settings only once at the end of the frame
		# and only if they were changed

		# camera settings
		camera_settings = self.settings["CAMERA"]
		for setting, (val, changed) in camera_settings.items():
			if changed:
				self.cam.set_cam_prop(setting, val.get())
				camera_settings[setting][1] = False

	def update(self):

		# read image from camera
		frame = self.cam.read()

		# TODO: does the model expect rgb or bgr??? 
		# Tkinter needs rgb either way
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

		frame, detected_cards = analyse_frame(frame)

		# convert image to tkinter usable format
		frame = ImageTk.PhotoImage(image=Image.fromarray(frame))

		# update image shown in viewport
		self.viewport.swap_buffer(frame)

		# update canvas with card sprites
		self.card_display.update(detected_cards)
	
		# update settings once per frame, only if they were changed
		self.update_settings()

		# call update again after 10ms
		self.after(10, self.update)

	def run(self):
		self.update()
		self.mainloop()

	def close(self):
		self.cam.release()
		self.destroy()

