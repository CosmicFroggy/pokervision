from pokerkit import StandardLookup


class Hand():
	"""
	Class to represent a hand of detected playing cards.
	"""

	def __init__(self, id, cards=[]):
		"""
		Initialise instance of Hand.

		Args:
			cards (list[Card], optional): The cards to initialise the hand with.
		"""
		
		self.id = id
		self.cards = cards
		for card in self.cards:
			card.hand_id = self.id

	def add_card(self, card):
		"""
		Add a card to the hand.

		Args:
			card (Card): The card to be added.
		"""

		card.hand_id = self.id
		self.cards.append(card)

	def remove_card(self, card):
		"""
		Remove a card from the hand.
		
		Args:
			card (Card): The card to be removed.
		"""

		card.hand_id = -1
		self.cards.remove(card)

	def evaluate(self):
		"""
		Evaluates the hand, returns a string like "Royal straight flush". Will return "Not enough cards!", "Too many cards!", and "Invalid hand!" if there are too few cards, too many cards, or a combination of cards that do not form a poker hand, respectively.

		Returns:
			str: The hand evaluation.
		"""

		# check the hand has 5 cards
		hand_size = len(self.cards)
		if hand_size < 5:
			return "Not enough cards!"
		elif hand_size > 5:
			return "Too many cards!"

		# get the card labels
		card_labels = [card.cls for card in self.cards]

		# pokerkit expects "T" instead of "10"
		for i, label in enumerate(card_labels):
			if label[0:2] == "10":
				card_labels[i] = "T" + label[2]
		
		# evaluate hand using pokerkit
		hand = "".join(card_labels)
		try:
			evaluation = str(StandardLookup().get_entry(hand).label)
		except ValueError:
			return "Invalid hand!"

		# check for royal straight flushes
		royals = ["T", "Q", "J", "K", "A"]
		if evaluation == "Straight flush" and all([(royal in hand) for royal in royals]):
			evaluation = "Royal " + evaluation.lower()

		return evaluation