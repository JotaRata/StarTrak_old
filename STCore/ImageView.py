# coding=utf-8

from astropy.io import fits
from  numpy import min, max
from matplotlib import use, figure
use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle
from matplotlib.colors import Normalize, PowerNorm, LogNorm
from matplotlib.artist import setp
import Tkinter as tk
import ttk
from STCore.item.Star import StarItem
from STCore import SetStar, Tracker
import STCore.DataManager
from time import time
import STCore.Settings
#region Messages and Events

def OnImageClick(event):
	loc = (int(event.ydata), int(event.xdata))
	SetStar.Awake(ViewerFrame, Data, Stars, OnStarChange, location = loc)

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
	return lambda: SetStar.Awake(ViewerFrame, Data, Stars, OnStarChange, index, stName, stLoc, stRadius, stBound, stType, stThr)
def __helperPop (list, index):
	return lambda: (list.pop(index), OnStarChange(), __helperTrackedChanged())
def __helperTrackedChanged():
	Tracker.DataChanged = True
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
		rect.aname = "Rect"+str(Stars.index(s))
		bound_pos = (s.location[1] - s.bounds, s.location[0] - s.bounds)
		bound = Rectangle(bound_pos, s.bounds*2, s.bounds *2, edgecolor = "0.5", linestyle = 'dashed', facecolor='none')
		bound.aname = "Bound"+str(Stars.index(s))
		ImageAxis.add_artist(rect)
		ImageAxis.add_artist(bound)
		text_pos = (s.location[1], s.location[0] - s.bounds - 6)
		text = ImageAxis.annotate(s.name, text_pos, color='w', weight='bold',fontsize=6, ha='center', va='center')
		text.aname = "Text"+str(Stars.index(s))
	ImageCanvas.draw()

def UpdateImage():
		global Levels
		if _LEVEL_MIN_.get() >_LEVEL_MAX_.get():
			_LEVEL_MIN_.set(_LEVEL_MAX_.get())
		Image.norm.vmax = _LEVEL_MAX_.get()
		Image.norm.vmin = _LEVEL_MIN_.get() + 0.01
		Image.set_cmap(ColorMaps[STCore.Settings._VISUAL_COLOR_.get()])
		Image.set_norm(Modes[STCore.Settings._VISUAL_MODE_.get()])
		STCore.DataManager.Levels = (_LEVEL_MAX_.get(), _LEVEL_MIN_.get())
		Levels = (_LEVEL_MAX_.get(), _LEVEL_MIN_.get())
		ImageCanvas.draw_idle()

#endregion

#region Create Funcions
def CreateCanvas(app, ImageClick):
	global ImageCanvas, Image, ImageFrame, ImageAxis
	ImageFrame = tk.Frame(app, width = 700, height = 350, bg = "white")
	ImageFrame.pack(side=tk.LEFT, fill = tk.BOTH, expand = True, anchor = tk.W)	

	ImageFigure = figure.Figure(figsize = (7,3.6), dpi = 100)
	ImageAxis = ImageFigure.add_subplot(111)
	Image = ImageAxis.imshow(Data, vmin = Levels[1], vmax = Levels[0], cmap=ColorMaps[STCore.Settings._VISUAL_COLOR_.get()], norm = Modes[STCore.Settings._VISUAL_MODE_.get()])
	if STCore.Settings._SHOW_GRID_.get() == 1:
		ImageAxis.grid()
	ImageCanvas = FigureCanvasTkAgg(ImageFigure,master=ImageFrame)
	ImageCanvas.draw()
	wdg = ImageCanvas.get_tk_widget()
	wdg.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
	wdg.config(cursor = "fleur")
	#ImageCanvas.mpl_connect('button_press_event',ImageClick)
	ImageCanvas.mpl_connect("button_press_event", OnMousePress) 
	ImageCanvas.mpl_connect("motion_notify_event", OnMouseDrag) 
	ImageCanvas.mpl_connect("button_release_event", OnMouseRelase) 


def CreateSidebar(app, root, items):
	global Sidebar, SidebarList
	import STCore.ImageSelector

	Sidebar = tk.LabelFrame(app, relief=tk.RIDGE, width = 400, height = 400, text = "Opciones de Análisis")
	Sidebar.pack(side = tk.RIGHT, expand = True, fill = tk.BOTH, anchor = tk.NE)

	SidebarList = tk.Frame(Sidebar)
	SidebarList.pack(expand = 1, fill = tk.X, anchor = tk.NW)
	loc = (int(Data.shape[0] * 0.5), int (Data.shape[1] * 0.5))
	
	cmdBack = lambda : 	(Destroy(), STCore.ImageSelector.Awake(root, []))
	cmdCreate = lambda : 	SetStar.Awake(app, Data, Stars, OnStarChange, location = loc)
	cmdTrack = lambda : Apply(root, items)
	
	buttonsFrame = tk.Frame(Sidebar)
	buttonsFrame.pack(anchor = tk.S, expand = 1, fill = tk.X)
	ttk.Button(buttonsFrame, text = "Volver", command = cmdBack).grid(row = 0, column = 0, sticky = tk.EW)
	ttk.Button(buttonsFrame, text = "Agregar estrella", command = cmdCreate).grid(row = 0, column = 1, sticky = tk.EW)
	ttk.Button(buttonsFrame, text = "Continuar", command = cmdTrack).grid(row = 0, column = 2, sticky = tk.EW)

#endregion

#region Global Variables
ViewerFrame = None
Data = None
Levels = (0,0)
Stars = []
ImageCanvas = None
Image = None 
ImageFrame = None 
ImageAxis = None
Sidebar = None 
SidebarList = None
SliderLabel = None
ColorMaps = {"Escala de grises" : "gray", "Temperatura" : "seismic", "Arcoiris" : "rainbow", "Negativo" : "binary"}
Modes = {"Linear" : Normalize(), "Raiz cuadrada": PowerNorm(gamma = 0.5), "Logartitmico" : LogNorm()}

SelectedStar = -1
MousePress = None
MousePressTime = -1
#endregion

#region Main Body

def Awake(root, items):
	global ViewerFrame, Data, Stars, ImageCanvas, Image, ImageFrame, ImageAxis, Sidebar, SidebarList, SliderLabel, _LEVEL_MAX_, _LEVEL_MIN_, Levels
	STCore.DataManager.CurrentWindow = 2
	ViewerFrame = tk.Frame(root)
	ViewerFrame.pack( fill = tk.BOTH, expand = 1)
	tk.Label(ViewerFrame,text="Visor de Imagen").pack(fill = tk.X)
	Data =  items[0].data
	Levels = STCore.DataManager.Levels
	if not isinstance(Levels, tuple):
		print "Viewer: not tuple!", type(Levels)
		Levels = (max(Data), min(Data))
		STCore.DataManager.Levels = Levels
	_LEVEL_MIN_ = tk.IntVar(value = Levels[1])
	_LEVEL_MAX_ = tk.IntVar(value = Levels[0])
	_LEVEL_MIN_.trace("w", lambda a,b,c: UpdateImage())
	_LEVEL_MAX_.trace("w", lambda a,b,c: UpdateImage())
	CreateCanvas(ViewerFrame, OnImageClick)

	levelFrame = tk.LabelFrame(ImageFrame, text = "Niveles:")
	levelFrame.pack(fill = tk.X, anchor = tk.S, side = tk.BOTTOM)
	tk.Label(levelFrame, text = "Maximo:").grid(row = 0,column = 0)
	ttk.Scale(levelFrame, from_=min(Data), to=max(Data), orient=tk.HORIZONTAL, variable = _LEVEL_MAX_).grid(row = 0, column = 1, columnspan = 10, sticky = tk.EW)
	tk.Label(levelFrame, text = "Minimo:").grid(row = 1,column = 0)
	ttk.Scale(levelFrame, from_=min(Data), to=max(Data), orient=tk.HORIZONTAL, variable = _LEVEL_MIN_).grid(row = 1, column = 1, columnspan = 10, sticky = tk.EW)
	for x in range(10):
		tk.Grid.columnconfigure(levelFrame, x, weight=1)
	CreateSidebar(ViewerFrame, root, items)
	OnStarChange()

def Destroy():
	ViewerFrame.destroy()

def Apply(root, items):
	import tkMessageBox
	if len(Stars) > 0:
		Destroy()
		Tracker.Awake(root, Stars, items)
	else:
		tkMessageBox.showerror("Error", "Debe tener al menos una estrella para comenzar el analisis")
		return
def ClearStars():
	global Stars
	Stars = []
#endregion

def OnMousePress(event):
	global ImageCanvas, MousePress, SelectedStar, ImageAxis, MousePressTime
	for a in ImageAxis.artists:
		contains, attrd = a.contains(event)
		if contains:
			x0, y0 = a.xy
			MousePress = x0, y0, event.xdata, event.ydata
			SelectedStar = int(filter(str.isdigit, a.aname)[0])
			setp(a, linewidth = 4)
		else:
			setp(a, linewidth = 1)
	ImageCanvas.draw()
	MousePressTime = time()

def OnMouseDrag(event):
	global MousePress, Stars
	if MousePress is None or SelectedStar == -1 or len(Stars) == 0 or event.inaxes is None: return
	x0, y0, xpress, ypress = MousePress
	dx = event.xdata - xpress
	dy = event.ydata - ypress
	sel = filter(lambda obj: obj.aname == "Rect"+str(SelectedStar), ImageAxis.artists)
	bod = filter(lambda obj: obj.aname == "Bound"+str(SelectedStar), ImageAxis.artists)
	text = filter(lambda obj: obj.aname == "Text"+str(SelectedStar), ImageAxis.texts)
	if len(sel) > 0 and len(text) > 0:
		sel[0].set_x(x0+dx + Stars[SelectedStar].bounds - Stars[SelectedStar].radius)
		sel[0].set_y(y0+dy + Stars[SelectedStar].bounds - Stars[SelectedStar].radius)
		bod[0].set_x(x0+dx)
		bod[0].set_y(y0+dy)
		text[0].set_x(x0 + dx + Stars[SelectedStar].bounds)
		text[0].set_y(y0 -6 +dy )
		Stars[SelectedStar].location = (int(y0 + dy + Stars[SelectedStar].bounds), int(x0 + dx + Stars[SelectedStar].bounds))
	ImageCanvas.draw()

def OnMouseRelase(event):
	global MousePress, SelectedStar
	UpdateStarList()
	MousePress = None
	SelectedStar = -1
	if time() - MousePressTime < 0.2:
		OnImageClick(event)
		print "timed"
	for a in ImageAxis.artists:
		setp(a, linewidth = 1)
	ImageCanvas.draw()