import tkinter as tk
from tkinter import ttk


class CardDisplay(ttk.Frame):
	def __init__(self, master):
		super().__init__(master)
		self.master = master

		# card attributes
		self.CARD_WIDTH = 88
		self.CARD_HEIGHT = 124
		self.CARD_PAD = 5
		self.CARDS_PER_ROW = 6

		# create canvas to draw cards on
		self.canvas = tk.Canvas(self, bg="#008080", height=400)
		self.canvas.pack(fill="both", expand=True)

		# track the card objects that are drawn on the canvas
		self.card_objects = {} # dict with k,v pair (card label:tk image object)

	def update(self, detected_cards):
		self.update_card_objects(detected_cards)
		self.update_canvas_layout()

	def update_card_objects(self, detected_cards):
		# remove old cards no longer detected
		to_delete = [] # track and delete after loop to avoid invalidation
		for card_label, card_object in self.card_objects.items():
			if card_label not in detected_cards:
				self.canvas.delete(card_object)
				to_delete.append(card_label)
		
		for card_label in to_delete:
			del self.card_objects[card_label]

		# add newly detected cards
		previously_detected = self.card_objects.keys()  # get the labels
		new_cards = [ card for card in detected_cards if card not in previously_detected ]

		for card_label in set(new_cards): # change to set to remove duplicates
			card_object = self.canvas.create_image(0, 0, image=self.master.card_sprites[card_label], anchor="nw")  # create canvas image object, init at 0,0
			self.card_objects[card_label] = card_object

		# TODO: later we might want duplicates?

	def update_canvas_layout(self):
		# flow and wrap the card sprites
		row = 0
		col = 0
		for i, card_object in enumerate(self.card_objects.values()):
			col = i % self.CARDS_PER_ROW
			if i != 0 and col == 0:
				row += 1
			x = self.CARD_PAD + col*(self.CARD_PAD + self.CARD_WIDTH)
			y = self.CARD_PAD + row*(self.CARD_PAD + self.CARD_HEIGHT)
			self.canvas.coords(card_object, x, y)