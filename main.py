import tkinter as tk
import cv2
from PIL import Image, ImageTk

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

		self.settings_menu = tk.Menu(self.menu_bar, tearoff=0)
		self.settings_menu.add_command(label="Camera")
		self.settings_menu.add_command(label="Clustering")
		self.menu_bar.add_cascade(menu=self.settings_menu, label="Settings")

		self.root.config(menu=self.menu_bar)

		# get camera feed
		self.cam = cv2.VideoCapture(0)

	def update(self):
		# read image from camera
		_, frame = self.cam.read()

		# convert image to tkinter usable format
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
		frame = ImageTk.PhotoImage(image=Image.fromarray(frame))

		# update the video panel
		self.video_panel.frame = frame # store reference so not garb-collected
		self.video_panel.config(image=frame)

		# call update again after 10ms
		self.root.after(10, self.update)
		
	def run(self):
		self.update()
		self.root.mainloop()

	def destroy(self):
		self.cam.release()
		self.root.destroy()


if __name__ == "__main__":
	app = App()
	app.run()