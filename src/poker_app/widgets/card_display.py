import tkinter as tk
from tkinter import ttk
import distinctipy

# colours for the hands
_COLOURS = list(map(distinctipy.get_hex, [(0.0, 1.0, 0.0), (1.0, 0.0, 1.0), (0.0, 0.5, 1.0), (1.0, 0.5, 0.0), (0.5, 0.75, 0.5), (0.39678717264876207, 0.13197211806938614, 0.5819931085974647), (0.827283646369405, 0.0138353214106115, 0.1133231387287158), (0.9473827093671684, 0.5084359241017635, 0.8346452862150692), (0.8164329577113776, 0.9928299927881508, 0.009255363614705248), (0.019434052374008415, 0.5050126764558274, 0.11088395395899864), (0.0, 1.0, 1.0), (0.0, 0.0, 1.0), (0.0, 1.0, 0.5), (0.40589042036593503, 0.22354084754929282, 0.10318437663226065), (0.997383433128567, 0.8260316549965426, 0.48300860517842303)]))


class CardDisplay(ttk.Frame):
	"""
	Panel that displays the detected playing cards as sprites and organises them into hands.
	"""

	def __init__(self, master):
		"""
		Initialise instance of CardDisplay.

		Args:
			master (App, or similar tk object): The parent of the CardDisplay.
		"""

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

	def __draw_cards(self, card_labels, x, y):
		"""
		Draws the card sprites corresponding to card_labels on the canvas into rows of length self.CARDS_PER_ROW starting at (x,y).

		args:
			card_labels (list[str]): List of labels of cards to draw.
			x (int): x-coordinate of start of first card row.
			y (int): y-coordinate of start of first card row.
		"""

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

			self.canvas.create_image(x, y, image=self.master.card_sprites[card_label], anchor="nw")  # create canvas image object, init at 0,0

	def update(self, hands, hand_evals, outliers):
		"""
		Draws the hand titles and evaluations with their corresponding card sprites. Also draws outliers separately

		Args:
			hands (list[list[str]]): Lists of card labels organised into hands.
			hand_evals (list[str]): List of corresponding hand evaluations.
			outliers (list[str]): List of card labels of cards belonging to no hand.
		"""

		# clear the canvas
		self.canvas.delete("all")

		# flow and wrap the card sprites, organised by hands
		x = self.CARD_PAD
		y = self.CARD_PAD
		for hand, card_labels in enumerate(hands):
			if hand != 0:
				x = self.CARD_PAD
				y += self.CARD_HEIGHT + self.TITLE_ABOVE_PAD
			self.canvas.create_text(x, y, text=f"Hand {hand + 1}: {hand_evals[hand]}", fill=_COLOURS[hand], font=('Helvetica 20 bold'), anchor="nw")
			y += self.TITLE_HEIGHT + self.TITLE_BELOW_PAD
			self.__draw_cards(card_labels, x, y)
		
		# draw the outliers as well
		if len(outliers) > 0:
			# add padding if we've drawn rows above
			if len(hands) > 0:
				x = self.CARD_PAD
				y += self.CARD_HEIGHT + self.TITLE_ABOVE_PAD
				
			self.canvas.create_text(x, y, text=f"Outliers:", fill="#808080", font=('Helvetica 20 bold'), anchor="nw")
			y += self.TITLE_HEIGHT + self.TITLE_BELOW_PAD
			self.__draw_cards(outliers, x, y)