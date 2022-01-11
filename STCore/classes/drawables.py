from abc import ABC, abstractmethod
from sys import maxsize
import tkinter as tk
from os.path import basename, getsize
from tkinter import Label, Widget, ttk
from astropy.io.fits import header
from matplotlib import image

import numpy
from PIL import Image, ImageTk

import STCore as st
from STCore import styles
# from ..icons import get_icon
# from STCore import st.styles
#from STCore.item.File import FileItem
#from STCore.item.Star import StarItem
#from STCore.item.Track import TrackItem

# This file contains different UI elements which are repeated along the program

class Drawable (ABC, tk.Widget):
	command : callable = None
	@abstractmethod
	def __init__(self, master : tk.Widget, cmd : callable, *args, **kwargs) -> None:
		raise NotImplementedError()
	
	def bind_cmd(self, tag: str, function : callable):
		self.bind(tag, function)
		for child in self.winfo_children():
			child.bind(tag, function)

	def config(self, **kwargs):
		if "cmd" in kwargs:
			self.command = kwargs["cmd"]
			kwargs.pop("cmd")
		elif "command" in kwargs:
			self.command = kwargs["command"]
			kwargs.pop("command")
		self.configure(**kwargs)

# Levels creates two sliders on the bottom of the ImageView viewport
# It allow to control the brightness and contrast of an image
class LevelsSlider(Drawable, tk.Canvas):	
	def __init__(self, master : tk.Widget, cmd, *args, **kwargs):
		st_base, st_hover, st_press = st.styles.get_resources('handle_base', 'handle_hover', 'handle_press')
		tk.Canvas.__init__(self, master,  *args, **kwargs)
		
		self.configure(bg= master['bg'], highlightthickness=0)
		self.columnconfigure(1, weight=1)
		self.rowconfigure(0, weight=1)
		self.__min = tk.DoubleVar(self.master, value = 0)
		self.__max = tk.DoubleVar(self.master, value = 1)
		
		width = master.winfo_width()
		height = master.winfo_height()
		zero = (0, 0, 0, 0)
		
		label_id =self.create_text(0, 0, text= st.lang.get('levels'), fill='gray70', anchor='nw')
		rail_id = self.create_rectangle(0, 0, 0, 0, fill= 'gray60')
		interval_id = self.create_rectangle(0, 0, 0, 0, fill= styles.hover_highlight)
		
		max_handle_id = self.create_image(0, 0, image= st_base, activeimage= st_hover)
		min_handle_id = self.create_image(0, 0, image= st_base, activeimage= st_hover)

		def get_id(event):
			return event.widget.find_withtag('current')[0]
		def update_wdgt(id, xdata):
			if   id == min_handle_id:
				self.__min.set(value=xdata)
			elif id == max_handle_id:
				self.__max.set(value=xdata)	

			_min_x = self.coords(min_handle_id)[0]
			_max_x = self.coords(max_handle_id)[0]
			self.coords(interval_id, _min_x, height - 3, _max_x, height + 3)
			if cmd:
				cmd(self.__min.get(), self.__max.get())
		def handle_drag(e : tk.Event):
			if e.widget is None:
				return
			
			rel_width = 8/width
			max_cut = self.__max.get()  if get_id(e) == min_handle_id else 1
			min_cut = self.__min.get() + 2*rel_width 	if get_id(e) == max_handle_id else 0

			x = numpy.clip(e.x/ width, min_cut + rel_width, max_cut - rel_width)
			self.coords(get_id(e), x * width,  height)
			update_wdgt(get_id(e), (x - rel_width) * (width + rel_width)/width)

		def on_widget_map(e):
			nonlocal width, height
			width = self.winfo_width()
			height = self.winfo_height() * 0.5

			self.coords(label_id, 0, 0)
			self.coords(rail_id, 0, height - 1, width, height + 1)
			self.coords(interval_id, 0, height - 2, width, height + 2)

			self.coords(min_handle_id, 8, height)
			self.coords(max_handle_id, width -8, height)
			
		
		self.on_config = lambda e: update_wdgt(None, 0)
			
		self.tag_bind(min_handle_id, '<B1-Motion>', handle_drag)
		self.tag_bind(max_handle_id, '<B1-Motion>', handle_drag)
		self.tag_bind(min_handle_id, '<Button>', handle_drag)
		self.tag_bind(max_handle_id, '<Button>', handle_drag)

		self.bind('<Map>', on_widget_map)


		# for x in range(10):
		# 	tk.Grid.columnconfigure(self, x, weight=1)

		# ttk.Label(self, text = "Maximo:").grid(row = 0,column = 0)
		# self.maxScale=ttk.Scale(self, orient=tk.HORIZONTAL,from_=0, to=1, variable = self.__max)
		# self.maxScale.grid(row = 0, column = 1, columnspan = 10, sticky = tk.EW)
		
		# ttk.Label(self, text = "Minimo:").grid(row = 1,column = 0)
		# self.minScale=ttk.Scale(self, from_=0, to= 1, orient=tk.HORIZONTAL, variable = self.__min)
		# self.minScale.grid(row = 1, column = 1, columnspan = 10, sticky = tk.EW)
	def get_value(self) -> tuple:
		return self.__min.get(), self.__max.get()
	def set_value(self, levels : tuple):
		self.minScale.set(levels[0])
		self.maxScale.set(levels[1])
		self.on_config()
# ------------------------------------
class Button(Drawable):
	def __init__(self, master, cmd = None, *args,**kwargs):
		st_base, st_hover, st_press = styles.get_resources('button_base', 'button_hover', 'button_press')
		tk.Label.__init__(self, master, image=st_base, **kwargs)
		self.config(**kwargs)
		self.config(compound ="center", height = 32, width = 164, **styles.BUTTON)
		self.config(bg = master["bg"])
		is_hover = False
		def on_enter(e):
			nonlocal is_hover
			e.widget["image"] = st_hover
			is_hover = True
		def on_leave(e): 
			nonlocal is_hover
			e.widget["image"] = st_base
			is_hover = False
		def on_press(e): 
			e.widget["image"] = st_press
			e.widget["relief"] = "flat"
		def on_release(e): 
			e.widget["image"] = st_base
			e.widget["relief"] = "flat"
			if cmd is not None and is_hover:
				self.command(*args)
		
		self.bind("<Enter>", on_enter)
		self.bind("<Leave>", on_leave)
		self.bind('<Button-1>', on_press)
		self.bind("<ButtonRelease-1>", on_release)
		# self.photo = styles.button_base
	def setup_image(self):
		self.photo = styles.button_base
# ------------------------------------
class HButton(Drawable):
	def __init__(self, master, cmd, *args, **kwargs):
		st_base, st_hover, st_press = styles.get_resources('hbutton_base', 'hbutton_hover', 'hbutton_press')
		tk.Label.__init__(self, master, image=st_base, **kwargs)
		self.config(compound ="center", height = 32, width = 164, **styles.HBUTTON)
		self.command = cmd
		self.config(bg = master["bg"])
		hover = False
		def on_enter(e):
			nonlocal hover
			e.widget["image"] = st_hover
			hover = True
		def on_leave(e): 
			nonlocal hover
			e.widget["image"] = st_base
			hover = False
		def on_press(e): 
			e.widget["image"] = st_press
			e.widget["relief"] = "flat"
		def on_release(e): 
			e.widget["image"] = st_base
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
		# self.photo = styles.button_base
	def setup_image(self):
		self.photo = st.styles.button_base
# ------------------------------------
class Scrollbar(Drawable):
	def __init__(self, master, cmd, *args, **kwargs):
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
		def on_change(value, callback = True):
			self.handle_size = abs(self.range[1] - self.range[0])
			if  self.orientation == 'vertical':
				self.handle.place(rely=value, relheight=self.handle_size)
				self.value = value
			elif self.orientation == 'horizontal':
				self.handle.place(relx=value, relwidth=self.handle_size)
				self.value = value
			if callback:
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

		self.__update_shape = lambda : on_change(self.range[0], False)
		self.__update_value = lambda v: on_change(v, True)
	def set_range(self, lower, upper):
		self.range = (float(lower), float(upper))
		self.__update_shape()
	def set_value(self, value):
		self.__update_value(float(value))
# ------------------------------------
class FileEntry(Drawable):
	def __init__(self, master, cmd,  fileitem : st.classes.items.File, *args, **kwargs):
		tk.Frame.__init__(self, master, **kwargs)
		self.columnconfigure((1,2,3, 4), weight=1, uniform='names')
		self.config(height=48)

		self.file = fileitem
		active_b = tk.Checkbutton(self, width=1)
		filename = tk.Label(self, text= fileitem.name, wraplength=72)
		filedate = tk.Label(self, text= fileitem.date, wraplength=72)
		filesize = tk.Label(self, text= '{0} Mb'.format(fileitem.size))
		delete_b = tk.Button(self,image= styles.get_resource('icon_clear-24'))

		def on_set_active(event, active = True):	
			if active:
				self.config(bg= styles.base_highlight)
				filename.config(**styles.HBUTTON)
				filedate.config(**styles.HBUTTON)
				filesize.config(**styles.HBUTTON)

				active_b.config(**styles.HBUTTON)
				delete_b.config(**styles.HBUTTON)
			else:
				self.config(bg= styles.base_dark)
				filename.config(**styles.LABEL)
				filedate.config(**styles.LABEL)
				filesize.config(**styles.LABEL)

				active_b.config(**styles.DBUTTON)
				delete_b.config(**styles.DBUTTON)
			if cmd is not None and event is not None:
				cmd(self)

		active_b.grid(row= 0, column= 0, sticky='e' )
		filename.grid(row= 0, column= 1, sticky='ew')
		filedate.grid(row= 0, column= 2, sticky='ew')
		filesize.grid(row= 0, column= 3, sticky='ew')
		delete_b.grid(row= 0, column= 4, sticky='w' )

		on_set_active(None, False)
		self.grid_propagate(0)

		self.bind_cmd('<Button>', on_set_active)
		self.__set_active = lambda a: on_set_active(None, a)
	def set_active(self, active : bool):
		self.__set_active(active)

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

	