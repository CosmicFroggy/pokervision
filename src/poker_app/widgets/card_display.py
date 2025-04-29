import tkinter as tk
from tkinter import ttk
import distinctipy
import numpy as np

# colours for the hands
_COLOURS = list(map(distinctipy.get_hex, [(0.0, 1.0, 0.0), (1.0, 0.0, 1.0), (0.0, 0.5, 1.0), (1.0, 0.5, 0.0), (0.5, 0.75, 0.5), (0.39678717264876207, 0.13197211806938614, 0.5819931085974647), (0.827283646369405, 0.0138353214106115, 0.1133231387287158), (0.9473827093671684, 0.5084359241017635, 0.8346452862150692), (0.8164329577113776, 0.9928299927881508, 0.009255363614705248), (0.019434052374008415, 0.5050126764558274, 0.11088395395899864), (0.0, 1.0, 1.0), (0.0, 0.0, 1.0), (0.0, 1.0, 0.5), (0.40589042036593503, 0.22354084754929282, 0.10318437663226065), (0.997383433128567, 0.8260316549965426, 0.48300860517842303)]))


class CardDisplay(ttk.Frame):
	"""
	Panel that displays the detected playing cards as sprites and organises them into hands.
	"""

	def __init__(self, app, master):
		"""
		Initialise instance of CardDisplay.

		Args:
			app (App): Reference to main App instance.
			master (some tk object): The parent of the CardDisplay.
		"""

		super().__init__(master)
		self.app = app
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

		# create scrollbar
		self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
		self.canvas.configure(yscrollcommand=self.scrollbar.set)
		self.canvas.bind("<Configure>", lambda _: self.canvas.configure(scrollregion=self.canvas.bbox("all"))) # update scroll region on config event
		self.scrollbar.place(relx=1, rely=0, relheight=1, anchor="ne")
		
		# add mouse scrolling
		self.canvas.bind("<MouseWheel>", lambda event: self.canvas.yview_scroll(-int(np.sign(event.delta)*app.scroll_speed), "units")) 

	def __draw_cards(self, cards, x, y):
		"""
		Draws the card sprites corresponding to given cards on the canvas into rows of length self.CARDS_PER_ROW starting at (x,y).

		args:
			cards (list[Card]): Cards to be drawn.
			x (int): x-coordinate of start of first card row.
			y (int): y-coordinate of start of first card row.
		"""

		col = 0
		for i, card in enumerate(cards):
			# go onto new row if exceed max per row
			col = i % self.CARDS_PER_ROW

			if col == 0:
				x = self.CARD_PAD
			else:
				x += self.CARD_WIDTH + self.CARD_PAD

			if i != 0 and col == 0:
				y += self.CARD_HEIGHT+ self.CARD_PAD

			self.canvas.create_image(x, y, image=self.app.card_sprites[card.cls], anchor="nw")  # create canvas image object, init at 0,0

	def update(self, hands, outliers):
		"""
		Draws the hand titles and evaluations with their corresponding card sprites. Also draws outliers separately.

		Args:
			hands (list[Hand]): Hands to be drawn.
			outliers (list[Card]): Outliers to be drawn.
		"""

		# clear the canvas
		self.canvas.delete("all")

		# flow and wrap the card sprites, organised by hands
		x = self.CARD_PAD
		y = self.CARD_PAD
		for i, hand in enumerate(hands):
			if i != 0:
				x = self.CARD_PAD
				y += self.CARD_HEIGHT + self.TITLE_ABOVE_PAD
			self.canvas.create_text(x, y, text=f"Hand {i + 1}: {hand.evaluate()}", fill=_COLOURS[i], font=('Helvetica 20 bold'), anchor="nw")
			y += self.TITLE_HEIGHT + self.TITLE_BELOW_PAD
			self.__draw_cards(hand.cards, x, y)
		
		# draw the outliers as well
		if len(outliers) > 0:
			# add padding if we've drawn rows above
			if len(hands) > 0:
				x = self.CARD_PAD
				y += self.CARD_HEIGHT + self.TITLE_ABOVE_PAD
				
			self.canvas.create_text(x, y, text=f"Outliers:", fill="#808080", font=('Helvetica 20 bold'), anchor="nw")
			y += self.TITLE_HEIGHT + self.TITLE_BELOW_PAD
			self.__draw_cards(outliers, x, y)

		# update scroll region for scrollbar
		self.canvas.configure(scrollregion=self.canvas.bbox("all"))

		# TODO: This seems to have made us lose the outer padding, fix!