import tkinter as tk
from tkinter import ttk


class Viewport(ttk.Frame):
	def __init__(self, master):
		super().__init__(master)
		self.master = master
		self.view = tk.Label(self)
		self.view.pack()

	def swap_buffer(self, frame):
		self.view.buffer = frame # store reference so not garb-collected
		self.view.config(image=self.view.buffer)