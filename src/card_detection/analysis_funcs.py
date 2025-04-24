import cv2
from ultralytics import YOLO
from sklearn.cluster import DBSCAN
import distinctipy

from card_detection.card import Card
from card_detection.hand import Hand


_LABELS = ['10c', '10d', '10h', '10s', '2c', '2d', '2h', '2s', '3c', '3d', '3h', '3s', '4c', '4d', '4h', '4s', '5c', '5d', '5h', '5s', '6c', '6d', '6h', '6s', '7c', '7d', '7h', '7s', '8c', '8d', '8h', '8s', '9c', '9d', '9h', '9s', 'Ac', 'Ad', 'Ah', 'As', 'Jc', 'Jd', 'Jh', 'Js', 'Kc', 'Kd', 'Kh', 'Ks', 'Qc', 'Qd', 'Qh', 'Qs']

# generate 15 distinct colours to use to label the groups
# COLOURS = list(map(distinctipy.get_rgb256, distinctipy.get_colors(15)))
# hard code these for now so we can use them across classes,
# TODO: find a way more elegant solution to this
_COLOURS = list(map(distinctipy.get_rgb256, [(0.0, 1.0, 0.0), (1.0, 0.0, 1.0), (0.0, 0.5, 1.0), (1.0, 0.5, 0.0), (0.5, 0.75, 0.5), (0.39678717264876207, 0.13197211806938614, 0.5819931085974647), (0.827283646369405, 0.0138353214106115, 0.1133231387287158), (0.9473827093671684, 0.5084359241017635, 0.8346452862150692), (0.8164329577113776, 0.9928299927881508, 0.009255363614705248), (0.019434052374008415, 0.5050126764558274, 0.11088395395899864), (0.0, 1.0, 1.0), (0.0, 0.0, 1.0), (0.0, 1.0, 0.5), (0.40589042036593503, 0.22354084754929282, 0.10318437663226065), (0.997383433128567, 0.8260316549965426, 0.48300860517842303)]))


# create model using previously trained weights
# model = YOLO("CardDetector.pt")
# using model from https://github.com/PD-Mera/Playing-Cards-Detection
# while I fine tune my own
_detector_model = YOLO("./res/models/yolov8s_playing_cards.pt")


def detect_cards(image):
	"""
	Detects the position of the suit and rank of playing cards on the image passed in using YOLO object detection. The top most (in frame) suitrank is selected and all duplicates are discarded. 

	Args:
		image (MatLike): The image to be searched for playing cards.

	Returns:
		list[Card]: A list of card objects, corresponding to the detected cards.
	"""

	cards = []
	prediction = _detector_model.track(image, verbose=False, persist=True)[0]
	if prediction.boxes.id != None:
		for i, box_id in enumerate(prediction.boxes.id):
			# get attributes of identified card
			box_id = int(box_id.cpu().tolist())
			cls_id = int(prediction.boxes.cls[i].cpu().tolist())
			cls_label = _LABELS[cls_id]
			conf = prediction.boxes.conf[i].cpu().tolist()
			x, y, w, h = prediction.boxes.xywh[i].cpu().tolist()

			if conf < 0.5:
				continue
			
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
			y1 = card1.box.y
			cls2 = card2.cls
			y2 = card2.box.y
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


def detect_hands(cards):
	"""
	Detect hand arrangements for given cards.

	Args:
		cards (list[Card]): List of cards to be grouped into hands.
	
	Returns:
		list[Hand]: List of hand objects.
		list[Card]: List of cards that are outliers, belong to no hand.
	"""

	hand_labels = _cluster(cards)
	hands, outliers = _group_hands(cards, hand_labels)

	return hands, outliers


def _cluster(cards, eps=100, min_samples=2):
	"""
	Uses DBSCAN to cluster cards into hands by proximity.

	Args:
		cards (list[Card]): List of card objects to cluster.
		eps (float, optional): The maximum distance between two samples for one to be considered as in the neighborhood of the other. See DBSCAN docs.
		min_samples (int, optional): The number of samples in a neighborhood for a point to be considered as a core point. See DBSCAN docs.

	Returns:
		list[int]: List of hand labels that correspond to the list of cards.
	"""

	if len(cards) == 0:
		return []

	positions = []
	for card in cards:
		position = (card.box.x, card.box.y)
		positions.append(position)
	
	# identify hand label for each card
	hand_labels = DBSCAN(eps=eps, min_samples=min_samples).fit(positions).labels_.tolist()

	return hand_labels


def _group_hands(cards, hand_labels):
	"""
	Groups the given cards into hands using the given hand_labels. Also groups the outliers into a separate list.

	Args:
		cards (list[Card]): List of cards to group.
		hand_labels (list[int]): List of hand labels to group the card labels by.

	Returns:
		list[Hand]: The grouped hands.
		list[Card]: List of outlier cards.
	"""

	hands = []
	outliers = []
	checked_labels = []

	for i, hand_label in enumerate(hand_labels):
		# check if card is an outlier
		if hand_label == -1:
			outliers.append(cards[i])
		# add card to appropriate hand if it already exists
		elif hand_label in checked_labels:
			hand = next(filter(lambda hand : hand.id == hand_label, hands))
			hand.add_card(cards[i]) 
		# create a new hand if it doesn't
		else:
			hands.append(Hand(hand_label, [cards[i]]))
			checked_labels.append(hand_label)

	return hands, outliers

		
def annotate(image, cards):
	"""
	Annotate the frame with the given cards. The colours of the drawn frames represent the hands, outliers have grey boxes.

	Args:
		image (MatLike): The image to be annotated.
		cards (list[Card]): List of cards to annotate image with.
	"""
	# draw the card annotations
	for i, card in enumerate(cards):
		# get attributes
		x, y, w, h = card.box.xywh
		x_l, y_t, x_r, y_b = int(x-w/2), int(y-h/2), int(x+w/2), int(y+h/2)
		x, y = int(x), int(y)

		# annotate
		if card.hand_id == -1:
			colour = (127, 127, 127)
		else:
			colour = _COLOURS[card.hand_id]
		cv2.rectangle(image, (x_l, y_t), (x_r, y_b), colour, 2)
		cv2.rectangle(image, (x_l, y_t-30), (x_l+80, y_t-10), colour, -1)
		cv2.putText(image, f"{card.cls}: {card.conf:.2f}", (x_l, y_t-15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
