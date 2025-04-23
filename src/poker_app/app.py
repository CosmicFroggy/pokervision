import tkinter as tk
import cv2
from PIL import Image, ImageTk

from card_detection import detect_cards, cluster, annotate, group_hands, identifyHands
from poker_app.widgets import Viewport, CardDisplay, MenuBar
from poker_app.utils import Camera, load_sprites


# main app class
class App(tk.Tk):
	"""
	Top-level class of my program. Use run method to start the program.
	"""

	def __init__(self, title):
		"""
		Initilialise an App instance.

		Args:
			title (str): The title of the program, displayed on window border.
		"""

		super().__init__()
		self.title(title)
		self.protocol("WM_DELETE_WINDOW", self.close)

		self.geometry("1600x720")

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
		self.viewport.pack(side="left")

		self.card_display = CardDisplay(self)  # create area to display cards
		self.card_display.pack(side="right", fill="both", expand=True)

		self.menu_bar = MenuBar(self)  # create menu bar
		self.config(menu=self.menu_bar)

	def setting_update_notify(self, category, setting):
		"""
		Notify the program that the setting has changed so that it can update the onboard camera settings once at the end of frame. See update_settings method.

		Args:
			category (str): The setting category, e.g. "CAMERA".
			setting (str): The setting that has been changed, e.g. "FOCUS".
		"""

		self.settings[category][setting][1] = True

	def update_settings(self):
		"""
		Update the onboard camera settings to match the values set by the program. Used to update the camera settings only once at the end of the frame and only if they were changed. This improves the frame rate when adjusting settings.
		"""

		camera_settings = self.settings["CAMERA"]
		for setting, (val, changed) in camera_settings.items():
			if changed:
				self.cam.set_cam_prop(setting, val.get())
				camera_settings[setting][1] = False

	def update(self):
		"""
		Update all elements of the program. Running this starts an update loop.
		"""

		# read image from camera
		frame = self.cam.read()
		
		# scale the image up
		frame = cv2.resize(frame, (int(frame.shape[1]*1.5), int(frame.shape[0]*1.5)))
		
		# use machine learning to detect cards
		cards = detect_cards(frame)
		card_labels = [card.cls for card in cards]
		hand_labels = cluster(cards)  # use dbscan to identify hands by clustering
		hands, outliers = group_hands(card_labels, hand_labels)
		hand_evals = identifyHands(hands)
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
		annotate(frame, cards, hand_labels) # draw on the frame


		# convert image to tkinter usable format
		frame = ImageTk.PhotoImage(image=Image.fromarray(frame))

		# update image shown in viewport
		self.viewport.swap_buffer(frame)

		# update canvas with card sprites
		self.card_display.update(card_labels, hands, outliers, hand_evals)
	
		# update settings once per frame, only if they were changed
		self.update_settings()

		# call update again after 10ms
		self.after(10, self.update)

	def run(self):
		"""
		Start the program.
		"""

		self.update()
		self.mainloop()

	def close(self):
		"""
		Close the program.
		"""

		self.cam.release()
		self.destroy()

