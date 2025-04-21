import cv2
import kagglehub
from ultralytics import YOLO
import yaml
from sklearn.cluster import DBSCAN

from card_detection import CardPrediction


# TODO: put this label generation code in an object somewhere!!

# TODO: probably should hard code the labels so we don't need to download
# the dataset just for the labels

# download playing card dataset using kagglehub
data_path = kagglehub.dataset_download("andy8744/playing-cards-object-detection-dataset")

# get dataset labels
with open(data_path + "/data.yaml", "r") as file:
	data = yaml.safe_load(file)

labels = data["names"]


# create model using previously trained weights
# model = YOLO("CardDetector.pt")
# using model from https://github.com/PD-Mera/Playing-Cards-Detection
# while I fine tune my own
model = YOLO("yolov8s_playing_cards.pt")

def analyse_frame(frame):
		# detect cards
		cards = []
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
			card_names = list(map(lambda cls_id : labels[int(cls_id)], prediction.boxes.cls.cpu().tolist()))
			
		return frame, card_names