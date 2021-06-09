# coding=utf-8

import Tkinter as tk
import ttk
from PIL import Image, ImageTk
from astropy.io import fits
#import pyfits as fits
from os.path import basename, getmtime, isfile
from time import sleep, strftime, localtime, strptime,gmtime
import tkFileDialog
import tkMessageBox
from STCore.item.File import FileItem
import STCore.ImageView
import STCore.DataManager
import numpy
from functools import partial
import STCore.utils.Icons as icons
#region Variables
SelectorFrame = None
ImagesFrame = None
ScrollView = None
ItemList = []
loadIndex = 0
FilteredList = []
#endregion

def LoadFiles(paths, root):
	global loadIndex
	listSize = len(ItemList)
	Progress = tk.DoubleVar()
	LoadWindow = CreateLoadBar(root, Progress)
	LoadWindow[0].update()
	#Progress.trace("w",lambda a,b,c:LoadWindow[0].update())
	sortedP = sorted(paths, key=lambda f: Sort(f))
	n = 0
	map(partial(SetFileItems, ListSize = listSize, PathSize = len(paths),loadWindow = LoadWindow, progress = Progress, root = root), sortedP)
	loadIndex = 0
	
	LoadWindow[0].destroy()
	ScrollView.config(scrollregion=(0,0, root.winfo_width()-180, len(ItemList)*240/4))

def Sort(path):
	if any(char.isdigit() for char in path):
		return int(filter(str.isdigit, str(path)))
	else:
		return str(path)

def SetFileItems(path, ListSize, PathSize, progress, loadWindow,  root):
	global loadIndex
	item = FileItem()
	item.path = str(path)
	item.data, hdr = fits.getdata(item.path, header = True)
	#item.date = fits.header['NOTE'].split()[3]
	# Request DATE-OBS keyword to extract date information (previously used NOTE keyword which was not always available)
	try:
		item.date = strptime(hdr["DATE-OBS"], "%Y-%m-%dT%H:%M:%S.%f")
	except:
		print ("File has no DATE-OBS keyword in Header   -   using system time instead..")
		item.date = gmtime(getmtime(item.path))
		pass
	#print strftime('%H/%M/%S', localtime(item.date))
	#item.timee = header['NOTE'].split()[3]
	item.active = 1
	ItemList.append(item)
	CreateFileGrid(loadIndex + ListSize, item, root)
	progress.set(100*float(loadIndex)/PathSize)
	loadWindow[1].config(text="Cargando archivo "+str(loadIndex)+" de "+str(PathSize))
	loadWindow[0].update()
	#loadWindow[2]["value"] = (100 * float(loadIndex)/PathSize)
	sleep(0.01)
	loadIndex += 1
	#lock.relase()

def Awake(root, paths = []):
	global SelectorFrame, ItemList, ImagesFrame, ScrollView
	STCore.DataManager.CurrentWindow = 1
	SelectorFrame = tk.Frame(root)
	SelectorFrame.pack(fill = tk.BOTH, expand = 1)
	tk.Label(SelectorFrame, text = "Seleccionar Imagenes").pack(fill = tk.X)
	ScrollView = tk.Canvas(SelectorFrame, scrollregion=(0,0, root.winfo_width()-80, len(paths)*220/4), width = root.winfo_width()-180)
	ScrollBar = ttk.Scrollbar(SelectorFrame, command=ScrollView.yview)
	ScrollView.config(yscrollcommand=ScrollBar.set)  
	ScrollView.pack(expand = 0, fill = tk.BOTH, anchor = tk.NW, side = tk.LEFT)
	ScrollBar.pack(side = tk.LEFT,fill=tk.Y) 
	ImagesFrame = tk.Frame()
	ScrollView.create_window(0,0, anchor = tk.NW, window = ImagesFrame, width = root.winfo_width() - 180)
	buttonFrame = tk.Frame(SelectorFrame, width = 80)
	buttonFrame.pack(side = tk.RIGHT, anchor = tk.NE, fill = tk.BOTH, expand = 1)
	for c in range(1):
		tk.Grid.columnconfigure(buttonFrame, c, weight=1)
	style = ttk.Style()
	style.configure("Left.TButton", anchor = tk.E)
	CleanButton = ttk.Button(buttonFrame, text="Limpiar todo     ", command = lambda: ClearList(root), state = tk.DISABLED,  image = icons.Icons["delete"], compound = "right",style = "Left.TButton")
	CleanButton.image = icons.Icons["delete"]
	CleanButton.grid(row=2, column=0, sticky = tk.EW, pady=5)
	AddButton = ttk.Button(buttonFrame, text=  "Agregar archivo  ", command = lambda: AddFiles(root), state = tk.DISABLED, image = icons.Icons["multi"], compound = "right",style = "Left.TButton")
	AddButton.grid(row=1, column=0, sticky = tk.EW, pady=5)
	ApplyButton = ttk.Button(buttonFrame, text="Continuar        ", command = lambda: Apply(root), state = tk.DISABLED, image = icons.Icons["next"], compound = "right",style = "Left.TButton")
	ApplyButton.grid(row=0, column=0, sticky = tk.EW, pady=5)
	if len(ItemList) != 0 and len(paths) == 0:
		ind = 0
		Progress = tk.DoubleVar()
		LoadWindow = CreateLoadBar(root, Progress, title = "Cargando "+basename(STCore.DataManager.CurrentFilePath))
		while ind < len(ItemList):
			if ItemList[ind].data is None:
				if ItemList[ind].Exists():
					ItemList[ind].data, hdr = fits.getdata(ItemList[ind].path, header = True)
					try:
						ItemList[ind].date = strptime(hdr["NOTE"].split()[1]+"-"+hdr["NOTE"].split()[3], "time:%m/%d/%Y-%H:%M:%S")
					except:
						print ("File has no Header!   -   using system time instead..")
						ItemList[ind].date = gmtime(getmtime(ItemList[ind].path))
						pass
					Progress.set(100*float(ind)/len(ItemList))
					LoadWindow[0].update()
				else:
					tkMessageBox.showerror("Error de carga.", "Uno o más archivos no existen\n"+ ItemList[ind].path)
					break	
			ScrollView.config(scrollregion=(0,0, root.winfo_width()-180, len(ItemList)*240/4))
			CreateFileGrid(ind, ItemList[ind], root)
			ind += 1
		LoadWindow[0].destroy()
	else:
		LoadFiles(paths, root)
	CleanButton.config(state = tk.NORMAL)
	ApplyButton.config(state = tk.NORMAL)
	AddButton.config(state = tk.NORMAL)

def GridPlace(root, index, size):
	maxrows = root.winfo_height()/size
	maxcols = (root.winfo_width()-180)/size
	col = index
	row = 0
	while col >= maxcols:
		col -= maxcols
		row += 1
	return row, col

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
	GridFrame = tk.LabelFrame(ImagesFrame, width = 200, height = 200)
	Row, Col = GridPlace(root, index, 250)
	GridFrame.grid(row = Row, column = Col, sticky = tk.NSEW, padx = 20, pady = 20)
	dat = item.data.astype(float)
	minv = numpy.min(dat)
	maxv = numpy.max(dat)
	thumb = numpy.clip(255*(dat - minv)/(maxv - minv), 0, 255).astype(numpy.uint8)
	Pic = Image.fromarray(thumb)
	Pic.thumbnail((200, 200))
	Img = ImageTk.PhotoImage(Pic)
	tk.Label(GridFrame, text=basename(item.path)).grid(row=0,column=0, sticky=tk.W)
	isactive =tk.IntVar(ImagesFrame, value=item.active)
	Ckeckbox = tk.Checkbutton(GridFrame, variable = isactive)
	Ckeckbox.grid(row=0,column=1, sticky=tk.E)
	isactive.trace("w", lambda a,b,c: SetActive(item, isactive, c))
	ImageLabel = tk.Label(GridFrame, image = Img, width = 200, height = 200 * item.data.shape[0]/float(item.data.shape[1]))
	ImageLabel.image = Img
	ImageLabel.grid(row=1,column=0, columnspan=2)

def SetActive(item, intvar, operation):
	item.active = intvar.get()
	if operation == "w":
		STCore.Tracker.DataChanged = True
def SetFilteredList():
	global FilteredList
	FilteredList = list(filter(lambda item: item.active == 1, ItemList))

def Apply(root):
	SetFilteredList()
	if len(FilteredList) == 0:
		tkMessageBox.showerror("Error", "Debe seleccionar al menos un archivo")
		return
	Destroy()
	# Crea otra lista identica pero solo conteniendo los valores path y active  para liberar espacio al guardar #
	LightList = []
	for i in ItemList:
		item = FileItem()
		item.path = i.path
		item.active = i.active
		LightList.append(item)
	STCore.DataManager.FileItemList = LightList
	STCore.ImageView.Awake(root, FilteredList)

def ClearList(root):
	global ItemList
	for i in ItemList:
		del i
	ItemList = []
	try:
		ScrollView.config(scrollregion=(0,0, root.winfo_width(), 1))
		for child in ImagesFrame.winfo_children():
			child.destroy()
	except:
		pass

def AddFiles(root):
	paths = tkFileDialog.askopenfilenames(parent = root, filetypes=[("FIT Image", "*.fits;*.fit"), ("Todos los archivos",  "*.*")])
	paths = root.tk.splitlist(paths)
	STCore.Tracker.DataChanged = True
	LoadFiles(paths, root)

def Destroy():
	SetFilteredList()
	SelectorFrame.destroy()
