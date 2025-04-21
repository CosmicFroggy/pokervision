import cv2
import kagglehub
from ultralytics import YOLO
import yaml
from sklearn.cluster import DBSCAN

from card_detection import CardPrediction


labels = ['10c', '10d', '10h', '10s', '2c', '2d', '2h', '2s', '3c', '3d', '3h', '3s', '4c', '4d', '4h', '4s', '5c', '5d', '5h', '5s', '6c', '6d', '6h', '6s', '7c', '7d', '7h', '7s', '8c', '8d', '8h', '8s', '9c', '9d', '9h', '9s', 'Ac', 'Ad', 'Ah', 'As', 'Jc', 'Jd', 'Jh', 'Js', 'Kc', 'Kd', 'Kh', 'Ks', 'Qc', 'Qd', 'Qh', 'Qs']



# create model using previously trained weights
# model = YOLO("CardDetector.pt")
# using model from https://github.com/PD-Mera/Playing-Cards-Detection
# while I fine tune my own
model = YOLO("./res/models/yolov8s_playing_cards.pt")

def analyse_frame(frame):
		# detect cards
		cards = []
		card_names = []
		prediction = model.track(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), verbose=False, persist=True)[0]
		
		if prediction.boxes.id != None:
			for i, box_id in enumerate(prediction.boxes.id):
				# get attributes of identified card
				x1, y1, x2, y2 = prediction.boxes.xyxy[i]
				x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
				cx, cy, _, _ = prediction.boxes.xywh[i]
				cx, cy = int(cx), int(cy)
				class_id = int(prediction.boxes.cls[i])
				conf = prediction.boxes.conf[i]

				# create new prediction object and add to list
				cards.append(CardPrediction(box_id, (cx, cy), x1, x2, y1, y2, class_id, labels[class_id], conf))

			# using DBSCAN clustering algo to group card hands
			positions = []
			for card in cards:
				positions.append(card.position)
			hand_labels = DBSCAN(eps=100, min_samples=2).fit(positions).labels_
			for i, label in enumerate(hand_labels):
				cards[i].hand = label

			# draw the card annotations
			for card in cards:
				card.draw(frame)

			# draw hand clustering
			for i, card1 in enumerate(cards):
				if i == len(cards) - 1:
					break
				for card2 in cards[i+1:]:
					if card1.hand != -1 and card1.hand == card2.hand:
						cv2.line(frame, 
								card1.position, 
								card2.position, 
								(0, 255, 0), 
								2)
						
			# get the names of the detected cards
			cls_list = prediction.boxes.cls.cpu().tolist()
			card_names = [ labels[int(cls_id)] for cls_id in cls_list ]
			
		return frame, card_names