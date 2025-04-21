import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk


from card_detection import analyse_frame


class Viewport(ttk.Frame):
	def __init__(self, master):
		super().__init__(master)
		self.view = tk.Label(self)
		self.view.pack()

	def swap_buffer(self, frame):
		self.view.buffer = frame # store reference so not garb-collected
		self.view.config(image=self.view.buffer)


# main app class
class App(tk.Tk):
	def __init__(self, title):
		super().__init__()
		self.title(title)
		self.protocol("WM_DELETE_WINDOW", self.close)

		# TODO: Lock the window size

		# create video panel
		self.viewport = Viewport(self)
		self.viewport.pack()

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


		# create menu bar
		self.menu_bar = tk.Menu(self)
		self.menu_bar.add_command(label="Settings", command=self.open_settings_window)
		self.config(menu=self.menu_bar)

		# organise card sprites
		self.CARD_WIDTH = 88
		self.CARD_HEIGHT = 124	# TODO: add these to a config file/settings?
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

		# create canvas to draw cards on
		self.card_canvas = tk.Canvas(self, bg="#008080", height=400)
		self.card_canvas.pack(fill="both", expand=True)

		# track the card objects that are drawn on the canvas
		self.card_objects = [] # list of tuples (card label, tk image object)

	
	def update_card_objects(self, detected_cards):

		# remove old cards no longer detected
		to_delete = [] # record indices to delete, avoid invalidation
		for i, (card_label, card_object) in enumerate(self.card_objects):
			if card_label not in detected_cards:
				self.card_canvas.delete(card_object)
				to_delete.append(i)

		to_delete.reverse()
		for i in to_delete:
			del self.card_objects[i]


		# add newly detected cards
		previously_detected = [ val[0] for val in self.card_objects ]  # get the labels
		new_cards = [ val for val in detected_cards if val not in previously_detected ]

		
		for card_label in set(new_cards): # change to set to remove duplicates
			card_object = self.card_canvas.create_image(0, 0, image=self.card_sprites[card_label], anchor="nw")  # create canvas image object, init at 0,0
			self.card_objects.append((card_label, card_object))

		# TODO: later we might want duplicates?

	
	def update_canvas_layout(self):
		row = 0
		col = 0
		for i, (_, card_object) in enumerate(self.card_objects):
			col = i % self.CARDS_PER_ROW
			if i != 0 and col == 0:
				row += 1
			x = self.CARD_PAD + col*(self.CARD_PAD + self.CARD_WIDTH)
			y = self.CARD_PAD + row*(self.CARD_PAD + self.CARD_HEIGHT)
			self.card_canvas.coords(card_object, x, y)


	def update_cam_setting(self, setting):
		self.cam.set(setting, self.cam_settings[setting].get())


	def open_settings_window(self):
		# vv disable settings button
		self.menu_bar.entryconfig("Settings", state="disabled") 
		settings_window = tk.Toplevel(self)
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

		frame, detected_cards = analyse_frame(frame)

		# convert image to tkinter usable format
		frame = ImageTk.PhotoImage(image=Image.fromarray(frame))

		self.viewport.swap_buffer(frame)

		# TODO: update canvas with card sprites
		self.update_card_objects(detected_cards)
		self.update_canvas_layout()

		# call update again after 10ms
		self.after(10, self.update)

		

	def run(self):
		self.update()
		self.mainloop()


	def close(self):
		self.cam.release()
		self.destroy()

