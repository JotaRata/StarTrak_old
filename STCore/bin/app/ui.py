
import tkinter as tk
from os import basename
from abc import ABC, abstractmethod
from tkinter import ttk

from PIL import ImageTk

from STCore import Settings, Tools
from STCore.bin.enviroment import session_manager, recent_manager
from STCore.classes.drawables import FileListElement
from STCore.classes.items import  File
from STCore.icons import get_icon

def_keywords = ["DATE-OBS", "EXPTIME", "OBJECT", "INSTRUME"]
#-------------------------

# Base abstract class for instancing windows
class STView(ABC):
	# build no debe llamarse desde dentro de la clase
	@abstractmethod
	def build(self, master):
		raise NotImplementedError()

	@abstractmethod
	def destroy(self):
		raise NotImplementedError()
	
	@abstractmethod
	def config_callback(self, **args):
		raise NotImplementedError()

#---------------------------

# Class for managing the selector window UI
class SelectorUI(STView, tk.Frame):
	def __init__(self, master):
		session_manager.CurrentWindow = 1

		self.columnconfigure((0, 1), weight=1)
		self.columnconfigure(( 4), weight=1)
		self.rowconfigure((1, 2), weight=1)		

		self.create_canvas()
		self.create_header(def_keywords)
		self.create_sidebar(master)
		self.update_header(session_manager.file_items[0])
	
		self.Header.grid(row= 0, column= 0, columnspan=3, sticky="ew")
		self.scroll_view.grid(row=1, column=0, rowspan=3, columnspan=3, sticky="news")
		self.sidebar.grid(row=0, column=4, rowspan=3, sticky="news")
		
	def build(self, master):
		self.pack(master, expand=1)

		self.clear_button.config(command= lambda: self.callbacks["clear"](master))
		self.add_button.config( command = lambda: self.callbacks["add"](master))
		self.apply_button.config(command = lambda: self.callbacks["apply"](master))


	def destroy(self):
		self.destroy()
	def config_callback(self, **args):
		self.callbacks = args
		
	def create_canvas(self):
		self.scroll_view = tk.Canvas(self, bg= "gray15", bd=0, relief="flat", highlightthickness=0)
		self.scrollbar = ttk.Scrollbar(self, command=self.scrollView.yview)
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
	def __init__(self, master):
		# TODO Move to another script
		#recent_manager.CurrentWindow = 0
		#Tracker.DataChanged = False
		self.set_window_name(master)
		self.create_sidebar()
		self.create_bottom(master)

		self.sidebar.pack(side = tk.LEFT, anchor = tk.NW, fill = tk.Y, expand = 0)
		self.sidebar.pack_propagate(0)
		self.bottombar.pack(expand=1, side=tk.BOTTOM, anchor=tk.SW, fill = tk.X)
		self.bottombar.pack_propagate(0)

	def build(self, master):
		self.pack(master, expand=1)
		self.session_button.config(command = lambda: self.callbacks["toplevel"](master))
		self.load_button.config(command = Tools.OpenFileCommand)
		self.create_recent(master)

	def destroy(self):
		self.sidebar.destroy()
		self.bottombar.destroy()
		self.destroy()
	def config_callback(self, **args):
		self.callbacks = args

	def create_bottom(self, master):
		self.bottombar = tk.Frame(self, bg ="gray18", height=64)
		self.session_button = ttk.Button(self.bottombar, text = "Nueva Sesion",image = get_icon("run"), compound = "left",  width=32, style="Highlight.TButton")
		self.session_button.pack(side= tk.RIGHT, anchor = tk.E)

		self.load_button = ttk.Button(self.bottombar, text = "Cargar Sesion",image = get_icon("open"), compound = "left", width=32)
		self.load_button.pack(side= tk.RIGHT, anchor = tk.E, after=self.session_button)


	def create_sidebar(self):
		self.sidebar = tk.Frame(self, bg="gray15", width=400)
		logo = ImageTk.PhotoImage(file ="STCore/StarTrak.png")
		logo_label = tk.Label(self.sidebar,image= logo, bg = "gray15")
		logo_label.pack(pady=16)
		tk.Label(self.sidebar, text = "Bienvenido a StarTrak",font="-weight bold", bg = "gray15", fg = "gray80").pack(pady=16)

	def create_recent(self, master):
		if Settings._RECENT_FILES_.get() == 1:
			self.recent_label = tk.LabelFrame(self, text = "Archivos recientes:", bg="gray18", fg="gray90", relief="flat", font="-weight bold")
			self.recent_label.pack(anchor = tk.NW, pady=16, expand=1, fill=tk.BOTH)

			ttk.Label(self.recent_label).pack()
			for p in reversed(recent_manager.recent_files):
				recent_elem = ttk.Button(self.recent_label, text = p[0], cursor="hand2", style= "Highlight.TButton")
				recent_elem.config(command= lambda : self.callbacks["load_data"](p[1], master))
				recent_elem.pack(anchor = tk.W, pady=4, fill=tk.X)
				ttk.Button(recent_elem, image=get_icon("delete"), command=lambda:self.remove_recent(p, master), style="Highlight.TButton").pack(side=tk.RIGHT)
	def remove_recent(self, path, master):
		recent_manager.recent_files.remove(path)
		recent_manager.save_recent()()
		self.recent_label.destroy()
		
		self.create_recent(master)


	def set_window_name(self, master):
		if len(session_manager.current_path) > 0:
			master.wm_title(string = "StarTrak 1.1.0 - "+ basename(session_manager.current_path))
		else:
			master.wm_title(string = "StarTrak 1.1.0")
	