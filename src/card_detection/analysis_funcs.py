import cv2
from ultralytics import YOLO
from sklearn.cluster import DBSCAN
import distinctipy
from pokerkit import StandardLookup


LABELS = ['10c', '10d', '10h', '10s', '2c', '2d', '2h', '2s', '3c', '3d', '3h', '3s', '4c', '4d', '4h', '4s', '5c', '5d', '5h', '5s', '6c', '6d', '6h', '6s', '7c', '7d', '7h', '7s', '8c', '8d', '8h', '8s', '9c', '9d', '9h', '9s', 'Ac', 'Ad', 'Ah', 'As', 'Jc', 'Jd', 'Jh', 'Js', 'Kc', 'Kd', 'Kh', 'Ks', 'Qc', 'Qd', 'Qh', 'Qs']

# generate 15 distinct colours to use to label the groups
# COLOURS = list(map(distinctipy.get_rgb256, distinctipy.get_colors(15)))
# hard code these for now so we can use them across classes,
# TODO: find a way more elegant solution to this
COLOURS = list(map(distinctipy.get_rgb256, [(0.0, 1.0, 0.0), (1.0, 0.0, 1.0), (0.0, 0.5, 1.0), (1.0, 0.5, 0.0), (0.5, 0.75, 0.5), (0.39678717264876207, 0.13197211806938614, 0.5819931085974647), (0.827283646369405, 0.0138353214106115, 0.1133231387287158), (0.9473827093671684, 0.5084359241017635, 0.8346452862150692), (0.8164329577113776, 0.9928299927881508, 0.009255363614705248), (0.019434052374008415, 0.5050126764558274, 0.11088395395899864), (0.0, 1.0, 1.0), (0.0, 0.0, 1.0), (0.0, 1.0, 0.5), (0.40589042036593503, 0.22354084754929282, 0.10318437663226065), (0.997383433128567, 0.8260316549965426, 0.48300860517842303)]))


# create model using previously trained weights
# model = YOLO("CardDetector.pt")
# using model from https://github.com/PD-Mera/Playing-Cards-Detection
# while I fine tune my own
detector_model = YOLO("./res/models/yolov8s_playing_cards.pt")


class Card:
	"""
	Data structure class to hold the attributes of a detected card suitrank box.
	"""
	def __init__(self, id, cls, conf, x, y, w, h):
		"""
		Initialise instance of Card.

		Args:
			id (int): The id of the card.
			cls (str): The card label, e.g "Ah" for Ace of Hearts.
			conf (float): The confidence of the detection.
			x (float): The x-coordinate of the center of the box.
			y (float): The y-coordinate of the center of the box.
			w (float): The width of the box.
			h (float): The height of the box.
		"""

		self.id = id
		self.cls = cls
		self.conf = conf
		self.x = x
		self.y = y
		self.w = w
		self.h = h


def detect_cards(image):
	"""
	Detects the position of the suit and rank of playing cards on the image passed in using YOLO object detection. The top most (in frame) suitrank is selected and all duplicates are discarded. 

	Args:
		image (MatLike): The image to be searched for playing cards.

	Returns:
		list[Card]: A list of card objects, corresponding to the detected cards.
	"""

	cards = []
	prediction = detector_model.track(image, verbose=False, persist=True)[0]
	if prediction.boxes.id != None:
		for i, box_id in enumerate(prediction.boxes.id):
			# get attributes of identified card
			box_id = int(box_id.cpu().tolist())
			cls_id = int(prediction.boxes.cls[i].cpu().tolist())
			cls_label = LABELS[cls_id]
			conf = prediction.boxes.conf[i].cpu().tolist()
			x, y, w, h = prediction.boxes.xywh[i].cpu().tolist()
			
			cards.append(Card(box_id, cls_label, conf, x, y, w, h))
	
	# to avoid detecting the same card twice because both of it's symbols 
	# are exposed, we only count the top most one, checking by y coordinate
	# TODO: this temporary fix does not account for if the hand is upside down
	# need to think of a way to fix this. We are also assuming that this is a 
	# 52 card deck and it is not possible for a card to appear twice
	to_discard = set() # make it a set so were not removing same index twice
	for i, card1 in enumerate(cards):
		if i == len(cards) - 1:
			break
		for j, card2 in enumerate(cards[i+1:]):
			cls1 = card1.cls
			y1 = card1.y
			cls2 = card2.cls
			y2 = card2.y
			# discard the lower instance (remember y goes down the screen!)
			if cls1 == cls2 and y1 <= y2:
				to_discard.add(i+j+1)
			elif cls1 == cls2 and y1 > y2:
				to_discard.add(i)
	
	# sort the list and remove cards backwards from list to avoid invalidation
	to_discard = sorted(to_discard)
	to_discard.reverse()
	for i in to_discard:
		del cards[i]

	return cards


def cluster(cards, eps=100, min_samples=2):
	"""
	Uses DBSCAN to cluster cards into hands by proximity.

	Args:
		cards (list[Card]): List of card objects to cluster.
		eps (float, optional): The maximum distance between two samples for one to be considered as in the neighborhood of the other. See DBSCAN docs.
		min_samples (int, optional): The number of samples in a neighborhood for a point to be considered as a core point. See DBSCAN docs.

	Returns:
		list[int]: List of hand labels that correspond to the list of cards.
	"""

	# using DBSCAN clustering algo to group card hands

	if len(cards) == 0:
		return []

	positions = []
	for card in cards:
		position = (card.x, card.y)
		positions.append(position)
	
	# identify hand label for each card
	hand_labels = DBSCAN(eps=eps, min_samples=min_samples).fit(positions).labels_.tolist()

	return hand_labels


def group_hands(card_labels, hand_labels):
	"""
	Groups the given card_labels into hands using the given hand_labels. Also groups the outliers into a separate list.

	Args:
		card_labels (list[str]): List of card labels to group.
		hand_labels (list[int]): List of hand labels to group the card labels by.

	Returns:
		list[list[str]]: The card labels grouped into lists by hand, excluding outliers.
		list[str]: The outliers are grouped separately.
	"""

	# determine how many hands there is
	unique_hands = set(filter(lambda i : i != -1, hand_labels))
	num_hands = len(unique_hands)

	# create list of n empty hands
	hands = [ [] for _ in range(num_hands) ]
	outliers = []

	# groups the cards into hand lists
	for i, hand_label in enumerate(hand_labels):
		if hand_label == -1:
			outliers.append(card_labels[i])
			continue
		hands[hand_label].append(card_labels[i])

	return hands, outliers


def identify_hands(hands):
	"""
	Returns the values of a list of 5 card poker hands.

	Args:
		hands (list[list[str]]): A list of list of card labels - the list of hands to be evaluated.

	Returns:
		list[str]: A list of hand evaluations.
	"""

	evaluations = []
	for hand in hands:
		# check the hand has 5 cards
		hand_size = len(hand)
		if hand_size < 5:
			evaluations.append("Not enough cards!")
			continue
		elif hand_size > 5:
			evaluations.append("Too many cards!")
			continue

		# create copy of the list to iterate over so we can modify
		hand = hand[:]

		# pokerkit expects "Th" instead of "10h" for example
		for i, label in enumerate(hand):
			if label[0:2] == "10":
				hand[i] = "T" + label[2]
		
		# evaluate hand using pokerkit
		hand = "".join(hand)
		try:
			evaluation = str(StandardLookup().get_entry(hand).label)
		except ValueError:
			evaluation = "Invalid hand!"

		# check for royal straight flushes
		royals = ["T", "Q", "J", "K", "A"]
		if evaluation == "Straight flush" and all([(royal in hand) for royal in royals]):
			evaluation = "Royal " + evaluation.lower()
		
		evaluations.append(evaluation)
	
	return evaluations

		
def annotate(image, cards, hand_labels):
	"""
	Annotate the frame with the given card boxes and hand groupings. The colours of the drawn frames represent the hands, outliers have grey boxes.

	Args:
		image (MatLike): The image to be annotated.
		cards (list[Card]): List of card suitrank box data structure objects to use to annotate the image.
		hand_labels (list[int]): Hand labels corresponding to the given cards, used to show the hands visually.
	"""
	# draw the card annotations
	for i, card in enumerate(cards):
		# get attributes
		x, y, w, h = card.x, card.y, card.w, card.h
		x_l, y_t, x_r, y_b = int(x-w/2), int(y-h/2), int(x+w/2), int(y+h/2)
		x, y = int(x), int(y)

		# annotate
		if hand_labels[i] == -1:
			colour = (127, 127, 127)
		else:
			colour = COLOURS[hand_labels[i]]
		cv2.rectangle(image, (x_l, y_t), (x_r, y_b), colour, 2)
		cv2.rectangle(image, (x_l, y_t-30), (x_l+80, y_t-10), colour, -1)
		cv2.putText(image, f"{card.cls}: {card.conf:.2f}", (x_l, y_t-15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
