from os import stat
from STCore.item.Track import TrackItem
from STCore.item.Star import StarItem
from STCore.utils.Icons import GetIcon
import tkinter as tk
from tkinter import ttk

# This file contains different UI elements which are repeated along the program

# Levels creates two sliders on the bottom of the ImageView viewport
# It allow to control the brightness and contrast of an image
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

# This class is instancesmin the sidebar of ImageView
# It shows status and properties of the stars created
# Also it allows the user to edit the star
class StarElement(tk.Frame):
	def __init__(self, master, star : StarItem, command_setstar, command_delete, *args, **kwargs):
		tk.Frame.__init__(self, master, *args, **kwargs)

		self.config(bg="gray10")

		delete_icon = GetIcon("delete")
		self.config(bg="gray8")
		self.grid_columnconfigure(tuple(range(1)), weight=1)
		self.grid_columnconfigure(6, weight=0)

		cmd_del = lambda: (command_delete(), self.destroy())

		self.main_button = ttk.Button(self, text=star.name, command=command_setstar)
		self.deleteButton = ttk.Button(self, image = delete_icon, width = 1, command = cmd_del)
		self.deleteButton.image = delete_icon   
		
		self.main_button.grid(row=0, column=0, sticky="news")
		self.deleteButton.grid(row=0, column=1)
	
	def update_star(self, star : StarItem):
		self.main_button.config(text=star.name)

# TrackElelement displays some information about the curent tracking status
# It is instanced in the sidebar of Tracker
class TrackElement(tk.Frame):
	def __init__(self, master, track : TrackItem, *args, **kwargs):
		tk.Frame.__init__(self, master , *args, **kwargs)

		self.config(bg="gray8")
		self.grid_columnconfigure(tuple(range(2)), weight=1)

		nameLabel = ttk.Label(self, text = track.star.name, font=(None, 15))
		posLabel = ttk.Label(self, text = "Posicion")
		lostLabel = ttk.Label(self, text = "Perdidos")
		trustLabel = ttk.Label(self, text = "Confianza")

		variation = 100 * (1 - int(abs(track.currValue - track.star.value) / track.star.value))
		self.lastPos = ttk.Label(self, text = str(track.lastPos))
		self.lost = ttk.Label(self, text = str(len(track.lostPoints)))
		self.trust = ttk.Label(self, text = str(variation))
		self.active = tk.Label(self, text = "Esperando", bg="gray15", fg="green")

		nameLabel.grid(row=0, column=0, sticky="ew")
		posLabel.grid(row=1, column=0, padx=4)
		lostLabel.grid(row=2, column=0, padx=4)
		trustLabel.grid(row=3, column=0, padx=4)

		self.active.grid(row=0, column=1, sticky="ew")
		self.lost.grid(row=2, column=1, padx=4)
		self.lastPos.grid(row=1, column=1, padx=4)
		self.trust.grid(row=3, column=1, padx=4)


	def update_track(self, track : TrackItem):
		variation = int(100 * (1 - abs(track.currValue - track.star.value) / track.star.value))

		if track.active == 1:
			status = "Activo"
			self.active.config(fg = "green")
		elif track.active == 0:
			status = "Perdido"
			self.active.config(fg = "red")
		elif track.active == 2:
			status = "Listo"
			self.active.config(fg = "green")
		elif track.active == -1:
			status = "Esperando"
			self.active.config(fg = "green")

		self.active.config(text= status)
		self.lastPos.config(text = str(track.lastPos))
		self.lost.config(text = str(len(track.lostPoints)))
		self.trust.config(text = str(variation))
