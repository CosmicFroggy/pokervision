class Box:
	"""
	A simple 2D box class.
	"""

	def __init__(self, x, y, w, h):
		"""
		Initialise instance of Box.

		Args:
			x (float): The x-coordinate of box center.
			y (float): The y-coordinate of box center.
			w (float): The width of the box.
			h (float): The height of the box.
		"""

		self.x = x
		self.y = y
		self.w = w
		self.h = h

	@property
	def xywh(self):
		return self.x, self.y, self.w, self.h


class Card:
	"""
	Data structure class to hold the attributes of a detected card.
	"""

	def __init__(self, id, cls, conf, x, y, w, h):
		"""
		Initialise instance of Card.

		Args:
			id (int): The id of the card.
			cls (str): The card label, e.g "Ah" for Ace of Hearts.
			conf (float): The confidence of the detection.
			x (float): The x-coordinate of the center of the suitrank box.
			y (float): The y-coordinate of the center of the suitrank box.
			w (float): The width of the suitrank box.
			h (float): The height of the suitrank box.
		"""

		self.id = id
		self.cls = cls
		self.conf = conf
		self.box = Box(x, y, w, h)
		self.hand_id = -1


