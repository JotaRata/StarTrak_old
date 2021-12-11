
from pickle import FRAME
import tkinter as tk
# from os import basename, dirname
from abc import ABC, abstractmethod
from tkinter import Grid, Toplevel, ttk
from tkinter import filedialog

from PIL import ImageTk
from astropy.io.fits import column

#from STCore import Settings, Tools
from STCore.bin.data_management import SessionManager
from STCore.classes.drawables import Button, FileListElement, HButton
from STCore.classes.items import  File
from STCore.Icons import get_icon
from STCore import styles

def_keywords = ["DATE-OBS", "EXPTIME", "OBJECT", "INSTRUME"]
#-------------------------

# Base abstract class for instancing windows
class STView(ABC):
	# @property
	# @abstractmethod
	# def active (cls):
	# 	raise NotImplementedError()
	# build no debe llamarse desde dentro de la clase
	@abstractmethod
	def build(self, master):
		raise NotImplementedError()

	@abstractmethod
	def close(self):
		raise NotImplementedError()
	
	@abstractmethod
	def config_callback(self, **args):
		raise NotImplementedError()

#---------------------------

# Class for managing the selector window UI
class SelectorUI(STView, tk.Frame):
	def __init__(self, master, *args, **kwargs):
		tk.Frame.__init__(self, master, *args, **kwargs)
		#session_manager.CurrentWindow = 1
		self.columnconfigure((0, 1), weight=1)
		self.columnconfigure(( 4), weight=1)
		self.rowconfigure((1, 2), weight=1)		

		self.create_canvas()
		self.create_header(def_keywords)
		self.create_sidebar(master)
		#self.update_header(session_manager.file_items[0])
	
		self.header.grid(row= 0, column= 0, columnspan=2, sticky="ew")
		self.scroll_view.grid(row=1, column=0, rowspan=3, columnspan=2, sticky="news")
		self.sidebar.grid(row=0, column=4, rowspan=3, sticky="news")
		
	def build(self, master):
		self.pack(master, expand=1)

		self.clear_button.config(command= lambda: self.callbacks["clear"](master))
		self.add_button.config( command = lambda: self.callbacks["add"](master))
		self.apply_button.config(command = lambda: self.callbacks["apply"](master))


	def close(self):
		self.destroy()
	def config_callback(self, **args):
		# Callbacks: clear, add, apply
		self.callbacks = args
		
	def create_canvas(self):
		self.scroll_view = tk.Canvas(self, bg= "gray15", bd=0, relief="flat", highlightthickness=0)
		self.scrollbar = ttk.Scrollbar(self, command=self.scroll_view.yview)
		self.scroll_view.config(yscrollcommand=self.scrollbar.set)  

		self.list_frame = ttk.Frame(self.scroll_view)
		self.list_frame.columnconfigure(0, weight=1)
		self.scroll_view.create_window(0, 0, anchor = tk.NW, window = self.list_frame)
		self.scrollbar.grid(row=1, column=3, rowspan=3, sticky="ns")

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

#---------------------------

class MainScreenUI (STView, tk.Frame):
	def __init__(self, master, *args, **kwargs):
		tk.Frame.__init__(self, master, *args, **kwargs)
		# TODO Move to another script
		#recent_manager.CurrentWindow = 0
		#Tracker.DataChanged = False
		self.set_window_name(master)
		self.create_sidebar()
		self.create_top()
		self.config(width = 1100, height = 400, **styles.FRAME)

		self.sidebar.pack(side = tk.LEFT, anchor = tk.NW, fill = tk.Y, expand = 0)
		self.sidebar.pack_propagate(0)

		self.bottombar.pack(expand=1, side=tk.TOP, anchor=tk.NW, fill = tk.X)
		self.bottombar.pack_propagate(0)

	def build(self, master):
		self.pack(expand=1, fill = "both")
		self.session_button.config(cmd = self.callbacks["toplevel"])
		#self.load_button.config(command = Tools.OpenFileCommand)
		#self.create_recent(master)

	def close(self):
		self.sidebar.destroy()
		self.bottombar.destroy()
		self.destroy()
	def config_callback(self, **args):
		# Callbarck: toplevel, load_data
		self.callbacks = args

	def create_top(self):
		self.bottombar = tk.Frame(self, height=64, **styles.SFRAME)
		
		self.session_button = HButton(self.bottombar, None, text = "Nueva Sesion", width=196)
		self.session_button.pack(side= tk.RIGHT, anchor = tk.E)

		self.load_button = Button(self.bottombar, None, text = "Cargar Sesion", width=196)
		self.load_button.pack(side= tk.RIGHT, anchor = tk.E, after=self.session_button)

	def create_sidebar(self):
		self.sidebar = tk.Frame(self, width=300, bg = styles.hover_dark)
		logo = tk.PhotoImage(file ="STCore/StarTrak.png")
		logo_label = tk.Label(self.sidebar,image= logo, bg = styles.hover_dark)
		logo_label.photo = logo
		logo_label.pack(pady=16)

		tk.Label(self.sidebar, text = "Bienvenido a StarTrak",font="-weight bold", **styles.SLABEL, background = styles.hover_primary).pack(pady=16)

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
		if False:
		#if len(session_manager.current_path) > 0:
			master.wm_title(string = "StarTrak 1.2.0 - "+ basename(session_manager.current_path))
		else:
			master.wm_title(string = "StarTrak 1.2.0")
	
class SessionDialog(STView, tk.Toplevel):
	def __init__(self, master, *args, **kwargs) :
		center = (master.winfo_width()/2 + master.winfo_x() - 360 + 100,  master.winfo_height()/2 + master.winfo_y() - 240 + 60)
		Toplevel.__init__(self, master, *args, **kwargs)
		
		self.config(bg = styles.press_primary, bd=4)
		self.session = SessionManager()
		self.geometry("720x480+%d+%d" % center)
		try:
			self.wm_attributes('-type', 'splash')
		except:
			self.overrideredirect(True)
			
		self.rowconfigure((6), weight=1)
		self.columnconfigure(( 1), weight=1)
		self.wm_title(string = "Nueva Sesion")
		self.name_var = tk.StringVar(self, value="Nueva Sesion")

		tk.Label(self, text="Crear nueva sesion", font="-weight bold", bg = styles.press_primary, fg="white").grid(row= 0, columnspan=2 , sticky="ew")
		tk.Label(self, text="Nombre de la sesion:",  bg = styles.press_primary, fg="gray60", font = (None, 12)).grid(row= 1, column= 0, sticky="ew", pady=12)

		self.load_frame = tk.Frame(self, bg= styles.press_primary, height=128)
		self.info_label = None
		
		entry = tk.Entry(self, textvariable= self.name_var, font=(None, 16), bg = styles.press_primary, fg ="gray80")
		entry.grid(row= 1, column= 1, sticky="ew", padx=8)

		rtsession = tk.Frame(self ,height=8, **styles.SFRAME)
		assession = tk.Frame(self ,height=8, **styles.SFRAME)

		rtsession.grid(row= 3, columnspan=2,  sticky="news", pady=4)
		assession.grid(row= 4, columnspan=2,  sticky="news", pady=4)

		rt_cmd = lambda e: self.set_mode(0, rtsession, assession)
		as_cmd = lambda e: self.set_mode(1, rtsession, assession)

		rtsession.bind('<Button-1>', rt_cmd)
		assession.bind('<Button-1>', as_cmd)

		rt_title = tk.Label(rtsession,text="Analisis en tiempo real", justify="center",font="-weight bold", **styles.HLABEL)
		as_title = tk.Label(assession,text="Analisis asincrono", justify="center", font="-weight bold", **styles.HLABEL)
		
		rt_title.pack(fill="x")
		as_title.pack(fill="x")
		
		rt_label = tk.Label(rtsession, text="Comienza un analisis fotometrico en tiempo real con el telescopio\nDebes seleccionar un archivo de muestra que se encuentre en la misma carpeta donde se exportaran los archivos FITS desde el CCD", **styles.LABEL)
		as_label = tk.Label(assession, text="Selecciona varias imagenes tomadas anteriormente para comenzar un analisis fotometrico de estas\nTambien puedes apilar estas imagenes", **styles.LABEL)

		as_label.pack(fill="x")
		rt_label.pack(fill="x")
		
		rt_title.bind('<Button-1>', rt_cmd)
		as_title.bind('<Button-1>', as_cmd)

		rt_label.bind('<Button-1>', rt_cmd)
		as_label.bind('<Button-1>', as_cmd)
		self.set_mode(-1, rtsession, assession)
		
		self.load_frame.grid(row=5, columnspan=2, sticky="news")

		button_frame = tk.Frame(self, **styles.SFRAME)
		button_frame.grid(row=7, columnspan=2, sticky="ew")

		HButton(button_frame, text = "Continuar", cmd=self.apply, width=40).pack(side=tk.RIGHT, pady=16, padx=8)
		Button(button_frame, text = "Cancelar", cmd=self.close, width=32).pack(side=tk.RIGHT, pady=16, padx=8)

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
			tk.Label(self.load_frame, text="Abrir la primera imagen de la sesion", **styles.LABEL).pack()
			Button(self.load_frame, text="Arbir archivo", cmd=self.get_directory, width=28).pack()
		
		if mode == 1:
			for c in self.load_frame.winfo_children():
				c.destroy()
			
			tk.Label(self.load_frame, text="Abrir varias imagenes", **styles.LABEL).pack()
			Button(self.load_frame, text="Arbir archivos", cmd=self.get_filepaths, width=28).pack()

		self.info_label = tk.Label(self.load_frame, text = "", **styles.LABEL)
		self.info_label.pack()

		rtbutton.config(bg = styles.base_highlight if mode == 0 else styles.base_primary)
		for c in rtbutton.winfo_children():
			c.config(bg = styles.base_highlight if mode == 0 else styles.base_primary, fg = "white" if mode == 0 else "gray70")

		asbutton.config(bg = styles.base_highlight if mode == 1 else styles.base_primary)
		for c in asbutton.winfo_children():
			c.config(bg = styles.base_highlight if mode == 1 else styles.base_primary, fg = "white" if mode == 1 else "gray70")
	def build(self):
		pass
	def config_callback(self, **args):
		pass
	def close(self):
		self.destroy()	
	
	def apply(self):
		self.session.session_name = str(self.name_var.get())
		if self.session.runtime == 0:
			self.close()
			#RuntimeAnalysis.startFile = directory_path
			#RuntimeAnalysis.Awake(root)
		if self.session.runtime == 1:
			self.close()
			#Destroy()
			#ImageSelector.Awake(root, file_paths)

	