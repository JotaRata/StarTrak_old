import tkinter as tk
from tkinter import ttk

class Levels(tk.Frame):
	
	def __init__(self, master, command, *args, **kwargs):
		tk.Frame.__init__(self, master, *args, **kwargs)

		self.config(bg="gray8")
		self._LEVEL_MIN_ = tk.IntVar(self.master, value = 0)
		self._LEVEL_MAX_ = tk.IntVar(self.master, value = 1)
		self._LEVEL_MIN_.trace("w", lambda a,b,c: command())
		self._LEVEL_MAX_.trace("w", lambda a,b,c: command())

		for x in range(10):
			tk.Grid.columnconfigure(self, x, weight=1)

		ttk.Label(self, text = "Maximo:").grid(row = 0,column = 0)
		self.maxScale=ttk.Scale(self, orient=tk.HORIZONTAL,from_=0, to=1, variable = self._LEVEL_MAX_)
		self.maxScale.grid(row = 0, column = 1, columnspan = 10, sticky = tk.EW)
		
		ttk.Label(self, text = "Minimo:").grid(row = 1,column = 0)
		self.minScale=ttk.Scale(self, from_=0, to= 1, orient=tk.HORIZONTAL, variable = self._LEVEL_MIN_)
		self.minScale.grid(row = 1, column = 1, columnspan = 10, sticky = tk.EW)
	
	def set_limits(self, minimum, maximum):
		self.minScale.config(from_=minimum, to=maximum)
		self.maxScale.config(from_=minimum, to=maximum)
	
	def getMin(self):
		return self._LEVEL_MIN_.get()
	def getMax(self):
		return self._LEVEL_MAX_.get()

	def setMin(self, lvl):
		self._LEVEL_MIN_.set(lvl)
		self.minScale.set(lvl)

	def setMax(self, lvl):
		self._LEVEL_MAX_.set(lvl)
		self.maxScale.set(lvl)
