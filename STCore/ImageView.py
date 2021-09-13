# coding=utf-8

from operator import contains
from os import scandir
import matplotlib
from matplotlib import axes
import numpy
from matplotlib import use, figure
from matplotlib.axes import Axes
use("TkAgg")

import matplotlib as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle
from matplotlib.colors import Normalize, PowerNorm, LogNorm
from matplotlib.artist import setp, getp
import tkinter as tk
from tkinter import ttk
from STCore.item.Star import StarItem
from STCore import SetStar, Tracker
import STCore.DataManager
from time import time
import STCore.Settings
import STCore.RuntimeAnalysis
import gc
from PIL import Image
import STCore.utils.Icons as icons
#region Messages and Events
params = {"ytick.color" : "w",
			"xtick.color" : "w",
			"axes.labelcolor" : "grey",
			"axes.edgecolor" : "grey"}
plt.rcParams.update(params)
#endregion

#region Update Funcions

def UpdateStarList():
	global SidebarList
	for child in SidebarList.winfo_children():
		child.destroy()
	index = 0
	icon = icons.Icons["delete"]
	#Las funciones lambda no se pueden llamar dentro de un loop for o while,
	## para eso hay que crear una funcion que retorne un lambda
	def __helperCreateWindow(index, stName, stLoc, stRadius, stBound, stType,stThr, bsg):
		return lambda: SetStar.Awake(ViewerFrame, Data, Stars, OnStarChange, index, stName, stLoc, stRadius, stBound, stType, stThr)
	def __helperPop (list, index):
		return lambda: (list.pop(index), OnStarChange(), __helperTrackedChanged())
	def __helperTrackedChanged():
		Tracker.DataChanged = True

	for s in Stars:
		ListFrame = ttk.Frame(SidebarList)
		ListFrame.pack(fill = tk.X, expand = 1, anchor = tk.N, pady = 5)

		cmd = __helperCreateWindow(index, stName = s.name, stLoc = s.location, stRadius = s.radius, stBound = s.bounds, stType = s.type, stThr = 100 * s.threshold, bsg=s.bsigma)
		cmd2= __helperPop(Stars, index)
		ttk.Button(ListFrame, text = s.name, width = 10, command = cmd).pack(side = tk.LEFT, fill = tk.X, expand = 1)
		deleteButton = ttk.Button(ListFrame, image = icon, width = 1, command = cmd2)
		deleteButton.image = icon   #se necesita una referencia
		deleteButton.pack(side = tk.RIGHT)
		index += 1
	UpdateCanvasOverlay()

def UpdateCanvasOverlay():
	# Si se elimina el primer elemento de un lista en un ciclo for, entonces
	# ya no podra seguir iterando, lo que producir errores, se utiliza reversed para eliminar
	# el ultimo elemento de la lista primero y asi.
	for a in reversed(axis.artists):
		if a.label == "zoom_container" or a.label == "zoom_box":
			continue
		a.remove()
	for t in reversed(axis.texts):
		t.remove()
	for s in Stars:
		rect_pos = (s.location[1] - s.radius, s.location[0] - s.radius)
		rect = Rectangle(rect_pos, s.radius *2, s.radius *2, edgecolor = "w", facecolor='none')
		rect.label = "Rect"+str(Stars.index(s))
		bound_pos = (s.location[1] - s.bounds, s.location[0] - s.bounds)
		bound = Rectangle(bound_pos, s.bounds*2, s.bounds *2, edgecolor = "y", linestyle = 'dashed', facecolor='none')
		bound.label = "Bound"+str(Stars.index(s))
		axis.add_artist(rect)
		axis.add_artist(bound)
		text_pos = (s.location[1], s.location[0] - s.bounds - 6)
		text = axis.annotate(s.name, text_pos, color='w', weight='bold',fontsize=6, ha='center', va='center')
		text.label = "Text"+str(Stars.index(s))
	canvas.draw()

def UpdateZoomGizmo(scale, xrange, yrange):
	global axis, zoom_factor, img_offset, z_container, z_box

	aspect = yrange/xrange

	# Change the size of the Gizmo
	size = 320

	if zoom_factor > 1:
		gizmo_pos = img_offset[0] - xrange * scale, img_offset[1] - yrange * scale
		gizmo_w = size  * scale
		gizmo_h = size * scale * aspect

		if z_container is None:
			z_container = Rectangle(gizmo_pos, gizmo_w, gizmo_h, edgecolor = "w", facecolor='none')
			z_container.label = "zoom_container"

			z_box = Rectangle(gizmo_pos, gizmo_w, gizmo_h, alpha = 0.5)
			z_box.label = "zoom_box"

			axis.add_artist(z_container)
			axis.add_artist(z_box)
		else:
			z_container.set_xy(gizmo_pos)
			z_container.set_width(gizmo_w)
			z_container.set_height(gizmo_h)

			z_box.set_x(gizmo_pos[0] + 0.5*(img_offset[0] * gizmo_w / xrange- gizmo_w * scale) )	
			z_box.set_y(gizmo_pos[1] + 0.5*(img_offset[1] * gizmo_h / yrange- gizmo_h * scale) )	
			z_box.set_width(gizmo_w * scale)
			z_box.set_height(gizmo_h * scale)
	else:
		if z_container is not None:
			z_container.remove()
			z_container = None

			z_box.remove()
			z_box = None

def ChangeLevels():
		global Levels
		if _LEVEL_MIN_.get() >_LEVEL_MAX_.get():
			_LEVEL_MIN_.set(_LEVEL_MAX_.get() + 1)
		implot.norm.vmax = _LEVEL_MAX_.get()
		implot.norm.vmin = _LEVEL_MIN_.get() + 0.01
		implot.set_cmap(ColorMaps[STCore.Settings._VISUAL_COLOR_.get()])
		implot.set_norm(Modes[STCore.Settings._VISUAL_MODE_.get()])
		STCore.DataManager.Levels = (_LEVEL_MAX_.get(), _LEVEL_MIN_.get())
		Levels = (_LEVEL_MAX_.get(), _LEVEL_MIN_.get())
		canvas.draw_idle()

#endregion

#region Create Funcions
def CreateCanvas(app, ImageClick):
	global canvas, implot, ImageFrame, axis
	ImageFrame = ttk.Frame(app, width = 700, height = 350)
	ImageFrame.pack(side=tk.LEFT, fill = tk.BOTH, expand = True, anchor = tk.W)	

	ImageFigure = figure.Figure(figsize = (7,3.6), dpi = 100)
	axis = ImageFigure.add_subplot(111)
	
	ImageFigure.subplots_adjust(0.0,0.05,1,1)
	implot = axis.imshow(Data, vmin = Levels[1], vmax = Levels[0], cmap=ColorMaps[STCore.Settings._VISUAL_COLOR_.get()], norm = Modes[STCore.Settings._VISUAL_MODE_.get()])
	if STCore.Settings._SHOW_GRID_.get() == 1:
		axis.grid()
	ImageFigure.set_facecolor("black")
	
	canvas = FigureCanvasTkAgg(ImageFigure,master=ImageFrame)
	canvas.draw()
	wdg = canvas.get_tk_widget()
	wdg.configure(bg="black")
	wdg.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
	wdg.config(cursor = "fleur")

	# Get axis limits and save it as a tuple
	global img_limits

	img_limits = (axis.get_xlim(), axis.get_ylim())

	#ImageCanvas.mpl_connect('button_press_event',ImageClick)
	canvas.mpl_connect("button_press_event", OnMousePress) 
	canvas.mpl_connect("motion_notify_event", OnMouseDrag) 
	canvas.mpl_connect("button_release_event", OnMouseRelase) 
	canvas.mpl_connect('scroll_event',OnMouseScroll)

	UpdateCanvasOverlay()

def CreateSidebar(app, root, items):
	global Sidebar, SidebarList
	import STCore.ImageSelector

	Sidebar = ttk.LabelFrame(app, relief=tk.RIDGE, width = 200, height = 400, text = "Opciones de Análisis")
	Sidebar.pack(side = tk.RIGHT, expand = 0, fill = tk.BOTH, anchor = tk.NE)

	SidebarList = ttk.Frame(Sidebar)
	SidebarList.pack(expand = 1, fill = tk.X, anchor = tk.NW)
	loc = (int(Data.shape[0] * 0.5), int (Data.shape[1] * 0.5))
	
	cmdBack = lambda : 	(Destroy(), STCore.ImageSelector.Awake(root, []))
	cmdCreate = lambda : 	SetStar.Awake(app, Data, Stars, OnStarChange, location = loc, name = "Estrella " + str(len(Stars) + 1))
	cmdTrack = lambda : Apply(root, items)
	
	buttonsFrame = ttk.Frame(Sidebar)
	buttonsFrame.pack(anchor = tk.S, expand = 1, fill = tk.X)
	PrevButton = ttk.Button(buttonsFrame, text = " Volver", image = icons.Icons["prev"], command = cmdBack, compound="left")
	PrevButton.grid(row = 0, column = 0, sticky = tk.EW)
	AddButton = ttk.Button(buttonsFrame, text = "Agregar estrella", command = cmdCreate, image = icons.Icons["add"], compound="left")
	AddButton.grid(row = 0, column = 1, sticky = tk.EW)
	NextButton = ttk.Button(buttonsFrame, text = "Continuar", command = cmdTrack, image = icons.Icons["next"], compound = "right")
	NextButton.grid(row = 0, column = 2, sticky = tk.EW)

#endregion

#region Global Variables
ViewerFrame = None
Data = None
Levels = (0,0)
Stars = []
canvas = None
implot = None 
ImageFrame = None 
axis : Axes = None
Sidebar = None 
SidebarList = None
SliderLabel = None
ColorMaps = {"Escala de grises" : "gray", "Temperatura" : "seismic", "Arcoiris" : "rainbow", "Negativo" : "binary"}
Modes = {"Linear" : Normalize(), "Raiz cuadrada": PowerNorm(gamma = 0.5), "Logaritmico" : LogNorm()}

SelectedStar = -1
MousePress = None
MousePressTime = -1

img_limits : tuple = None
img_offset : tuple = (0,0)
zoom_factor = 1

z_container : Rectangle = None
z_box : Rectangle = None
#endregion

#region Main Body

def Awake(root, items):
	global ViewerFrame, Data, Stars, canvas, implot, ImageFrame, axis, Sidebar, SidebarList, SliderLabel, _LEVEL_MAX_, _LEVEL_MIN_, Levels

	STCore.DataManager.CurrentWindow = 2
	ViewerFrame = tk.Frame(root)
	ViewerFrame.pack( fill = tk.BOTH, expand = 1)
	ttk.Label(ViewerFrame,text="Visor de Imagen").pack(fill = tk.X)
	Data =  items[0].data
	Levels = STCore.DataManager.Levels

	# Setting Levels
	if not isinstance(Levels, tuple):
		Levels = (numpy.percentile(Data, 99.8), numpy.percentile(Data, 1))
		STCore.DataManager.Levels = Levels

	_LEVEL_MIN_ = tk.IntVar(value = Levels[1])
	_LEVEL_MAX_ = tk.IntVar(value = Levels[0])
	_LEVEL_MIN_.trace("w", lambda a,b,c: ChangeLevels())
	_LEVEL_MAX_.trace("w", lambda a,b,c: ChangeLevels())
	CreateCanvas(ViewerFrame, OnImageClick)

	levelFrame = ttk.LabelFrame(ImageFrame, text = "Niveles:")
	levelFrame.pack(fill = tk.X, anchor = tk.S, side = tk.BOTTOM)
	ttk.Label(levelFrame, text = "Maximo:").grid(row = 0,column = 0)
	ttk.Scale(levelFrame, from_= numpy.min(Data), to= numpy.max(Data), orient=tk.HORIZONTAL, variable = _LEVEL_MAX_).grid(row = 0, column = 1, columnspan = 10, sticky = tk.EW)
	ttk.Label(levelFrame, text = "Minimo:").grid(row = 1,column = 0)
	ttk.Scale(levelFrame, from_= numpy.min(Data), to= numpy.max(Data), orient=tk.HORIZONTAL, variable = _LEVEL_MIN_).grid(row = 1, column = 1, columnspan = 10, sticky = tk.EW)
	for x in range(10):
		tk.Grid.columnconfigure(levelFrame, x, weight=1)
	CreateSidebar(ViewerFrame, root, items)
	OnStarChange()

def Destroy():
	global img_limits, zoom_factor

	# Reset current viewport
	img_limits, zoom_factor = None, 1
	img_offset = (0, 0)

	ViewerFrame.destroy()
	gc.collect()

def Apply(root, items):
	from tkinter import messagebox
	if len(Stars) > 0:
		Destroy()
		Tracker.Awake(root, Stars, items)
		if STCore.DataManager.RuntimeEnabled == True:
			STCore.RuntimeAnalysis.StartRuntime(root)
	else:
		messagebox.showerror("Error", "Debe tener al menos una estrella para comenzar el analisis")
		return
def ClearStars():
	global Stars
	Stars = []
#endregion
def OnMouseScroll(event):
	global Data, canvas, axis, zoom_factor, img_limits, img_offset

	# Check if for some reason, no limits were defined
	if img_limits is None:
		axis.relim()
		img_limits = (axis.get_xlim(), axis.get_ylim())
	# Modify this for faster/slower increments
	increment = 0.5

	xdata = event.xdata # get event x location
	ydata = event.ydata # get event y location
	# If we are outside the viewport, then stop the function
	if xdata is None or ydata is None:
		return
	xcenter = 0.5 * (img_limits[0][1] + img_limits[0][0])
	ycenter = 0.5 * (img_limits[1][1] + img_limits[1][0])

	xrange = 0.5 * (img_limits[0][1] - img_limits[0][0])
	yrange = 0.5 * (img_limits[1][0] - img_limits[1][1]) # By some reason, matplotlib y-axis is inverted

	if event.button == 'up':
		# deal with zoom in
		if zoom_factor < 10:
			zoom_factor += increment
	elif event.button == 'down':
		# deal with zoom out
		if zoom_factor > 1:
			zoom_factor -= increment
	else:
		# deal with something that should never happen
		zoom_factor = 1
		print (event.button)
	scale = 1. / zoom_factor

	# Set the offset to the current mouse position
	img_offset = numpy.clip(xdata * scale + (1-scale)*img_offset[0], xrange * scale, img_limits[0][1] - xrange * scale), numpy.clip(ydata * scale + (1-scale)*img_offset[1], yrange * scale, img_limits[1][0] - yrange * scale)
	
	axis.set_xlim([img_offset[0] - xrange * scale,
					img_offset[0] + xrange * scale])
	axis.set_ylim([img_offset[1] - yrange * scale,
					img_offset[1] + yrange * scale])
	
	UpdateZoomGizmo(scale, xrange, yrange)
	canvas.draw() # force re-draw

	

def OnMousePress(event):
	global canvas, MousePress, SelectedStar, axis, MousePressTime
	
	for a in axis.artists:
		contains, attrd = a.contains(event)
		if contains:
			x0, y0 = a.xy
			MousePress = x0, y0, event.xdata, event.ydata

			# Check if we selected the zoom controls
			if a.label == "zoom_container" or a.label == "zoom_box":
				setp(z_box, alpha = 1)
				setp(z_box, edgecolor = "w")
				SelectedStar = -100  # We'll use the code -100 to identify whether the zoom controls are selected (to avoid declaring more global variables)
				break
			SelectedStar = int(next(filter(str.isdigit, a.label)))
			setp(a, linewidth = 4)
		else:
			setp(a, linewidth = 1)
	canvas.draw()
	MousePressTime = time()

def OnMouseDrag(event):
	global MousePress, Stars
	if MousePress is None or event.inaxes is None:
		return
	x0, y0, xpress, ypress = MousePress
	dx = event.xdata - xpress
	dy = event.ydata - ypress

	# Check whether the zoom controls are selected
	if SelectedStar == -100:
		if z_container is not None:
			global img_limits, axis, img_offset
			w, h = getp(z_container, "width"), getp(z_container, "height")
			xy = getp(z_container, "xy")

			xrange = 0.5 * (img_limits[0][1] - img_limits[0][0])
			yrange = 0.5 * (img_limits[1][0] - img_limits[1][1])
			
			scale = 1./zoom_factor
			xcenter = 2*(event.xdata - xy[0]) * xrange / w
			ycenter = 2*(event.ydata - xy[1]) * yrange / h

			xcenter = numpy.clip(xcenter, xrange * scale, img_limits[0][1] - xrange * scale)
			ycenter = numpy.clip(ycenter, yrange * scale, img_limits[1][0] - yrange * scale)
			img_offset = xcenter, ycenter
			axis.set_xlim([xcenter - xrange * scale,
						xcenter + xrange * scale])
			axis.set_ylim([ycenter - yrange * scale,
						ycenter + yrange * scale])
			UpdateZoomGizmo(scale, xrange, yrange)
			canvas.draw() # fo

		return # Stop the function here
	
	# Fail conditions
	if SelectedStar == -1 or len(Stars) == 0: return

	sel = list(filter(lambda obj: obj.label == "Rect"+str(SelectedStar), axis.artists))
	bod = list(filter(lambda obj: obj.label == "Bound"+str(SelectedStar), axis.artists))
	text = list(filter(lambda obj: obj.label == "Text"+str(SelectedStar), axis.texts))
	if len(sel) > 0 and len(text) > 0:
		sel[0].set_x(x0+dx + Stars[SelectedStar].bounds - Stars[SelectedStar].radius)
		sel[0].set_y(y0+dy + Stars[SelectedStar].bounds - Stars[SelectedStar].radius)
		bod[0].set_x(x0+dx)
		bod[0].set_y(y0+dy)
		text[0].set_x(x0 + dx + Stars[SelectedStar].bounds)
		text[0].set_y(y0 -6 +dy )
		Stars[SelectedStar].location = (int(y0 + dy + Stars[SelectedStar].bounds), int(x0 + dx + Stars[SelectedStar].bounds))
	canvas.draw()

def OnMouseRelase(event):
	global MousePress, SelectedStar
	UpdateStarList()
	MousePress = None
	if SelectedStar == -100:
		if z_box is not None:
			setp(z_box, alpha = 0.5)
			setp(z_box, edgecolor = None)
	if SelectedStar >= 0:
		OnStarChange()
	SelectedStar = -1
	if time() - MousePressTime < 0.2:
		OnImageClick(event)
	for a in axis.artists:
		setp(a, linewidth = 1)
	canvas.draw()
	
def OnImageClick(event):
	loc = (int(event.ydata), int(event.xdata))
	SetStar.Awake(ViewerFrame, Data, Stars, OnStarChange, location = loc, name = "Estrella " + str(len(Stars) + 1))

def OnStarChange():
	UpdateStarList()
	#UpdateCanvasOverlay()
	STCore.DataManager.StarItemList = Stars