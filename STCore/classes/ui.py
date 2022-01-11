import os
import tkinter as tk
from abc import ABC, abstractmethod
from os.path import basename
from tkinter import Frame, Toplevel, filedialog, ttk

from matplotlib.pyplot import colormaps

import STCore as st

from matplotlib import use
use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.colors import Normalize, LogNorm, PowerNorm
from STCore import debug, styles
from STCore.bin import env
#from STCore import Settings, Tools
from STCore.bin.data_management import SessionManager
from STCore.classes.drawables import (Button, FileEntry, FileListElement,
                                      HButton, LevelsSlider, Scrollbar)
from STCore.classes.items import File
from STCore.icons import get_icon

from queue import Queue
from threading import Thread, Timer

import time

def_keywords = ["DATE-OBS", "EXPTIME", "OBJECT", "INSTRUME"]
#-----------------------------------------

# Base abstract class for instancing windows
class STView(ABC):
	callbacks : dict = NotImplemented

	@abstractmethod
	def __init__(self) -> None:
		pass
	
	@abstractmethod
	def build(self, master):
		raise NotImplementedError()

	@abstractmethod
	def close(self, master):
		raise NotImplementedError()
	
	def config_callback(self, **args):
		self.callbacks = args
	
	def get_callback(self, name : str) -> callable:
		def __nothing(*args, **kwargs):
			pass
		
		if name in self.callbacks:
			return self.callbacks[name]
		else:
			debug.warn(__name__, f'The object of type {self.__class__.__name__} don\'t have a callable property named {name}')
			return __nothing

#-------------------------------------------
# Class for managing the selector window UI
class SelectorUI(STView, tk.Frame):
	def __init__(self, master, *args, **kwargs):
		tk.Frame.__init__(self, master, *args, **kwargs)
		self.config(**styles.SFRAME)

		elements : list[tuple[File, FileEntry]] = []
		
		#session_manager.CurrentWindow = 1
		canvas = tk.Canvas(self, scrollregion= (0, 0, 0, 0), highlightthickness=0, **styles.FRAME)
		scrollbar = Scrollbar(self, width= 12, cmd= canvas.yview_moveto)
		frame = tk.Frame(canvas, **styles.HFRAME)
		window = canvas.create_window(0, 0, window=frame, anchor='nw')
		header = tk.Frame(self, height=72,**styles.SFRAME)
		footer = tk.Frame(self, height=72,**styles.SFRAME)

		self.columnconfigure(0, weight=1)
		self.rowconfigure(1, weight=1)
		frame.columnconfigure(0,weight=1)
		def on_mouse_scroll(e : tk.Event):
			scroll = -1 if e.delta > 0 else 1
			canvas.yview_scroll(scroll, "units")
			scrollbar.set_range(*canvas.yview())
		def on_config(e):
			canvas.itemconfig(window, width=self.winfo_width())
			canvas.config(scrollregion= canvas.bbox('all'))
		def on_list_append(e):
			item = FileEntry(frame, on_item_select, e)
			elements.append((e, item))
			item.grid(row= len(elements), column= 0, sticky='ew', pady=2, padx=4)
			canvas.update_idletasks()
		def on_file_add():
			files = filedialog.askopenfilenames()
			for file in files:
				item = File(basename(file) , file)
				item.date_from_file()
				on_list_append(item)
			on_config(None)
		def on_item_select(selected : FileEntry):
			item : FileEntry
			for el, item in elements:
				if item is not selected:
					item.set_active(False)
				else:
					self.get_callback('on_file_select')(item.file)
		def build_header():
			header.columnconfigure((0, 4), minsize=16)
			header.columnconfigure((1,2,3, 4), weight=1, uniform='names')
			header.rowconfigure((0, 1), weight=1)

			tk.Label(header, text= 'Nombre'	, **styles.SLABEL).grid(row= 1, column=1, sticky='ew')
			tk.Label(header, text= 'Fecha'	, **styles.SLABEL).grid(row= 1, column=2, sticky='ew')
			tk.Label(header, text= 'Tamaño'	, **styles.SLABEL).grid(row= 1, column=3, sticky='ew')	

			header.grid_propagate(0)
		def build_footer():
			footer.columnconfigure((0,1), weight=1)
			add_button = HButton(footer, on_file_add, text= "Añadir archivos")
			clear_button = Button(footer, on_list_append, text= "Limpiar lista")

			add_button.grid(row= 0, column= 0, sticky='news')
			clear_button.grid(row= 0, column= 1, sticky='news')
		
		canvas.config(yscrollcommand= scrollbar.set_range)
		canvas.grid(row= 1, column=0, sticky='news', padx=8, pady= 4)
		scrollbar.grid(row= 1, column=1, sticky='ns')
		
		build_header()
		header.grid(row= 0, column=0, columnspan=2, sticky='ew')
		build_footer()
		footer.grid(row= 2, column=0, columnspan=2, sticky='ew')
		
		self.__add = lambda e : on_list_append(e)
		self.bind('<Map>', on_config)

		canvas.bind_all('<MouseWheel>', on_mouse_scroll)
	
	def add_element(self, item : File):
		self.__add(item)
	def build(self, master):
		pass
		
	def close(self, master):
		self.destroy()

	def create_canvas(self):
		self.scroll_view = tk.Canvas(self, bg= "gray15", bd=0, relief="flat", highlightthickness=0)
		scrollbar = ttk.Scrollbar(self, command=self.scroll_view.yview)
		self.scroll_view.config(yscrollcommand=scrollbar.set)  

		self.list_frame = ttk.Frame(self.scroll_view)
		self.list_frame.columnconfigure(0, weight=1)
		self.scroll_view.create_window(0, 0, anchor = tk.NW, window = self.list_frame)
		scrollbar.grid(row=1, column=3, rowspan=3, sticky="ns")

	def create_sidebar(self, master):
		self.sidebar = ttk.Frame(self, width = 200)
		self.sidebar.columnconfigure(0, weight=1)

		self.clear_button = ttk.Button(self.sidebar, text="Limpiar todo",  image = get_icon("delete"), compound = "right")	
		self.add_button = ttk.Button(self.sidebar, text=  "Agregar archivo", image = get_icon("multi"), compound = "right")
		self.apply_button = ttk.Button(self.sidebar, text="Continuar", image = get_icon("next"), compound = "right")
		
		self.add_button.config(style="Highlit.TButton")

		self.clear_button.grid(row=2, column=0, sticky = "ew", pady=5)
		self.add_button.grid(row=1, column=0, sticky = "ew", pady=5)
		self.apply_button.grid(row=0, column=0, sticky = "ew", pady=5)

		self.clear_button.config(state = tk.NORMAL)
		self.apply_button.config(state = tk.NORMAL)
		self.add_button.config(state = tk.NORMAL)

	def create_header(self, keywords):
		self.header = tk.Frame(self,bg = "gray40", height=24)
		self.header_buttons = []
		#Header.columnconfigure((tuple(range(10))), weight=1)
		dargs = {"font":(None, 11), "bg":"gray30", "fg":"white", "bd":1, "relief":tk.RIDGE}
		args = {"row":0, "sticky":"news", "ipadx":2}

		tk.Label(self.header, text= "Vista previa", width=16, **dargs).grid(column=0, **args)
		tk.Label(self.header, text= "Nombre", width = 20, **dargs).grid(column=1, **args)
		tk.Label(self.header, text= "Dimensiones", width=12, **dargs).grid(column=2, **args)
		tk.Label(self.header, text= "Tamaño", width=12, **dargs).grid(column= 4 + len(keywords), **args)

		index = 0
		for key in keywords:
			button = tk.Button(self.header, text=key+" ▼", width=12 if index != 0 else 20, cursor="hand2", highlightcolor="gray50", **dargs)
			button.grid(column= 3 + index, **args)
			index += 1
			self.header_buttons.append((button, key))
	
	def create_element(self, index, item, keywords):
		element = FileListElement(self.list_frame, item)
		element.SetLabels(keywords)
		element.grid(row=index, sticky="ew", pady=4)
		self.list_frame.append(element)

	def update_elements(self, keywords):
	
		for element in self.list_frame:
			element.SetLabels(keywords)

	def update_header(self, sample_item : File):		
		i = 0
		keys = def_keywords
		def SetKey(bindex, key):
			nonlocal keys
			button = self.header_buttons[bindex][0]
			button.config(text= key + " ▼", state="normal")
			self.header_buttons[bindex] = button, key
			keys[bindex] = key

			self.update_elements(keys)

		def OpenEnum(index, event):
			nonlocal sample_item
			menu = tk.Menu(self.header)
			for key in sample_item.header:
				menu.add_command(label=key, command=lambda b=index, k=key : SetKey(b, k))
			menu.post(event.x_root, event.y_root)

		for button, key in self.header_buttons:
			button.bind("<Button-1>", lambda event, index = i: OpenEnum(index, event))
			
			i += 1
#-------------------------------------------

class MainScreenUI (STView, tk.Frame):
	def __init__(self, master, *args, **kwargs):
		tk.Frame.__init__(self, master, *args, **kwargs)
		# TODO Move to another script
		#recent_manager.CurrentWindow = 0
		#Tracker.DataChanged = False
		self.set_window_name(master)
		self.create_sidebar()
		self.create_top()
		self.config(**st.styles.FRAME)
		self.columnconfigure((1), weight=1)
		self.rowconfigure((1), weight=1)

		self.sidebar.grid(row=0, column=0, rowspan=2, sticky='ns')
		self.bottombar.grid(row=0, column=1, columnspan=2, sticky='ew')

	def build(self, master):
		#self.pack(expand=1, fill = "both")
		self.session_button.config(cmd = self.callbacks["toplevel"])
		#self.load_button.config(command = Tools.OpenFileCommand)
		#self.create_recent(master)

	def close(self, master):
		self.sidebar.destroy()
		self.bottombar.destroy()
		self.destroy()

	def create_top(self):
		self.bottombar = tk.Frame(self, height=64, **st.styles.SFRAME)
		
		self.session_button = HButton(self.bottombar, None, text = "Nueva Sesion", width=196)
		self.session_button.pack(side= tk.RIGHT, anchor = tk.E)

		self.load_button = Button(self.bottombar, None, text = "Cargar Sesion", width=196)
		self.load_button.pack(side= tk.RIGHT, anchor = tk.E, after=self.session_button)

	def create_sidebar(self):
		self.sidebar = tk.Frame(self, width=300, bg = st.styles.base_light)
		logo = tk.PhotoImage(file ="STCore/StarTrak.png")
		logo_label = tk.Label(self.sidebar,image= logo, bg = st.styles.base_light)
		logo_label.photo = logo
		logo_label.pack(pady=16)

		tk.Label(self.sidebar, text = "Bienvenido a StarTrak",font="-weight bold", **st.styles.SLABEL, background = st.styles.hover_primary).pack(pady=16)

	# def create_recent(self, master):
		# if Settings._RECENT_FILES_.get() == 1:
		# 	self.recent_label = tk.LabelFrame(self, text = "Archivos recientes:", bg="gray18", fg="gray90", relief="flat", font="-weight bold")
		# 	self.recent_label.pack(anchor = tk.NW, pady=16, expand=1, fill=tk.BOTH)

		# 	ttk.Label(self.recent_label).pack()
		# 	for p in reversed(recent_manager.recent_files):
		# 		recent_elem = ttk.Button(self.recent_label, text = p[0], cursor="hand2", style= "Highlight.TButton")
		# 		recent_elem.config(command= lambda : self.callbacks["load_data"](p[1], master))
		# 		recent_elem.pack(anchor = tk.W, pady=4, fill=tk.X)
		# 		ttk.Button(recent_elem, image=get_icon("delete"), command=lambda:self.remove_recent(p, master), style="Highlight.TButton").pack(side=tk.RIGHT)
	# def remove_recent(self, path, master):
	# 	recent_manager.recent_files.remove(path)
	# 	recent_manager.save_recent()()
	# 	self.recent_label.destroy()
	# 	self.create_recent(master)


	def set_window_name(self, master):
		master.wm_title(string = "StarTrak 1.2.0")
		if env.session_manager is None:
			return
		if len(env.session_manager.current_path) > 0:
			master.wm_title(string = "StarTrak 1.2.0 - "+ os.basename(env.session_manager.current_path))
#-------------------------------------------

class SessionDialog(STView, tk.Toplevel):
	def __init__(self, master : tk.Tk, *args, **kwargs) :
		center = (master.winfo_width()/2 + master.winfo_x() - 360 + 100,  master.winfo_height()/2 + master.winfo_y() - 240 + 60)
		Toplevel.__init__(self, master, *args, **kwargs)
		
		self.config(bg = st.styles.press_primary, bd=4)
		self.session = SessionManager()
		self.geometry("720x480+%d+%d" % center)
		self.grab_set()
		try:	 # If is Linux
			self.wm_attributes('-type', 'splash')
		except:	 # If is Windows
			self.overrideredirect(True)
			
		self.rowconfigure((6), weight=1)
		self.columnconfigure(( 1), weight=1)
		self.wm_title(string = "Nueva Sesion")
		self.name_var = tk.StringVar(self, value="Nueva Sesion")

		tk.Label(self, text="Crear nueva sesion", font="-weight bold", bg = st.styles.press_primary, fg="white").grid(row= 0, columnspan=2 , sticky="ew")
		tk.Label(self, text="Nombre de la sesion:",  bg = st.styles.press_primary, fg="gray60", font = (None, 12)).grid(row= 1, column= 0, sticky="ew", pady=12)

		self.load_frame = tk.Frame(self, bg= st.styles.press_primary, height=128)
		self.info_label = None
		
		entry = tk.Entry(self, textvariable= self.name_var, font=(None, 16), bg = st.styles.press_primary, fg ="gray80")
		entry.grid(row= 1, column= 1, sticky="ew", padx=8)

		rtsession = tk.Frame(self ,height=8, **st.styles.SFRAME)
		assession = tk.Frame(self ,height=8, **st.styles.SFRAME)

		rtsession.grid(row= 3, columnspan=2,  sticky="news", pady=4)
		assession.grid(row= 4, columnspan=2,  sticky="news", pady=4)

		rt_cmd = lambda e: self.set_mode(0, rtsession, assession)
		as_cmd = lambda e: self.set_mode(1, rtsession, assession)

		rtsession.bind('<Button-1>', rt_cmd)
		assession.bind('<Button-1>', as_cmd)

		rt_title = tk.Label(rtsession,text="Analisis en tiempo real", justify="center",font="-weight bold", **st.styles.HLABEL)
		as_title = tk.Label(assession,text="Analisis asincrono", justify="center", font="-weight bold", **st.styles.HLABEL)
		
		rt_title.pack(fill="x")
		as_title.pack(fill="x")
		
		rt_label = tk.Label(rtsession, text="Comienza un analisis fotometrico en tiempo real con el telescopio\nDebes seleccionar un archivo de muestra que se encuentre en la misma carpeta donde se exportaran los archivos FITS desde el CCD", **st.styles.LABEL)
		as_label = tk.Label(assession, text="Selecciona varias imagenes tomadas anteriormente para comenzar un analisis fotometrico de estas\nTambien puedes apilar estas imagenes", **st.styles.LABEL)

		as_label.pack(fill="x")
		rt_label.pack(fill="x")
		
		rt_title.bind('<Button-1>', rt_cmd)
		as_title.bind('<Button-1>', as_cmd)

		rt_label.bind('<Button-1>', rt_cmd)
		as_label.bind('<Button-1>', as_cmd)
		self.set_mode(-1, rtsession, assession)
		
		self.load_frame.grid(row=5, columnspan=2, sticky="news")

		button_frame = tk.Frame(self, **st.styles.SFRAME)
		button_frame.grid(row=7, columnspan=2, sticky="ew")

		HButton(button_frame, text = "Continuar", cmd=	lambda:self.apply(master), width=40).pack(side=tk.RIGHT, pady=16, padx=8)
		Button(button_frame, text = "Cancelar", cmd=	lambda:self.close(master), width=32).pack(side=tk.RIGHT, pady=16, padx=8)
		
		def raise_level(event):
			self.attributes('-topmost', 1)
			self.attributes('-topmost', 0)
		def sync_windows(event):
			raise_level(event)
			x = master.winfo_width()/2 + master.winfo_x() - 360 + 100
			y = master.winfo_height()/2 + master.winfo_y() - 240 + 60
			self.geometry("720x480+%d+%d" % (x,y)) 

		self.sync_call = master.bind("<Configure>", lambda e : sync_windows(e))
		self.raise_call= master.bind("<FocusIn>", 	lambda e : raise_level(e))

	def build(self, master):
		pass
	
	def close(self, master):
		master.unbind("<FocusIn>", self.raise_call)
		master.unbind("<Configure>", self.sync_call)
		self.grab_release()
		self.destroy()	
	
	def apply(self, master):
		self.session.session_name = str(self.name_var.get())
		if self.session.runtime == 0:
			self.close(master)
			#RuntimeAnalysis.startFile = directory_path
			#RuntimeAnalysis.Awake(root)
		if self.session.runtime == 1:
			self.close(master)
			#Destroy()
			#ImageSelector.Awake(root, file_paths)

	def get_filepaths(self):
		file_paths = filedialog.askopenfilenames(parent = self, filetypes=[("FIT Image", "*.fits;*.fit"), ("Todos los archivos",  "*.*")])
		if self.info_label is not None:
			self.info_label.config(text="Se seleccionaron %o archivos" % len(file_paths))
		
		for path in file_paths:
			file_ref = File(path, simple=True)
			self.session.file_refs.append(file_ref)

	def get_directory(self):
		path = filedialog.askdirectory(parent=self)
		if self.info_label is not None:
			self.info_label.config(text="Directorio de la sesion:\n"+path)
		self.session.current_path = path

	def set_mode(self, mode, rtbutton, asbutton):
		self.session.runtime = mode == 1

		selectText = ""
		if mode == 0:
			
			for c in self.load_frame.winfo_children():
				c.destroy()
			tk.Label(self.load_frame, text="Abrir la primera imagen de la sesion", **st.styles.LABEL).pack()
			Button(self.load_frame, text="Arbir archivo", cmd=self.get_directory, width=28).pack()
		
		if mode == 1:
			for c in self.load_frame.winfo_children():
				c.destroy()
			
			tk.Label(self.load_frame, text="Abrir varias imagenes", **st.styles.LABEL).pack()
			Button(self.load_frame, text="Arbir archivos", cmd=self.get_filepaths, width=28).pack()

		self.info_label = tk.Label(self.load_frame, text = "", **st.styles.LABEL)
		self.info_label.pack()

		rtbutton.config(bg = st.styles.base_highlight if mode == 0 else st.styles.base_primary)
		for c in rtbutton.winfo_children():
			c.config(bg = st.styles.base_highlight if mode == 0 else st.styles.base_primary, fg = "white" if mode == 0 else "gray70")

		asbutton.config(bg = st.styles.base_highlight if mode == 1 else st.styles.base_primary)
		for c in asbutton.winfo_children():
			c.config(bg = st.styles.base_highlight if mode == 1 else st.styles.base_primary, fg = "white" if mode == 1 else "gray70")
#-------------------------------------------

class ViewerUI(STView, tk.Frame):
	def __init__(self, master):
		tk.Frame.__init__(self, master, **st.styles.HFRAME)
		self.config(bg= styles.base_dark)

		data_range   : tuple = (0, 1)
		implot = None
		self.norm 	 : Normalize = None

		tk.Label(self, bg= self['bg'], fg='gray70', text="Archivo").grid(row=0, columnspan=22)
		
		fig	= Figure(figsize = (10,7), dpi = 100)
		fig.set_facecolor("black")
		axis : Axes = fig.add_subplot(111)
		axis.imshow(((0,0),(0,0)), cmap='gray')
		axis.text(0.5, 0.5, st.lang.get('open_image'), color='w', horizontalalignment= 'center', verticalalignment= 'center', fontsize=16)

		fig.subplots_adjust(0.0,0.05,1,1)

		canvas = FigureCanvasTkAgg(fig, master=self)

		viewport = canvas.get_tk_widget()
		viewport.config(bg = 'black', cursor='fleur')

		level_requests = Queue(1)

		def on_update_canvas(data):
			nonlocal data_range, implot
			
			self.norm = Normalize()
			slicing_rate = int(data.shape[0] / self.winfo_width()) + 1

			if not implot:
				axis.clear()
				implot = axis.imshow(data, norm = self.norm, cmap='gray')
			else:
				implot.set_array(data[::slicing_rate,::slicing_rate])
			data_range = data.min(), data.max()
			canvas.draw_idle()
		
		# Threaded function
		def mpl_render_call():
			while True:
				try:
					level_data = level_requests.get()
					minv = data_range[1] * level_data[0] + data_range[0]
					maxv = data_range[1] * level_data[1] + data_range[0]
					implot.norm.vmin = minv
					implot.norm.vmax = maxv
					canvas.draw_idle()
				except:
					continue
		def enqueue_level_change(lower, upper):
			try:
				level_requests.put((lower, upper))
			except:
				pass # The queue is full

		levels = LevelsSlider(self, enqueue_level_change, height = 64)
		#  canvas.mpl_connect()
		viewport.grid(row= 1, column=0, rowspan=2, columnspan=2, sticky='news', padx=4, pady=4)
		levels.grid(row=3, column=0, columnspan=2, sticky='news')	
		
		# TODO: #20 Move to a dedicated class
		render_thread = Thread(target= mpl_render_call, daemon= True, name= 'MPL Render Thread')
		render_thread.start()

		self.__upd_canvas = on_update_canvas
	
	def build(self, master):
		pass
	def close(self, master):
		pass
	def update_canvas(self, file : File):
		if file.simple:
			file.load_data()
		self.__upd_canvas(file.data)

#-------------------------------------------
