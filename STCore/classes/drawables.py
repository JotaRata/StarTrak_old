import tkinter as tk
from os import stat
from os.path import basename, getsize
from tkinter import Label, ttk
from astropy.io.fits import header

import numpy
from PIL import Image, ImageTk
from numpy.lib.arraypad import pad

import STCore as st
from STCore import styles
# from ..icons import get_icon
# from STCore import st.styles
#from STCore.item.File import FileItem
#from STCore.item.Star import StarItem
#from STCore.item.Track import TrackItem

# This file contains different UI elements which are repeated along the program

# Levels creates two sliders on the bottom of the ImageView viewport
# It allow to control the brightness and contrast of an image
class LevelsSlider(tk.Frame):	
	def __init__(self, master, command, *args, **kwargs):
		tk.Frame.__init__(self, master, *args, **kwargs)

		self.configure(bg= master['bg'])
		self.columnconfigure(1, weight=1)
		self.rowconfigure(0, weight=1)
		self.__min = tk.DoubleVar(self.master, value = 0)
		self.__max = tk.DoubleVar(self.master, value = 1)

		label = tk.Label(self, text= st.lang.get('levels'), bg= master['bg'], fg= 'gray60')
		rail  = tk.Frame(self, bg= master['bg'], height=34)

		tk.Frame(rail, height=3, bg= 'gray40').place(rely=0.5, relx=0, relwidth=1)
		interval= tk.Frame(rail, bg= styles.hover_highlight)
		max_handle = tk.Label(rail, image = styles.handle_base, compound='center', bg=master['bg'], cursor='sb_h_double_arrow')
		min_handle = tk.Label(rail, image = styles.handle_base, compound='center', bg=master['bg'], cursor='sb_h_double_arrow')
		interval.place(rely=0.5, height= 5)

		def update_wdgt(widget, xdata):
			if   widget is min_handle:
				self.__min.set(value=xdata)
			elif widget is max_handle:
				self.__max.set(value=xdata)	
			interval.place(x= min_handle.winfo_x(), width= (max_handle.winfo_x() - min_handle.winfo_x()))	
		def handle_drag(e : tk.Event):
			if e.widget is None:
				return
			rel_w = 16 / rail.winfo_width()
			max_cut = self.__max.get() if e.widget is min_handle else 1
			min_cut = self.__min.get() + rel_w if e.widget is max_handle else 0

			x = (e.x + e.widget.winfo_x() - 8) / rail.winfo_width()
			x = numpy.clip(x, min_cut, max_cut - rel_w)
			e.widget.place(relx= x)
			update_wdgt(e.widget, x)
		def handle_hover(e : tk.Event):
			e.widget['image'] = styles.handle_hover
		def handle_release(e : tk.Event):
			e.widget['image'] = styles.handle_base
		def handle_press(e : tk.Event):
			e.widget['image'] = styles.handle_press
		self.on_config = lambda e: update_wdgt(None, 0)
			
		min_handle.place(y=1, relx= 0, width=16, height=32)
		max_handle.place(y=1, relx= 0.5, width=16, height=32)

		min_handle.bind('<B1-Motion>',    handle_drag)
		min_handle.bind('<Button>', 	  handle_press)
		min_handle.bind('<Enter>',		  handle_hover)
		min_handle.bind('<Leave>', 		  handle_release)
		min_handle.bind('<ButtonRelease>',handle_release)

		max_handle.bind('<B1-Motion>',    handle_drag)
		max_handle.bind('<Button>', 	  handle_press)
		max_handle.bind('<Enter>',		  handle_hover)
		max_handle.bind('<Leave>', 		  handle_release)
		max_handle.bind('<ButtonRelease>',handle_release)
		max_handle.bind('<Map>', self.on_config)

		label.grid(row=0, column=0)
		rail.grid(row=0, column=1, sticky='news', padx=4)


		# for x in range(10):
		# 	tk.Grid.columnconfigure(self, x, weight=1)

		# ttk.Label(self, text = "Maximo:").grid(row = 0,column = 0)
		# self.maxScale=ttk.Scale(self, orient=tk.HORIZONTAL,from_=0, to=1, variable = self.__max)
		# self.maxScale.grid(row = 0, column = 1, columnspan = 10, sticky = tk.EW)
		
		# ttk.Label(self, text = "Minimo:").grid(row = 1,column = 0)
		# self.minScale=ttk.Scale(self, from_=0, to= 1, orient=tk.HORIZONTAL, variable = self.__min)
		# self.minScale.grid(row = 1, column = 1, columnspan = 10, sticky = tk.EW)
	def get(self) -> tuple:
		return self.__min.get(), self.__max.get()
	def set(self, levels : tuple):
		self.minScale.set(levels[0])
		self.maxScale.set(levels[1])
		self.on_config()
	def config(self, **kwargs):
		if "cmd" in kwargs:
			self.command = kwargs["cmd"]
			kwargs.pop("cmd")
		elif "command" in kwargs:
			self.command = kwargs["command"]
			kwargs.pop("command")
		self.configure(**kwargs)
# ------------------------------------
class Button(tk.Label):
	def __init__(self, master, cmd = None, *args,**kwargs):
		tk.Label.__init__(self, master, image=st.styles.button_base, **kwargs)
		self.config(**kwargs)
		self.config(compound ="center", height = 32, width = 164, **st.styles.BUTTON)
		self.config(bg = master["bg"])
		hover = False
		def on_enter(e):
			nonlocal hover
			e.widget["image"] = st.styles.button_hover
			hover = True
		def on_leave(e): 
			nonlocal hover
			e.widget["image"] = st.styles.button_base
			hover = False
		def on_press(e): 
			e.widget["image"] = st.styles.button_press
			e.widget["relief"] = "flat"
		def on_release(e): 
			e.widget["image"] = st.styles.button_base
			e.widget["relief"] = "flat"
			if cmd is not None and hover:
				self.command(*args)
		
		self.bind("<Enter>", on_enter)
		self.bind("<Leave>", on_leave)
		self.bind('<Button-1>', on_press)
		self.bind("<ButtonRelease-1>", on_release)
		# self.photo = st.styles.button_base
	def setup_image(self):
		self.photo = st.styles.button_base
	def config(self, **kwargs):
		if "cmd" in kwargs:
			self.command = kwargs["cmd"]
			kwargs.pop("cmd")
		if "command" in kwargs:
			self.command = kwargs["command"]
			kwargs.pop("command")
			
		self.configure(**kwargs)
# ------------------------------------
class HButton(tk.Label):
	def __init__(self, master, cmd, args = None,**kwargs):
		tk.Label.__init__(self, master, image=st.styles.hbutton_base, **kwargs)
		self.config(compound ="center", height = 32, width = 164, **st.styles.HBUTTON)
		self.command = cmd
		self.config(bg = master["bg"])
		hover = False
		def on_enter(e):
			nonlocal hover
			e.widget["image"] = st.styles.hbutton_hover
			hover = True
		def on_leave(e): 
			nonlocal hover
			e.widget["image"] = st.styles.hbutton_base
			hover = False
		def on_press(e): 
			e.widget["image"] = st.styles.hbutton_press
			e.widget["relief"] = "flat"
		def on_release(e): 
			e.widget["image"] = st.styles.hbutton_base
			e.widget["relief"] = "flat"
			if self.command is not None and hover:
				if args is None:
					self.command()
				else:
					self.command(*args)
		
		self.bind("<Enter>", on_enter)
		self.bind("<Leave>", on_leave)
		self.bind('<Button-1>', on_press)
		self.bind("<ButtonRelease-1>", on_release)
		# self.photo = st.styles.button_base
	def setup_image(self):
		self.photo = st.styles.button_base
	def config(self, **kwargs):
		if "cmd" in kwargs:
			self.command = kwargs["cmd"]
			kwargs.pop("cmd")
		if "command" in kwargs:
			self.command = kwargs["command"]
			kwargs.pop("command")
			
		self.configure(**kwargs)
# ------------------------------------
class Scrollbar(tk.Frame):
	def __init__(self, master, cmd= None, **kwargs):
		tk.Frame.__init__(self, master, **kwargs)
		
		if 'bg' not in kwargs:
			self.config(bg= master['bg'], border=1)
		self.config(border=1)

		rail = tk.Frame(self, bg= styles.hover_highlight)
		self.handle = tk.Label(self, bg= styles.base_highlight)
		self.orientation = 'vertical'
		self.range = (0, 1)
		self.value = 0
		self.command = cmd
		def on_config(e : tk.Event):
			self.handle_size = abs(self.range[1] - self.range[0])
			self.orientation = 'vertical' if self.winfo_height() > self.winfo_width() else 'horizontal'
			if 	 self.orientation == 'vertical':
				self.handle.place(rely=self.value, relwidth=1, relheight=self.handle_size)
				rail.place(relx=0.5, relheight=1, width=2, anchor='n')
			elif self.orientation == 'horizontal':
				self.handle.place(relx=self.value, relheight=1, relwidth= self.handle_size)
				rail.place(rely=0.5, relwidth=1, height=2, anchor='e')
		def on_change(value):
			self.handle_size = abs(self.range[1] - self.range[0])
			if  self.orientation == 'vertical':
				self.handle.place(rely=value, relheight=self.handle_size)
				self.value = value
			elif self.orientation == 'horizontal':
				self.handle.place(relx=value, relwidth=self.handle_size)
				self.value = value
			self.command(value)
		def on_hover(e : tk.Event):
			self.handle['bg'] = styles.hover_highlight
		def on_release(e : tk.Event):
			self.handle['bg'] = styles.base_highlight
		def on_press(e : tk.Event):
			self.handle['bg'] = styles.press_highlight
		def on_drag(e : tk.Event):
			if e.widget is not self.handle:
				return
			on_press(e)
			rel_pos = 0
			if   self.orientation == 'vertical':
				rel_pos = (e.y + e.widget.winfo_y()) / self.winfo_height() - self.handle_size*0.5
			elif self.orientation == 'horizontal':
				rel_pos = (e.x + e.widget.winfo_x()) / self.winfo_width() - self.handle_size*0.5
			on_change(rel_pos)

		self.handle.bind('<B1-Motion>', on_drag)
		self.handle.bind('<Button>', on_press)
		self.handle.bind('<Enter>', on_hover)
		self.handle.bind('<Leave>', on_release)
		self.handle.bind('<ButtonRelease>', on_release)
		self.bind('<Map>', on_config)

		self.__update_shape = lambda: on_change(self.value)
		self.__update_value = lambda v: on_change(v)
	def config(self, **kwargs):
		if "cmd" in kwargs:
			self.command = kwargs["cmd"]
			kwargs.pop("cmd")
		elif "command" in kwargs:
			self.command = kwargs["command"]
			kwargs.pop("command")
		self.configure(**kwargs)
	def set_range(self, lower, upper):
		self.range = (float(lower), float(upper))
		self.__update_shape()
	def set_value(self, value):
		self.__update_value(float(value))
# ------------------------------------
class FileEntry(tk.Frame):
	def __init__(self, master, fileitem : st.classes.items.File, **kwargs):
		tk.Frame.__init__(self, master, **kwargs)
		self.columnconfigure((1,2,3, 4), weight=1)
		self.rowconfigure(0, weight=1)
		self.config(bg= styles.base_dark, height=48)

		active   = tk.Checkbutton(self, width=1, **styles.DBUTTON)
		filename = tk.Label(self, text= fileitem.name, **styles.LABEL)
		filedate = tk.Label(self, text= fileitem.date, **styles.LABEL)
		filesize = tk.Label(self, text= getsize(fileitem.path), **styles.LABEL)
		delete   = tk.Button(self,text= 'del', **styles.DBUTTON)

		active.grid(row= 0, column= 0, sticky='e')
		filename.grid(row= 0, column= 1, sticky='ew')
		filedate.grid(row= 0, column= 2, sticky='ew')
		filesize.grid(row= 0, column= 3, sticky='ew')
		delete.grid(row= 0, column= 4, sticky='w')

		self.grid_propagate(0)

# ------------------------------------
# This class is instancesmin the sidebar of ImageView
# It shows status and properties of the stars created
# Also it allows the user to edit the star
class StarElement(tk.Frame):
	def __init__(self, master, star : st.classes.items.Star, index, command_setstar, command_setguide, command_delete, *args, **kwargs):
		tk.Frame.__init__(self, master, *args, **kwargs)

		self.config(bg="gray10")

		delete_icon = st.icons.get_icon("delete")
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
	
	def update_star(self, star : st.classes.items.Star):
		self.main_button.config(text=star.name)
		self.gvar.set(star.type)
# ------------------------------------
# TrackElelement displays some information about the curent tracking status
# It is instanced in the sidebar of Tracker
class TrackElement(tk.Frame):
	def __init__(self, master, track : st.classes.items.Track, *args, **kwargs):
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


	def update_track(self, track : st.classes.items.Track):
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
# ------------------------------------

class FileListElement(tk.Frame):
	def __init__(self, master, item : st.classes.items.File, *args, **kwargs):
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

	