# coding=utf-8

import tkinter as tk
from os.path import basename, getmtime
from time import gmtime, sleep, strptime
from tkinter import filedialog, messagebox, ttk

from astropy.io import fits

import DataManager
import Debug
import ImageView
import Tracker
from Icons import GetIcon
from Items import File, CURRENT_VERSION
from STCore.Component import FileListElement

#region Variables
App : tk.Frame = None

Sidebar :tk.Frame = None
ListFrame : tk.Frame = None
Header : tk.Frame = None
ScrollView = None
loadIndex = 0
FilteredList = []
ListElements = []
def_keywords = ["DATE-OBS", "EXPTIME", "OBJECT", "INSTRUME"]
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

	for path in sortedP:
		item = GetFileItem(path)
		DataManager.FileItemList.append(item)
		CreateElements(loadIndex + listSize, item, def_keywords)
		loadIndex += 1	
	
	loadIndex = 0
	
	LoadWindow[0].destroy()
	ScrollView.config(scrollregion=(0,0, root.winfo_width(), 150 * len(DataManager.FileItemList)))

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
			Debug.Warn(__name__, "El archivo \"{0}\" no tiene la clave DATE-OBS, se usara la fecha del sistema".format(path))
			date = gmtime(getmtime(path))

		item = File(path, data[0], data[1], date)
		item.name = basename(path)

		Debug.Log(__name__, "Cargado \"{0}\"".format(item.name))
		return item
	except:
		Debug.Error(__name__, "No se pudo cargar el archivo \"{0}\"".format(path), stop=False)
		return

def Awake(root, paths = []):
	global App, ListFrame, ScrollView, def_keywords
	DataManager.CurrentWindow = 1
	App = ttk.Frame(root)
	App.pack(fill = tk.BOTH, expand = 1)

	App.columnconfigure((0, 1), weight=1)
	App.columnconfigure(( 4), weight=1)
	App.rowconfigure((1, 2), weight=1)
	
	#ttk.Label(App, text = "Seleccionar Imagenes").grid(row=0, column=0, columnspan=3)
	
	CreateCanvas()
	CreateHeader(def_keywords)
	CreateSidebar(root)
	BuildLayout()

	# Saved File
	if len(DataManager.FileItemList) != 0 and len(paths) == 0:
		ind = 0
		Progress = tk.DoubleVar()
		LoadWindow = CreateLoadBar(root, Progress, title = "Cargando "+basename(DataManager.CurrentFilePath))
		
		index = 0
		item:File
		for item in DataManager.FileItemList:
			# File item is too old, has to be re-made
			if not hasattr(item, "version"):
				item.data = None
				continue
			elif item.version != CURRENT_VERSION:
				 _, item.header = fits.getdata(item.path, header = True)
		for item in DataManager.FileItemList:
			if item.data is None:
				if item.Exists():
					item = GetFileItem(item.path)
					Progress.set(100*float(ind)/len(DataManager.FileItemList))
					LoadWindow[0].update()
				else:
					messagebox.showerror("Error de carga.", "Uno o más archivos no existen\n"+ item.path)
					break	
			ScrollView.config(scrollregion=(0,0, root.winfo_width(), 150 * len(DataManager.FileItemList)))

			CreateElements(index, item, def_keywords)
			DataManager.FileItemList[index] = item
			index += 1
		LoadWindow[0].destroy()
	else:
		LoadFiles(paths, root)

	UpdateHeaders(DataManager.FileItemList[0])
def BuildLayout():
	global App, ScrollView, Sidebar, Header

	Header.grid(row= 0, column= 0, columnspan=3, sticky="ew")
	ScrollView.grid(row=1, column=0, rowspan=3, columnspan=3, sticky="news")
	Sidebar.grid(row=0, column=4, rowspan=3, sticky="news")

def CreateCanvas():
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

	CleanButton = ttk.Button(Sidebar, text="Limpiar todo", command = lambda: ClearList(root), state = tk.DISABLED,  image = GetIcon("delete"), compound = "right")	
	AddButton = ttk.Button(Sidebar, text=  "Agregar archivo", command = lambda: AddFiles(root), state = tk.DISABLED, image = GetIcon("multi"), compound = "right")
	ApplyButton = ttk.Button(Sidebar, text="Continuar", command = lambda: Apply(root), state = tk.DISABLED, image = GetIcon("next"), compound = "right")
	
	CleanButton.grid(row=2, column=0, sticky = "ew", pady=5)
	AddButton.grid(row=1, column=0, sticky = "ew", pady=5)
	ApplyButton.grid(row=0, column=0, sticky = "ew", pady=5)

	CleanButton.config(state = tk.NORMAL)
	ApplyButton.config(state = tk.NORMAL)
	AddButton.config(state = tk.NORMAL)

def CreateHeader(keywords):
	global App, Header, HeaderButtons
	Header = tk.Frame(App,bg = "gray40", height=24)
	HeaderButtons = []
	#Header.columnconfigure((tuple(range(10))), weight=1)
	dargs = {"font":(None, 11), "bg":"gray30", "fg":"white", "bd":1, "relief":tk.RIDGE}
	args = {"row":0, "sticky":"news", "ipadx":2}

	tk.Label(Header, text= "Vista previa", width=16, **dargs).grid(column=0, **args)
	tk.Label(Header, text= "Nombre", width = 20, **dargs).grid(column=1, **args)
	tk.Label(Header, text= "Dimensiones", width=12, **dargs).grid(column=2, **args)
	tk.Label(Header, text= "Tamaño", width=12, **dargs).grid(column= 4 + len(keywords), **args)

	index = 0
	for key in keywords:
		button = tk.Button(Header, text=key+" ▼", width=12 if index != 0 else 20, cursor="hand2", highlightcolor="gray50", **dargs)
		button.grid(column= 3 + index, **args)
		index += 1
		HeaderButtons.append((button, key))

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

def CreateElements(index, item, keywords):
	global ListElements
	
	element = FileListElement(ListFrame, item)
	element.SetLabels(keywords)
	element.grid(row=index, sticky="ew", pady=4)
	ListElements.append(element)

def UpdateElements(keywords):
	global ListElements
	
	for element in ListElements:
		element.SetLabels(keywords)

def UpdateHeaders(sample_item : File):
	global HeaderButtons
	
	i = 0
	keys = def_keywords
	def SetKey(bindex, key):
		nonlocal keys
		button = HeaderButtons[bindex][0]
		button.config(text= key + " ▼", state="normal")
		HeaderButtons[bindex] = button, key
		keys[bindex] = key

		UpdateElements(keys)

	def OpenEnum(index, event):
		nonlocal sample_item
		menu = tk.Menu(Header)
		for key in sample_item.header:
			menu.add_command(label=key, command=lambda b=index, k=key : SetKey(b, k))
		menu.post(event.x_root, event.y_root)

	for button, key in HeaderButtons:
		
		button.bind("<Button-1>", lambda event, index = i: OpenEnum(index, event))
		
		i += 1

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
	file : File
	for file in DataManager.FileItemList:
		item = File(file.path, None, file.header, file.date)
		item.active = file.active
		item.version = file.version
		item.name = file.name
		LightList.append(item)
	DataManager.FileItemList = FilteredList
	DataManager.FileRefList = LightList
	ImageView.Awake(root)

def ClearList(root):
	global ListElements
	for i in DataManager.FileItemList:
		del i
	DataManager.FileItemList = []
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
	App.destroy()
