import tkinter as tk
from os import stat
from os.path import basename, getsize
from tkinter import ttk

import numpy
from PIL import Image, ImageTk

from icons import get_icon
from STCore.item.File import FileItem
from STCore.item.Star import StarItem
from STCore.item.Track import TrackItem

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
	def __init__(self, master, star : StarItem, index, command_setstar, command_setguide, command_delete, *args, **kwargs):
		tk.Frame.__init__(self, master, *args, **kwargs)

		self.config(bg="gray10")

		delete_icon = get_icon("delete")
		self.config(bg="gray8")
		self.grid_columnconfigure(1, weight=1)

		cmd_del = lambda: (command_delete(), self.destroy())

		self.gvar = tk.IntVar(value=0)
		self.guide_button = ttk.Radiobutton(self, variable=self.gvar,  value = 1, command=lambda: command_setguide(index))
		self.main_button = ttk.Button(self, text=star.name, command=command_setstar)
		self.deleteButton = ttk.Button(self, image = delete_icon, width = 1, command = cmd_del)
		self.deleteButton.image = delete_icon   
		
		self.guide_button.grid(row=0, column=0, sticky="news")
		self.main_button.grid(row=0, column=1, sticky="news")
		self.deleteButton.grid(row=0, column=2)
	
	def update_star(self, star : StarItem):
		self.main_button.config(text=star.name)
		self.gvar.set(star.type)
	

# TrackElelement displays some information about the curent tracking status
# It is instanced in the sidebar of Tracker
class TrackElement(tk.Frame):
	def __init__(self, master, track : TrackItem, *args, **kwargs):
		tk.Frame.__init__(self, master , *args, **kwargs)

		self.config(bg="gray8")
		self.grid_columnconfigure(tuple(range(2)), weight=1)

		guide = " *" if track.star.type == 1 else ""
		nameLabel = ttk.Label(self, text = track.star.name + guide, font=(None, 15))
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

class FileListElement(tk.Frame):
	def __init__(self, master, item : FileItem, *args, **kwargs):
		tk.Frame.__init__(self, master , *args, **kwargs)
		
		self.styles = {"bg":"gray25", "fg":"gray70", "relief":"flat", "font":(None, 10, "bold"), "wraplength":100}
		self.file = item
		self.rowconfigure((2,3, 4), weight=1)
		self.columnconfigure(tuple(range(10)), weight=1)
		self.config(bg="gray25", height=150)
		self.labels = []

		thumb = self.GetThumbnail()
		self.image = ImageTk.PhotoImage(thumb)
		self.active =tk.IntVar(value=self.file.active)

		thumb_label = tk.Label(self, image =self.image, width = 150)
		thumb_label.image = self.image

		thumb_label.grid(row=0, column=0, rowspan=3, columnspan=3)

	def SetLabels(self, keywords):
		labelcount = len(keywords)

		if len(self.labels) != 4:
			for label in reversed(self.labels):
				label.destroy()
				self.labels.remove(label)
				
		name_label = tk.Label(self,width=20,**self.styles)
		size_label = tk.Label(self,width=12, **self.styles)
		dim_label = tk.Label(self,width=12, **self.styles)

		name_label.config(text = basename(self.file.path), fg="white")
		size_label.config(text = "%.2f Mb" % (getsize(self.file.path) / (1024 * 1024)))
		dim_label.config(text = str(self.file.data.shape))
		
		self.labels.append(name_label)
		self.labels.append(dim_label)

		for i in range(labelcount):
			label = tk.Label(self, width=12 if i != 0 else 20,**self.styles)
			try:
				label.config(text = self.file.header[keywords[i]])
			except:
				label.config(text = "NA")

			self.labels.append(label)
		
		# Size label should be last
		self.labels.append(size_label)

		spacer = tk.Label(self, **self.styles, width=100)
		self.labels.append(spacer)

		index = 0
		for label in self.labels:
			label.grid(row = 2, column = 4 + index, padx = 8, sticky="ew")
			index += 1
		
	def GetThumbnail(self):
		minv = numpy.percentile(self.file.data, 1)
		maxv = numpy.percentile(self.file.data, 99.8)
		thumb = Image.fromarray(numpy.clip(255*(self.file.data - minv)/(maxv - minv), 0, 255).astype(numpy.uint8))
		thumb.thumbnail((150, 150))
			
		return thumb
