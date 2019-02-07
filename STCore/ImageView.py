# coding=utf-8

from astropy.io import fits
from  numpy import min, max
from matplotlib import use, figure
use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle
import Tkinter as tk
import ttk
from STCore.item.Star import StarItem
from STCore import SetStar, Tracker
import STCore.DataManager
#region Messages and Events

def OnImageClick(event):
	loc = (int(event.ydata), int(event.xdata))
	SetStar.Awake(ViewerFrame, Data, Brightness, Stars, OnStarChange, location = loc)

def OnStarChange():
	UpdateStarList()
	UpdateCanvasOverlay()
	STCore.DataManager.StarItemList = Stars
#endregion

#region Update Funcions

def UpdateStarList():
	global SidebarList
	for child in SidebarList.winfo_children():
		child.destroy()
	index = 0
	for s in Stars:
		ListFrame = tk.Frame(SidebarList)
		ListFrame.pack(fill = tk.X, expand = 1, anchor = tk.N, pady = 5)

		cmd = __helperCreateWindow(index, stName = s.name, stLoc = s.location, stRadius = s.radius, stBound = s.bounds, stType = s.type, stThr = s.threshold)
		cmd2= __helperPop(Stars, index)
		ttk.Button(ListFrame, text = s.name, width = 10, command = cmd).pack(side = tk.LEFT, fill = tk.X, expand = 1)
		ttk.Button(ListFrame, text = "X", width = 1, command = cmd2).pack(side = tk.RIGHT)
		index += 1
#Las funciones lambda no se pueden llamar dentro de un loop for o while,
## para eso hay que crear una funcion que retorne un lambda
def __helperCreateWindow(index, stName, stLoc, stRadius, stBound, stType,stThr):
	return lambda: SetStar.Awake(ViewerFrame, Data, Brightness, Stars, OnStarChange, index, stName, stLoc, stRadius, stBound, stType, stThr)
def __helperPop (list, index):
	return lambda: (list.pop(index), OnStarChange())

def UpdateCanvasOverlay():
	# Si se elimina el primer elemento de un lista en un ciclo for, entonces
	# ya no podra seguir iterando, lo que producir errores, se utiliza reversed para eliminar
	# el ultimo elemento de la lista primero y asi.
	for a in reversed(ImageAxis.artists):
		a.remove()
	for t in reversed(ImageAxis.texts):
		t.remove()
	for s in Stars:
		rect_pos = (s.location[1] - s.radius, s.location[0] - s.radius)
		rect = Rectangle(rect_pos, s.radius *2, s.radius *2, edgecolor = "w", facecolor='none')
		bound_pos = (s.location[1] - s.bounds, s.location[0] - s.bounds)
		bound = Rectangle(bound_pos, s.bounds*2, s.bounds *2, edgecolor = "0.5", linestyle = 'dashed', facecolor='none')
		ImageAxis.add_artist(rect)
		ImageAxis.add_artist(bound)
		text_pos = (s.location[1], s.location[0] - s.bounds - 6)
		ImageAxis.annotate(s.name, text_pos, color='w', weight='bold',fontsize=6, ha='center', va='center')
	ImageCanvas.draw()

def UpdateImage(val):
	global Brightness
	Brightness = float(val);
	Image.norm.vmax = Brightness
	ImageCanvas.draw_idle()
	if SliderLabel is not None:
		SliderLabel.config(text = "Brillo máximo: "+str(int(Brightness)))
#endregion

#region Create Funcions

def CreateCanvas(app, ImageClick):
	global ImageCanvas, Image, ImageFrame, ImageAxis
	ImageFrame = tk.Frame(app, width = 700, height = 400, bg = "white")
	ImageFrame.pack(side=tk.LEFT, fill = tk.BOTH, expand = True, anchor = tk.W)	

	ImageFigure = figure.Figure(figsize = (7,4), dpi = 100)
	ImageAxis = ImageFigure.add_subplot(111)
	Image = ImageAxis.imshow(Data, vmin = min(Data), vmax = max(Data), cmap="gray")
	ImageCanvas = FigureCanvasTkAgg(ImageFigure,master=ImageFrame)
	ImageCanvas.draw()
	ImageCanvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
	ImageCanvas.mpl_connect('button_press_event',ImageClick)

def CreateSlider(UpdateImage):
	global SliderLabel
	SliderWdg = ttk.Scale(ImageFrame, from_=min(Data), to=max(Data), orient=tk.HORIZONTAL, command = UpdateImage)
	SliderWdg.set(max(Data))
	SliderWdg.pack(fill = tk.X, anchor = tk.S, side = tk.BOTTOM)
	SliderLabel = tk.Label(ImageFrame, text = "Brillo máximo: "+str(max(Data)))
	SliderLabel.pack(fill = tk.X, anchor = tk.S, side = tk.BOTTOM)

def CreateSidebar(app, root, items):
	global Sidebar, SidebarList
	import STCore.ImageSelector

	Sidebar = tk.LabelFrame(app, relief=tk.RIDGE, width = 400, height = 400, text = "Opciones de Análisis")
	Sidebar.pack(side = tk.RIGHT, expand = True, fill = tk.BOTH, anchor = tk.NE)

	SidebarList = tk.Frame(Sidebar)
	SidebarList.pack(expand = 1, fill = tk.X, anchor = tk.NW)
	loc = (int(Data.shape[0] * 0.5), int (Data.shape[1] * 0.5))
	
	cmdBack = lambda : 	(Destroy(), STCore.ImageSelector.Awake(root, []))
	cmdCreate = lambda : 	SetStar.Awake(app, Data, Brightness, Stars, OnStarChange, location = loc)
	cmdTrack = lambda : Apply(root, items)
	
	buttonsFrame = tk.Frame(Sidebar)
	buttonsFrame.pack(anchor = tk.S, expand = 1, fill = tk.X)
	ttk.Button(buttonsFrame, text = "Volver", command = cmdBack).grid(row = 0, column = 0, sticky = tk.EW)
	ttk.Button(buttonsFrame, text = "Agregar estrella", command = cmdCreate).grid(row = 0, column = 1, sticky = tk.EW)
	ttk.Button(buttonsFrame, text = "Analizar", command = cmdTrack).grid(row = 0, column = 2, sticky = tk.EW)

#endregion

#region Global Variables
ViewerFrame = None
Data = None
Brightness = 0
Stars = []
ImageCanvas = None
Image = None 
ImageFrame = None 
ImageAxis = None
Sidebar = None 
SidebarList = None
SliderLabel = None
#endregion

#region Main Body

def Awake(root, items):
	global ViewerFrame, Data, Brightness, Stars, ImageCanvas, Image, ImageFrame, ImageAxis, Sidebar, SidebarList, SliderLabel
	STCore.DataManager.CurrentWindow = 2
	ViewerFrame = tk.Frame(root)
	ViewerFrame.pack( fill = tk.BOTH, expand = 1)
	tk.Label(ViewerFrame,text="Visor de Imagen").pack(fill = tk.X)
	Data =  items[0].data
	Brightness = max(Data)
	CreateCanvas(ViewerFrame, OnImageClick)
	CreateSlider(UpdateImage)
	CreateSidebar(ViewerFrame, root, items)
	OnStarChange()

def Destroy():
	ViewerFrame.destroy()

def Apply(root, items):
	import tkMessageBox
	if len(Stars) > 0:
		Destroy()
		Tracker.Awake(root, Stars, items, Brightness)
	else:
		tkMessageBox.showerror("Error", "Debe tener al menos una estrella para comenzar el analisis")
		return
def ClearStars():
	global Stars
	Stars = []
#endregion