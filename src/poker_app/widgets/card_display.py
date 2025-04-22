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
		self.TITLE_ABOVE_PAD = 20
		self.TITLE_HEIGHT = 30
		self.TITLE_BELOW_PAD = 10

		# create canvas to draw cards on
		self.canvas = tk.Canvas(self, bg="#008080")
		self.canvas.pack(fill="both", expand=True)

		# track the card objects that are drawn on the canvas
		self.card_objects = {} # dict with k,v pair (card label:tk image object)
		self.hand_text_objects = [] # list of tk canvas text objects
		self.outlier_text_object = None

	def update(self, detected_cards, hands, outliers):
		self.update_card_objects(detected_cards)
		self.update_hand_text(len(hands), outliers=len(outliers)>0)
		self.update_canvas_layout(hands, outliers)

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

	def update_hand_text(self, num_hands, outliers=False):
		# destroy old hand titles if they're no longer needed
		# or add new ones if we need more
		num_labels = len(self.hand_text_objects)
		while(num_labels != num_hands):
			if num_hands > num_labels:
				new_label = self.canvas.create_text(0,0, text=f"Hand {num_labels}:", fill="black", font=('Helvetica 20 bold'), anchor="nw")
				self.hand_text_objects.append(new_label)
				num_labels += 1
			elif num_hands < num_labels:
				self.canvas.delete(self.hand_text_objects[-1])
				self.hand_text_objects.pop()
				num_labels -= 1

		# add or remove outlier label if needed
		if outliers and self.outlier_text_object == None:
			outlier_label = self.canvas.create_text(0,0, text=f"Outliers:", fill="black", font=('Helvetica 20 bold'), anchor="nw")
			self.outlier_text_object = outlier_label
		elif not outliers and self.outlier_text_object != None:
			self.canvas.delete(self.outlier_text_object)
			self.outlier_text_object = None

	def draw_cards(self, card_labels, x, y):
		col = 0
		for i, card_label in enumerate(card_labels):
			# go onto new row if exceed max per row
			col = i % self.CARDS_PER_ROW

			if col == 0:
				x = self.CARD_PAD
			else:
				x += self.CARD_WIDTH + self.CARD_PAD

			if i != 0 and col == 0:
				y += self.CARD_HEIGHT+ self.CARD_PAD

			self.canvas.coords(self.card_objects[card_label], x, y)

	def update_canvas_layout(self, hands, outliers):
		# flow and wrap the card sprites, organised by hands
		x = self.CARD_PAD
		y = self.CARD_PAD
		for hand, card_labels in enumerate(hands):
			if hand != 0:
				x = self.CARD_PAD
				y += self.CARD_HEIGHT + self.TITLE_ABOVE_PAD
			self.canvas.coords(self.hand_text_objects[hand], x, y)
			y += self.TITLE_HEIGHT + self.TITLE_BELOW_PAD
			self.draw_cards(card_labels, x, y)
		
		# draw the outliers as well
		if len(outliers) > 0:
			# add padding if we've drawn rows above
			if len(hands) > 0:
				x = self.CARD_PAD
				y += self.CARD_HEIGHT + self.TITLE_ABOVE_PAD
				
			self.canvas.coords(self.outlier_text_object, x, y)
			y += self.TITLE_HEIGHT + self.TITLE_BELOW_PAD
			self.draw_cards(outliers, x, y)