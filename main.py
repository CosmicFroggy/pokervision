import tkinter as tk
import cv2
from PIL import Image, ImageTk
import kagglehub
from ultralytics import YOLO
import os
import yaml
from sklearn.cluster import DBSCAN

# TODO: put this label generation code in an object somewhere!!

# download playing card dataset using kagglehub
data_path = kagglehub.dataset_download("andy8744/playing-cards-object-detection-dataset")

# get dataset labels
with open(data_path + "/data.yaml", "r") as file:
	data = yaml.safe_load(file)

labels = data["names"]


# class for storing card information, could make cards persistent between
# frames later
class CardPrediction:
	def __init__(self, id, position, left, right, top, bottom, class_id, suit_rank, confidence):
		self.id = id
		self.position = position
		self.left = left
		self.right = right
		self.top = top
		self.bottom = bottom
		self.class_id = class_id
		self.suit_rank = suit_rank
		self.confidence = confidence
		self.hand = -1


	def draw(self, frame):
		cv2.rectangle(frame, 
				 	  (self.left, self.top),
					  (self.right, self.bottom), 
					  (0, 255, 0), 
					  1)
		cv2.circle(frame,
				   self.position,
				   3,
				   (0, 255, 0),
				   -1)
		cv2.putText(frame, 
					f"[{self.id}]{self.suit_rank}({self.hand}): {100*self.confidence:.2f}%", 
					(self.left, self.top - 30), 
					cv2.FONT_HERSHEY_SIMPLEX, 
					0.5, 
					(0, 255, 0), 
					1, 
					cv2.LINE_AA)

# main app class
class App:
	def __init__(self):
		self.root = tk.Tk()
		self.root.title("PokerVision")
		self.root.protocol("WM_DELETE_WINDOW", self.destroy)

		# create video panel
		self.video_panel = tk.Label(self.root)
		self.video_panel.pack()

		# create menu bar
		self.menu_bar = tk.Menu(self.root)
		self.menu_bar.add_command(label="Settings", command=self.open_settings_window)
		self.root.config(menu=self.menu_bar)

		# get camera feed
		self.cam = cv2.VideoCapture(0)

		# camera settings TODO: pull these from config file
		self.cam_settings = {
			cv2.CAP_PROP_AUTOFOCUS : tk.IntVar(value=1),
			cv2.CAP_PROP_FOCUS : tk.IntVar(value=0),
			cv2.CAP_PROP_BRIGHTNESS : tk.IntVar(value=137),
			cv2.CAP_PROP_EXPOSURE : tk.IntVar(value=-3),
			cv2.CAP_PROP_CONTRAST: tk.IntVar(value=50)
		}

		# create model using previously trained weights
		self.model = YOLO("CardDetector.pt")


	def update_cam_setting(self, setting):
		self.cam.set(setting, self.cam_settings[setting].get())


	def open_settings_window(self):
		# vv disable settings button
		self.menu_bar.entryconfig("Settings", state="disabled") 
		settings_window = tk.Toplevel(self.root)
		# vv reenable settings button on window close
		settings_window.protocol("WM_DELETE_WINDOW", 
			lambda: self.close_settings_window(settings_window))
		
		settings_window.title("Settings")
		settings_window.geometry("200x600")

		# settings to be configured
		# TODO: not sure that autofocus or contrast settings working properly!
		# TODO: have sliders update every so often, or asynchronously so that
		# changing settings doesn't slow the whole program down
		# TODO: add settings for clustering to settings window
		tk.Label(settings_window, text="Autofocus").pack()
		tk.Checkbutton(settings_window, 
				       variable=self.cam_settings[cv2.CAP_PROP_AUTOFOCUS],
					   onvalue=1, offvalue=0,
					   command= lambda : self.update_cam_setting(cv2.CAP_PROP_AUTOFOCUS)).pack()
		
		tk.Label(settings_window, text="Focus").pack()
		tk.Scale(settings_window, from_=0, to=255, 
		   		 resolution=5, orient="horizontal", 
				 variable=self.cam_settings[cv2.CAP_PROP_FOCUS],
				 command= lambda _ : self.update_cam_setting(cv2.CAP_PROP_FOCUS)).pack()
		
		tk.Label(settings_window, text="Brightness").pack()
		tk.Scale(settings_window, from_=0, to=255, 
		   		 resolution=5, orient="horizontal", 
				 variable=self.cam_settings[cv2.CAP_PROP_BRIGHTNESS],
				 command= lambda _ : self.update_cam_setting(cv2.CAP_PROP_BRIGHTNESS)).pack()
		
		tk.Label(settings_window, text="Exposure").pack()
		tk.Scale(settings_window, from_=-7, to=-1, 
		   		 resolution=1, orient="horizontal", 
				 variable=self.cam_settings[cv2.CAP_PROP_EXPOSURE],
				 command= lambda _ : self.update_cam_setting(cv2.CAP_PROP_EXPOSURE)).pack()
		
		tk.Label(settings_window, text="Contrast").pack()
		tk.Scale(settings_window, from_=0, to=255, 
		   		 resolution=5, orient="horizontal", 
				 variable=self.cam_settings[cv2.CAP_PROP_CONTRAST],
				 command= lambda _ : self.update_cam_setting(cv2.CAP_PROP_CONTRAST)).pack()


	def close_settings_window(self, window):
		self.menu_bar.entryconfig("Settings", state="normal")
		window.destroy()


	def update(self):
		# read image from camera
		_, frame = self.cam.read()

		# TODO: does the model expect rgb or bgr??? 
		# Tkinter needs rgb either way
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

		frame = self.analyse_frame(frame)

		# convert image to tkinter usable format
		frame = ImageTk.PhotoImage(image=Image.fromarray(frame))

		# update the video panel
		self.video_panel.frame = frame # store reference so not garb-collected
		self.video_panel.config(image=frame)

		# call update again after 10ms
		self.root.after(10, self.update)


	def analyse_frame(self, frame):
		# detect cards
		cards = []
		prediction = self.model.track(frame, verbose=False)[0]
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
			
		return frame
		

	def run(self):
		self.update()
		self.root.mainloop()


	def destroy(self):
		self.cam.release()
		self.root.destroy()


if __name__ == "__main__":
	app = App()
	app.run()