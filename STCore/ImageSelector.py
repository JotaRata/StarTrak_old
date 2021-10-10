# coding=utf-8

import tkinter as tk
from PIL import Image, ImageTk
from astropy.io import fits
#import pyfits as fits
from os.path import basename, getmtime, isfile
from time import sleep, strftime, localtime, strptime,gmtime
from tkinter import Grid, Widget, filedialog, messagebox, ttk
from STCore.Component import FileListElement
from STCore.item.File import _FILE_VERSION
from item.File import FileItem

from STCore import ImageView, DataManager, Tracker
import numpy
from functools import partial
import STCore.utils.Icons as icons

#region Variables
App = None
ListFrame = None
ScrollView = None
loadIndex = 0
FilteredList = []
#endregion

def LoadFiles(paths, root):
	global loadIndex
	listSize = len(DataManager.FileItemList)
	Progress = tk.DoubleVar()
	LoadWindow = CreateLoadBar(root, Progress)
	LoadWindow[0].update()
	#Progress.trace("w",lambda a,b,c:LoadWindow[0].update())
	sortedP = sorted(paths, key=lambda f: Sort(f))
	n = 0
	print ("-"*60)
	[SetFileItems(x, ListSize = listSize, PathSize = len(paths),loadWindow = LoadWindow, progress = Progress, root = root) for x in sortedP]
	#map(partial(SetFileItems, ListSize = listSize, PathSize = len(paths),loadWindow = LoadWindow, progress = Progress, root = root), sortedP)
	loadIndex = 0
	
	LoadWindow[0].destroy()
	ScrollView.config(scrollregion=(0,0, root.winfo_width(), len(DataManager.FileItemList)*240/4))

def Sort(path):
	if any(char.isdigit() for char in path):
		return int("".join(filter(str.isdigit, str(path))))
	else:
		return str(path)

def SetFileItems(path, ListSize, PathSize, progress, loadWindow,  root):
	global loadIndex

	print (path)
	item = FileItem()
	item.path = str(path)
	item.data, item.header = fits.getdata(item.path, header = True)

	#item.date = fits.header['NOTE'].split()[3]
	# Request DATE-OBS keyword to extract date information (previously used NOTE keyword which was not always available)
	try:
		item.date = strptime(item.header["DATE-OBS"], "%Y-%m-%dT%H:%M:%S.%f")
	except:
		print ("File has no DATE-OBS keyword in Header   -   using system time instead..")
		item.date = gmtime(getmtime(item.path))
		pass
	#print strftime('%H/%M/%S', localtime(item.date))
	#item.timee = header['NOTE'].split()[3]

	item.active = 1
	DataManager.FileItemList.append(item)
	CreateFileGrid(loadIndex + ListSize, item, root)

	progress.set(100*float(loadIndex)/PathSize)
	loadWindow[1].config(text="Cargando archivo "+str(loadIndex)+" de "+str(PathSize))
	loadWindow[0].update()
	#loadWindow[2]["value"] = (100 * float(loadIndex)/PathSize)
	sleep(0.01)
	loadIndex += 1
	#lock.relase()

def Awake(root, paths = []):
	global App, ListFrame, ScrollView
	DataManager.CurrentWindow = 1
	App = ttk.Frame(root)
	App.pack(fill = tk.BOTH, expand = 1)

	#App.columnconfigure((0, 1), weight=2)
	App.columnconfigure((0, 1, 2, 4), weight=1)
	App.rowconfigure((1, 2), weight=1)
	
	ttk.Label(App, text = "Seleccionar Imagenes").grid(row=0, column=0, columnspan=3)
	
	CreateCanvas(root, paths)

	CreateSidebar(root)
	BuildLayout()

	# Saved File
	if len(DataManager.FileItemList) != 0 and len(paths) == 0:
		ind = 0
		Progress = tk.DoubleVar()
		LoadWindow = CreateLoadBar(root, Progress, title = "Cargando "+basename(DataManager.CurrentFilePath))
		
		index = 0
		for item in DataManager.FileItemList:
			# File item is too old, has to be re-made
			if not hasattr(item, "version"):
				item.data = None
				continue
			elif item.version != _FILE_VERSION:
				 _, item.header = fits.getdata(item.path, header = True)
				 
		for item in DataManager.FileItemList:
			if item.data is None:
				if item.Exists():
					item.data, item.header = fits.getdata(item.path, header = True)
					try:
						item.date = strptime(item.header["DATE-OBS"].split()[1]+"-"+item.header["DATE-OBS"].split()[3], "%Y-%m-%dT%H:%M:%S.%f")
					except:
						print ("File has no Header!   -   using system time instead..")
						item.date = gmtime(getmtime(item.path))
						pass
					Progress.set(100*float(ind)/len(DataManager.FileItemList))
					LoadWindow[0].update()
				else:
					messagebox.showerror("Error de carga.", "Uno o más archivos no existen\n"+ item.path)
					break	
			ScrollView.config(scrollregion=(0,0, root.winfo_width(), len(DataManager.FileItemList)*240/4))

			CreateFileGrid(index, item, root)
			DataManager.FileItemList[index] = item
			index += 1
		LoadWindow[0].destroy()
	else:
		LoadFiles(paths, root)

def BuildLayout():
	global App, ScrollView, Sidebar

	ScrollView.grid(row=1, column=0, rowspan=3, columnspan=3, sticky="news")
	Sidebar.grid(row=0, column=4, rowspan=3, sticky="news")

def CreateCanvas(root, paths):
	global App, ScrollView, ListFrame

	ScrollView = tk.Canvas(App, bg= "gray15", bd=0, relief="flat", highlightthickness=0)
	ScrollBar = ttk.Scrollbar(App, command=ScrollView.yview)
	ScrollView.config(yscrollcommand=ScrollBar.set)  

	ListFrame = ttk.Frame(ScrollView)
	ListFrame.columnconfigure(0, weight=1)
	ScrollView.create_window(0, 0, anchor = tk.NW, window = ListFrame)
	
	ScrollBar.grid(row=1, column=3, rowspan=3, sticky="ns")

def CreateSidebar(root):
	global App, Sidebar
	Sidebar = ttk.Frame(App, width = 200)
	Sidebar.columnconfigure(0, weight=1)

	CleanButton = ttk.Button(Sidebar, text="Limpiar todo", command = lambda: ClearList(root), state = tk.DISABLED,  image = icons.Icons["delete"], compound = "right")	
	AddButton = ttk.Button(Sidebar, text=  "Agregar archivo", command = lambda: AddFiles(root), state = tk.DISABLED, image = icons.Icons["multi"], compound = "right")
	ApplyButton = ttk.Button(Sidebar, text="Continuar", command = lambda: Apply(root), state = tk.DISABLED, image = icons.Icons["next"], compound = "right")
	
	CleanButton.grid(row=2, column=0, sticky = "ew", pady=5)
	AddButton.grid(row=1, column=0, sticky = "ew", pady=5)
	ApplyButton.grid(row=0, column=0, sticky = "ew", pady=5)

	CleanButton.config(state = tk.NORMAL)
	ApplyButton.config(state = tk.NORMAL)
	AddButton.config(state = tk.NORMAL)


def GridPlace(root, index, size):
	maxrows = root.winfo_height()/size
	maxcols = (root.winfo_width()-180) / size - 1
	col = index
	row = 0
	while col >= maxcols:
		col -= maxcols
		row += 1
	return int(row), int(col)

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

def CreateFileGrid(index, item, root):
	element = FileListElement(ListFrame, item)
	element.SetLabels(["DATE-OBS", "EXPTIME", "TELESCOP", "INSTRUME"])
	element.grid(row=index, sticky="ew")

def SetActive(item, intvar, operation):
	item.active = intvar.get()
	if operation == "w":
		Tracker.DataChanged = True
def SetFilteredList():
	global FilteredList
	FilteredList = list(filter(lambda item: item.active == 1, DataManager.FileItemList))

def Apply(root):
	SetFilteredList()
	if len(FilteredList) == 0:
		messagebox.showerror("Error", "Debe seleccionar al menos un archivo")
		return
	Destroy()
	# Crea otra lista identica pero solo conteniendo los valores path y active  para liberar espacio al guardar #
	LightList = []
	for i in DataManager.FileItemList:
		item = FileItem()
		item.path = i.path
		item.active = i.active
		LightList.append(item)
	DataManager.FileItemList = FilteredList
	ImageView.Awake(root)

def ClearList(root):
	
	for i in DataManager.FileItemList:
		del i
	DataManager.FileItemList = []
	try:
		ScrollView.config(scrollregion=(0,0, root.winfo_width(), 1))
		for child in ListFrame.winfo_children():
			child.destroy()
	except:
		pass

def AddFiles(root):
	paths = filedialog.askopenfilenames(parent = root, filetypes=[("FIT Image", "*.fits;*.fit"), ("Todos los archivos",  "*.*")])
	#print (paths)
	Tracker.DataChanged = True
	LoadFiles(paths, root)

def Destroy():
	SetFilteredList()
	App.destroy()
