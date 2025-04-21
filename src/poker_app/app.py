import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk

from card_detection import analyse_frame
from widgets import Viewport, SettingsWindow, CardDisplay
from utils import Camera


# main app class
class App(tk.Tk):
	def __init__(self, title):
		super().__init__()
		self.title(title)
		self.protocol("WM_DELETE_WINDOW", self.close)

		# TODO: Lock the window size

		# get access to camera
		self.cam = Camera()

		# initialise settings
		# this is a dict of lists [settingVar, changed]
		# changed refers to whether it has been modified this frame
		self.settings = {
			"CAMERA": { 
				"AUTOFOCUS": [tk.IntVar(self.cam.get_cam_prop("AUTOFOCUS")), False],
				"FOCUS": [tk.IntVar(self.cam.get_cam_prop("FOCUS")), False],
				"BRIGHTNESS": [tk.IntVar(self.cam.get_cam_prop("BRIGHTNESS")), False]
				},
			"CLUSTERING": {

			}
		}
		
		# TODO: pull settings from config file, probably JSON

		# create video panel
		self.viewport = Viewport(self)
		self.viewport.pack()

		# card attributes
		self.CARD_WIDTH = 88
		self.CARD_HEIGHT = 124
		self.CARD_PAD = 5
		self.CARDS_PER_ROW = 6

		self.card_sprites = {}
		sprite_sheets = ["Clubs-88x124.png",
						"Diamonds-88x124.png",
						"Hearts-88x124.png",
						"Spades-88x124.png"]

		ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

		for sheet_name in sprite_sheets:
			sheet_image = Image.open("./res/SBS - 2D Poker Pack/Top-Down/Cards/" + sheet_name)
			suit = sheet_name[0].lower()
			card_names = map(lambda rank : rank + suit, ranks) # TODO: should I use enums instead of strings?

			row = 0
			col = 0
			max_col = 5
			for i, name in enumerate(card_names):
				col = i % max_col
				if i != 0 and col == 0:
					row += 1
				self.card_sprites[name] = sheet_image.crop(
					(col*self.CARD_WIDTH, row*self.CARD_HEIGHT, 
					(col+1)*self.CARD_WIDTH, (row+1)*self.CARD_HEIGHT))
				
		# get card back sprite as well
		self.card_sprites["back"] = Image.open("./res/SBS - 2D Poker Pack/Top-Down/Cards/Card_Back-88x124.png").crop((0, 0, self.CARD_WIDTH, self.CARD_HEIGHT))

		# convert cards to tkinter compatible type
		self.card_sprites = { k: ImageTk.PhotoImage(v) for k, v in self.card_sprites.items() }

		# create area to display detected cards
		self.card_display = CardDisplay(self)
		self.card_display.pack(fill="both")

		

		# create menu bar
		self.menu_bar = tk.Menu(self)
		self.menu_bar.add_command(label="Settings", command= lambda : SettingsWindow(self))
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

