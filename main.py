import tkinter as tk
import cv2

class App:
	def __init__(self):
		self.root = tk.Tk()
		self.root.title("PokerVision")

	def run(self):
		self.root.mainloop()


if __name__ == "__main__":
	app = App()
	app.run()