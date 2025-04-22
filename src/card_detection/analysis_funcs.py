import cv2
from ultralytics import YOLO
from sklearn.cluster import DBSCAN
import distinctipy


LABELS = ['10c', '10d', '10h', '10s', '2c', '2d', '2h', '2s', '3c', '3d', '3h', '3s', '4c', '4d', '4h', '4s', '5c', '5d', '5h', '5s', '6c', '6d', '6h', '6s', '7c', '7d', '7h', '7s', '8c', '8d', '8h', '8s', '9c', '9d', '9h', '9s', 'Ac', 'Ad', 'Ah', 'As', 'Jc', 'Jd', 'Jh', 'Js', 'Kc', 'Kd', 'Kh', 'Ks', 'Qc', 'Qd', 'Qh', 'Qs']

# generate 15 distinct colours to use to label the groups
COLOURS = list(map(distinctipy.get_rgb256, distinctipy.get_colors(15)))


# create model using previously trained weights
# model = YOLO("CardDetector.pt")
# using model from https://github.com/PD-Mera/Playing-Cards-Detection
# while I fine tune my own
detector_model = YOLO("./res/models/yolov8s_playing_cards.pt")


def detect_cards(image):
	cards = []
	prediction = detector_model.track(image, verbose=False, persist=True)[0]
	if prediction.boxes.id != None:
		for i, box_id in enumerate(prediction.boxes.id):
			# get attributes of identified card
			box_id = box_id.cpu().tolist()
			cls_id = int(prediction.boxes.cls[i].cpu().tolist())
			cls_label = LABELS[cls_id]
			conf = prediction.boxes.conf[i].cpu().tolist()
			x, y, w, h = prediction.boxes.xywh[i].cpu().tolist()
			
			cards.append((box_id, cls_label, conf, x, y, w, h))
	
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
			cls1 = card1[1]
			y1 = card1[4]
			cls2 = card2[1]
			y2 = card2[4]
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
	# using DBSCAN clustering algo to group card hands

	if len(cards) == 0:
		return []

	positions = []
	for card in cards:
		x, y = card[3:5]
		position = (x, y)
		positions.append(position)
	
	# identify hand label for each card
	hand_labels = DBSCAN(eps=eps, min_samples=min_samples).fit(positions).labels_.tolist()

	return hand_labels


def group_hands(card_labels, hand_labels):
	# determine how many hands there is
	unique_hands = set(filter(lambda i : i != -1, hand_labels))
	num_hands = len(unique_hands)

	# create list of n empty hands
	hands = [ [] for i in range(num_hands) ]
	outliers = []

	# groups the cards into hand lists
	for i, hand_label in enumerate(hand_labels):
		if hand_label == -1:
			outliers.append(card_labels[i])
			continue
		hands[hand_label].append(card_labels[i])

	return hands, outliers


def annotate(image, cards, hand_labels):
	# draw the card annotations
	for i, card in enumerate(cards):
		# get attributes
		id, cls, conf, x, y, w, h = card
		x_l, y_t, x_r, y_b = int(x-w/2), int(y-h/2), int(x+w/2), int(y+h/2)
		x, y = int(x), int(y)

		# annotate
		if hand_labels[i] == -1:
			colour = (255, 255, 255)
		else:
			colour = COLOURS[hand_labels[i]]
		cv2.rectangle(image, (x_l, y_t), (x_r, y_b), colour, 2)
		cv2.circle(image, (x, y), 3, (0, 255, 0), -1)
		cv2.putText(image, f"[{id}]{cls}({hand_labels[i]}): {100*conf:.2f}%", (x_l, y_t-30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
