import tkinter as tk
from tkinter import ttk


class Viewport(ttk.Frame):
	"""Panel used to display a frame of video input."""

	def __init__(self, master):
		"""
		Initialise instance of Viewport.

		Args:
			master (App, or similar tk object): the parent of the Viewport.
		"""

		super().__init__(master)
		self.master = master
		self.view = tk.Label(self)
		self.view.pack()

	def swap_buffer(self, frame):
		"""
		Update the displayed frame.

		Args:
			frame (MatLike): the image to be displayed.
		"""

		self.view.buffer = frame # store reference so not garb-collected
		self.view.config(image=self.view.buffer)