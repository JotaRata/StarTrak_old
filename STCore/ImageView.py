# coding=utf-8

from logging import root
from operator import contains
from os import scandir
from tkinter.constants import W
import matplotlib
from matplotlib import axes
import numpy
from matplotlib import use, figure
from matplotlib.axes import Axes
from numpy.lib.histograms import histogram
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
from STCore import DataManager
from STCore.Component.Levels import Levels

#region Messages and Events
params = {"ytick.color" : "w",
			"xtick.color" : "w",
			"axes.labelcolor" : "grey",
			"axes.edgecolor" : "grey"}
plt.rcParams.update(params)
#endregion

#region Global Variables
ViewerFrame = None
Data = None
level_perc = (0,0)
Stars = []
canvas = None
implot = None 
ImageFrame = None 
axis : Axes = None

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

App : ttk.Frame = None
levelFrame : Levels = None
Viewport : tk.Canvas = None
Sidebar : tk.Canvas = None 

isInitialized = False
#endregion

#region Main Body

def Awake(root, items):
	global ViewerFrame, Data, Stars, canvas, implot, ImageFrame, axis, Sidebar, SidebarList, SliderLabel, level_perc, levelFrame, isInitialized

	STCore.DataManager.CurrentWindow = 2
	
	App.pack(fill=tk.BOTH, expand=1)

	#ViewerFrame = tk.Frame(root)
	#ttk.Label(ViewerFrame,text="Visor de Imagen").pack(fill = tk.X)
	Data =  items[0].data
	level_perc = STCore.DataManager.Levels

	# Setting Levels
	if not isinstance(level_perc, tuple):
		level_perc = (numpy.percentile(Data, 99.8), numpy.percentile(Data, 1))
		STCore.DataManager.Levels = level_perc
	
	BuildLayout(root)

	DrawCanvas()

	levelFrame.set_limits(numpy.nanmin(Data), numpy.nanmax(Data))
	levelFrame.setMax(level_perc[0])
	levelFrame.setMin(level_perc[1])
	

	OnStarChange()
	isInitialized = True

def BuildLayout(root : tk.Tk):
	global App, Viewport, Sidebar, levelFrame, isInitialized

	fresh = Viewport is None
	if isInitialized == False:
		App = ttk.Frame(root, width=root.winfo_width(), height=root.winfo_height())
		App.pack(fill=tk.BOTH, expand=1)

		App.columnconfigure(tuple(range(1)), weight=1)
		App.rowconfigure(tuple(range(1)), weight=1)

		CreateCanvas(App)
		CreateSidebar(App, App)
		CreateLevels(App)
		
		Viewport.grid(row=0, column=0, sticky=tk.NSEW)
		Sidebar.grid(row=0, column=1, rowspan=2, sticky=tk.NS)
		levelFrame.grid(row=1, column=0, sticky=tk.EW)
		
		if fresh:
			Destroy()
		isInitialized = True
	else:	# No need to rebuild
		Viewport.grid()
		Sidebar.grid()
		levelFrame.grid()

#region Create Funcions
def CreateCanvas(app):
	global canvas, implot, ImageFrame, axis, Viewport
	
	#ImageFrame = ttk.Frame(app, width = 700, height = 350)
	#ImageFrame.pack(side=tk.LEFT, fill = tk.BOTH, expand = True, anchor = tk.W)	

	fig = figure.Figure(figsize = (7,3.6), dpi = 100)
	fig.set_facecolor("black")

	# Create Canvas before any complex calculations
	canvas = FigureCanvasTkAgg(fig, master=app)
	
	Viewport = canvas.get_tk_widget()
	Viewport.configure(bg="black")
	Viewport.config(cursor = "fleur")

	axis = fig.add_subplot(111)
	fig.subplots_adjust(0.0,0.05,1,1)
	
	canvas.mpl_connect("button_press_event", OnMousePress) 
	canvas.mpl_connect("motion_notify_event", OnMouseDrag) 
	canvas.mpl_connect("button_release_event", OnMouseRelease) 
	canvas.mpl_connect('scroll_event',OnMouseScroll)

def DrawCanvas():
	global canvas, implot, ImageFrame, axis

	axis.clear()
	implot = axis.imshow(Data, vmin = level_perc[1], vmax = level_perc[0], cmap=ColorMaps[STCore.Settings._VISUAL_COLOR_.get()], norm = Modes[STCore.Settings._VISUAL_MODE_.get()])
	if STCore.Settings._SHOW_GRID_.get() == 1:
		axis.grid()
	
	axis.relim()
	canvas.draw()

	# Get axis limits and save it as a tuple
	global img_limits

	img_limits = (axis.get_xlim(), axis.get_ylim())
	UpdateCanvasOverlay()

def CreateSidebar(app, root):
	global Sidebar, SidebarList
	
	#import STCore.ImageSelector

	Sidebar = tk.Canvas(app, width = 250, relief = "flat", bg = "gray16")
	Sidebar.config(scrollregion=(0,0, 250, 1))

	SidebarList = ttk.Frame(Sidebar, width=250,height=root.winfo_height())
	Sidebar.create_window(250, 0, anchor=tk.NE, window=SidebarList, width=250, height=400)

	ScrollBar = ttk.Scrollbar(Sidebar, command=Sidebar.yview)
	Sidebar.config(yscrollcommand=ScrollBar.set)  
	ScrollBar.pack(side = tk.RIGHT,fill=tk.Y) 

	cmdTrack = lambda : Apply(root)
	def CommandCreate():
		if Data is None:
			return
		loc = (int(Data.shape[0] * 0.5), int (Data.shape[1] * 0.5))
		SetStar.Awake(app, Data, Stars, OnStarChange, location = loc, name = "Estrella " + str(len(Stars) + 1))
	def CommandBack():
		import STCore.ImageSelector
		Destroy()
		STCore.ImageSelector.Awake(root, [])

	buttonsFrame = ttk.Frame(Sidebar)
	buttonsFrame.pack(side=tk.BOTTOM, anchor = tk.S, expand = 1, fill = tk.X)
	
	PrevButton = ttk.Button(buttonsFrame, text = " Volver", image = icons.GetIcon("prev"), command = CommandBack, compound="left")
	PrevButton.grid(row = 0, column = 0, sticky = tk.EW)
	AddButton = ttk.Button(buttonsFrame, text = "Agregar estrella", command = CommandCreate, image = icons.GetIcon("add"), compound="left")
	AddButton.grid(row = 0, column = 1, sticky = tk.EW)
	NextButton = ttk.Button(buttonsFrame, text = "Continuar", command = cmdTrack, image = icons.GetIcon("next"), compound = "right")
	NextButton.grid(row = 0, column = 2, sticky = tk.EW)


def CreateLevels(app):
	global levelFrame
	levelFrame = Levels(app, ChangeLevels)

	
#endregion



#region Update Funcions

def UpdateStarList():
	global SidebarList
	for child in SidebarList.winfo_children():
		child.destroy()
	index = 0
	delete_icon = icons.GetIcon("delete")
	#Las funciones lambda no se pueden llamar dentro de un loop for o while,
	## para eso hay que crear una funcion que retorne un lambda
	def __helperCreateWindow(index, stName, stLoc, stRadius, stBound, stType,stThr, bsg):
		return lambda: SetStar.Awake(ViewerFrame, Data, Stars, OnStarChange, index, stName, stLoc, stRadius, stBound, stType, stThr)
	def __helperPop (list, index):
		return lambda: (list.pop(index), OnStarChange(), __helperTrackedChanged())
	def __helperTrackedChanged():
		Tracker.DataChanged = True

	for s in Stars:
		ListFrame = ttk.Frame(SidebarList, height=32, width=400)
		ListFrame.grid(row=index, column=0, sticky=tk.NSEW)
		#ListFrame.pack(fill = tk.X, expand = 1, anchor = tk.N, pady = 5)

		cmd = __helperCreateWindow(index, stName = s.name, stLoc = s.location, stRadius = s.radius, stBound = s.bounds, stType = s.type, stThr = 100 * s.threshold, bsg=s.bsigma)
		cmd2= __helperPop(Stars, index)
		ttk.Button(ListFrame, text = s.name, width = 30, command = cmd).pack(side = tk.LEFT, fill = tk.X, expand = 1)
		deleteButton = ttk.Button(ListFrame, image = delete_icon, width = 1, command = cmd2)
		deleteButton.image = delete_icon   #se necesita una referencia
		deleteButton.pack(side = tk.RIGHT)
		index += 1

	SidebarList.config(height=32 * index)
	Sidebar.config(scrollregion=(0,0, 250, 32 * index))
	UpdateCanvasOverlay()
	Sidebar.update_idletasks()

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
	canvas.draw_idle()

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
		global level_perc

		if levelFrame.getMin() > levelFrame.getMax():
			levelFrame.setMin(levelFrame.getMax() - 1)

		if levelFrame.getMax() <= levelFrame.getMin():
			levelFrame.setMax(levelFrame.getMin() + 1)


		_min = levelFrame.getMin()
		_max = levelFrame.getMax()
		
		implot.norm.vmax = _max
		implot.norm.vmin = _min + 0.01
		implot.set_cmap(ColorMaps[STCore.Settings._VISUAL_COLOR_.get()])
		implot.set_norm(Modes[STCore.Settings._VISUAL_MODE_.get()])

		STCore.DataManager.Levels =  (_max, _min)
		canvas.draw_idle()

#endregion



def Destroy():
	global img_limits, zoom_factor

	# Reset current viewport
	img_limits, zoom_factor = None, 1
	img_offset = (0, 0)

	#ViewerFrame.destroy()
	App.pack_forget()
	Sidebar.grid_remove()
	Viewport.grid_remove()
	levelFrame.grid_remove()
	gc.collect()

def Apply(root):
	items = DataManager.FileItemList
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
	canvas.draw_idle() # force re-draw

	

def OnMousePress(event):
	global canvas, MousePress, SelectedStar, axis, MousePressTime
	MousePress = 0, 0, event.xdata, event.ydata
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
	canvas.draw_idle()
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
			canvas.draw_idle() # fo

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
	canvas.draw_idle()

def OnMouseRelease(event):
	global MousePress, SelectedStar
	
	if SelectedStar == -100:
		if z_box is not None:
			setp(z_box, alpha = 0.5)
			setp(z_box, edgecolor = None)
	if SelectedStar >= 0:
		OnStarChange()
	SelectedStar = -1

	dx = event.xdata - MousePress[2]
	dy = event.ydata - MousePress[3]
	# Change this value for lower/higher drag tolerance
	drag_tolerance = 0.2

	if  dx < drag_tolerance and dy < drag_tolerance:
		loc = (int(event.ydata), int(event.xdata))
		SetStar.Awake(ViewerFrame, Data, Stars, OnStarChange, location = loc, name = "Estrella " + str(len(Stars) + 1))
	
	UpdateStarList()
	for a in axis.artists:
		setp(a, linewidth = 1)
	
	MousePress = None
	canvas.draw_idle()
	
	
def OnImageClick(event):
	loc = (int(event.ydata), int(event.xdata))
	SetStar.Awake(ViewerFrame, Data, Stars, OnStarChange, location = loc, name = "Estrella " + str(len(Stars) + 1))

def OnStarChange():
	UpdateStarList()
	#UpdateCanvasOverlay()
	STCore.DataManager.StarItemList = Stars