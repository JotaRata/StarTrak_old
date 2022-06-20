# coding=utf-8

import tkinter as tk
from os.path import basename, getmtime
from time import gmtime, strptime
from tkinter import filedialog, messagebox, ttk

from astropy.io import fits

import debug
import ImageView
import Tracker

from bin.enviroment import session_manager, current_view

def LoadFiles(paths, root):
	global loadIndex
	listSize = len(session_manager.file_items)
	Progress = tk.DoubleVar()
	LoadWindow = CreateLoadBar(root, Progress)
	LoadWindow[0].update()
	#Progress.trace("w",lambda a,b,c:LoadWindow[0].update())
	sortedP = sorted(paths, key=lambda f: Sort(f))
	n = 0

	for path in sortedP:
		item = GetFileItem(path)
		session_manager.file_items.append(item)
		CreateElements(loadIndex + listSize, item, def_keywords)
		loadIndex += 1	
	
	loadIndex = 0
	
	LoadWindow[0].destroy()
	ScrollView.config(scrollregion=(0,0, root.winfo_width(), 150 * len(session_manager.file_items)))

def Sort(path):
	if any(char.isdigit() for char in path):
		return int("".join(filter(str.isdigit, str(path))))
	else:
		return str(path)

def GetFileItem(path):
	try:
		data = fits.getdata(path, header = True)
		date = None
		try:
			date = strptime(data[1]["DATE-OBS"], "%Y-%m-%dT%H:%M:%S.%f")
		except:
			debug.warn(__name__, "El archivo \"{0}\" no tiene la clave DATE-OBS, se usara la fecha del sistema".format(path))
			date = gmtime(getmtime(path))

		item = File(path, data[0], data[1], date)
		item.name = basename(path)

		debug.log(__name__, "Cargado \"{0}\"".format(item.name))
		return item
	except:
		debug.error(__name__, "No se pudo cargar el archivo \"{0}\"".format(path), stop=False)
		return

def CreateLoadBar(root, progress, title = "Cargando.."):
	popup = tk.Toplevel()
	popup.geometry("300x60+%d+%d" % (root.winfo_width()/2,  root.winfo_height()/2) )
	popup.wm_title(string = title)
	popup.attributes('-topmost', 'true')
	popup.overrideredirect(1)
	pframe = tk.LabelFrame(popup)
	pframe.pack(fill = tk.BOTH, expand = 1)
	label = tk.Label(pframe, text="Cargando archivo..")
	bar = ttk.Progressbar(pframe, variable=progress, maximum=100)
	label.pack()
	bar.pack(fill = tk.X)
	return popup, label, bar

def SetActive(item, intvar, operation):
	item.active = intvar.get()
	if operation == "w":
		Tracker.DataChanged = True
def SetFilteredList():
	global FilteredList
	FilteredList = list(filter(lambda item: item.active == 1, session_manager.file_items))

def Apply(root):
	SetFilteredList()
	if len(FilteredList) == 0:
		messagebox.showerror("Error", "Debe seleccionar al menos un archivo")
		return
	Destroy()
	# Crea otra lista identica pero solo conteniendo los valores path y active  para liberar espacio al guardar #
	LightList = []
	file : File
	for file in session_manager.file_items:
		item = File(file.path, None, file.header, file.date)
		item.active = file.active
		item.version = file.version
		item.name = file.name
		LightList.append(item)
	session_manager.file_items = FilteredList
	session_manager.FileRefList = LightList
	ImageView.Awake(root)

def ClearList(root):
	global ListElements
	for i in session_manager.file_items:
		del i
	session_manager.file_items = []
	session_manager.FileRefList = []
	try:
		ScrollView.config(scrollregion=(0,0, root.winfo_width(), 1))
		for child in ListFrame.winfo_children():
			child.destroy()
	except:
		pass
	ListElements = []

def AddFiles(root):
	paths = filedialog.askopenfilenames(parent = root, filetypes=[("FIT Image", "*.fits;*.fit"), ("Todos los archivos",  "*.*")])
	Tracker.DataChanged = True
	LoadFiles(paths, root)

def Destroy():
	SetFilteredList()
