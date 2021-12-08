# coding=utf-8

from pickle import FALSE
from sys import flags, version_info
from tkinter import filedialog
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

from STCore.item import Star
use("TkAgg")

import matplotlib as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle
from matplotlib.colors import Normalize, PowerNorm, LogNorm
from matplotlib.artist import setp, getp
import tkinter as tk
from tkinter import ttk
from STCore.Component import StarElement
from STCore.item.Star import *
import SetStar, Tracker
import STCore.DataManager
from time import time
import Settings
import RuntimeAnalysis
import DataManager, RuntimeAnalysis
import gc
from PIL import Image

from Icons import GetIcon
from Component import Levels, StarElement

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
sidebar_buttons : tk.Frame = None

sidebar_elements = []

isInitialized = False
#endregion

#region Main Body

def Awake(root):
	global ViewerFrame, Data, Stars, canvas, implot, ImageFrame, axis, Sidebar, SidebarList, SliderLabel, level_perc, levelFrame, isInitialized

	DataManager.CurrentWindow = 2
	
	App.pack(fill=tk.BOTH, expand=1)

	#ViewerFrame = tk.Frame(root)
	#ttk.Label(ViewerFrame,text="Visor de Imagen").pack(fill = tk.X)
	Data =  DataManager.FileItemList[0].data
	level_perc = DataManager.Levels

	# Setting Levels
	if not isinstance(level_perc, tuple):
		level_perc = (numpy.percentile(Data, 99.8), numpy.percentile(Data, 1))
		DataManager.Levels = level_perc
	
	#BuildLayout(root)
	if implot is None:
		App.after(10, DrawCanvas)

	levelFrame.set_limits(numpy.nanmin(Data), numpy.nanmax(Data))
	levelFrame.setMax(level_perc[0])
	levelFrame.setMin(level_perc[1])
	
	# Star version control
	version_changed = False
	index = 0
	for star in Stars:
		version_changed = version_changed or CheckVersion(star, index)
		index += 1

	if version_changed:
		print ("Se actualizaron las estrellas de una version anterior")
		SetStar.closedTime = 0


	OnStarChange()
	isInitialized = True

# Draws the layout in a single pass
def BuildLayout(root : tk.Tk):
	global App, Viewport, Sidebar, levelFrame, isInitialized

	# Checks if Viewport object hasn't been destroyed or unloaded
	fresh = Viewport is None

	# Check whether the layout hadn't been built yet
	if isInitialized == False:
		App = ttk.Frame(root, width=root.winfo_width(), height=root.winfo_height(), name="imageview")
		App.pack(fill=tk.BOTH, expand=1)

		App.columnconfigure(tuple(range(2)), weight=1)
		App.columnconfigure(1, weight=0)
		App.rowconfigure(tuple(range(2)), weight=1)

		CreateCanvas()
		CreateLevels()
		CreateSidebar(root)
			
		#Sidebar.grid_propagate(0)

		Viewport.grid(row=0, column=0, rowspan=2, sticky="nsew")
		Sidebar.grid(row=0, column=1, rowspan=2, sticky="nsew")
		levelFrame.grid(row=2, column=0, sticky=tk.EW)
		sidebar_buttons.grid(row=2, column=1, sticky="ew")
		
		if fresh:
			Destroy()
		isInitialized = True
	#else:	# No need to rebuild
		#Viewport.grid()
		#Sidebar.grid()
		#levelFrame.grid()
		#sidebar_buttons.grid()

#region Create Funcions

# Creates the viewport, but doesn't draw it to the UI
def CreateCanvas():
	global canvas, implot, ImageFrame, axis, Viewport
	
	#ImageFrame = ttk.Frame(app, width = 700, height = 350)
	#ImageFrame.pack(side=tk.LEFT, fill = tk.BOTH, expand = True, anchor = tk.W)	

	fig = figure.Figure(figsize = (7,3.6), dpi = 100)
	fig.set_facecolor("black")

	# Create Canvas before any complex calculations
	canvas = FigureCanvasTkAgg(fig, master=App)
	
	Viewport = canvas.get_tk_widget()
	Viewport.configure(bg="black")
	Viewport.config(cursor = "fleur")

	axis = fig.add_subplot(111)
	fig.subplots_adjust(0.0,0.05,1,1)
	
	canvas.mpl_connect("button_press_event", OnMousePress) 
	canvas.mpl_connect("motion_notify_event", OnMouseDrag) 
	canvas.mpl_connect("button_release_event", OnMouseRelease) 
	canvas.mpl_connect('scroll_event',OnMouseScroll)

# Fill the Canvas window for the viewport
def DrawCanvas():
	global canvas, implot, ImageFrame, axis

	axis.clear()
	implot = axis.imshow(Data, vmin = level_perc[1], vmax = level_perc[0], cmap=ColorMaps[Settings._VISUAL_COLOR_.get()], norm = Modes[Settings._VISUAL_MODE_.get()])
	if Settings._SHOW_GRID_.get() == 1:
		axis.grid()
	
	axis.relim()
	canvas.draw()

	# Get axis limits and save it as a tuple
	global img_limits

	img_limits = (axis.get_xlim(), axis.get_ylim())
	UpdateCanvasOverlay()

# Creates the siderbar, but does not draw it to the UI
def CreateSidebar(root):
	global App, Sidebar, SidebarList, sidebar_buttons
	
	Sidebar = tk.Canvas(App, width = 300, relief = "flat", bg = "gray16")
	Sidebar.config(scrollregion=(0,0, 300, 1))

	SidebarList = ttk.Frame(Sidebar, width=300,height=root.winfo_height())
	Sidebar.create_window(300, 0, anchor=tk.NE, window=SidebarList, width=300, height=600)

	SidebarList.grid_columnconfigure(0, weight=1)

	ScrollBar = ttk.Scrollbar(App, command=Sidebar.yview)
	ScrollBar.grid(row=0, column=2, rowspan=3, sticky=tk.NS)
	Sidebar.config(yscrollcommand=ScrollBar.set)  

	cmdTrack = lambda : Apply(root)
	def CommandCreate():
		if Data is None:
			return
		loc = (int(Data.shape[0] * 0.5), int (Data.shape[1] * 0.5))
		SetStar.Awake(Data, None, OnStarChange, AddStar, location = loc, name = "Estrella " + str(len(Stars) + 1))
	
	def CommandBack():
		import ImageSelector
		Destroy()
		ImageSelector.Awake(root, [])

	def CommandExport():
		with filedialog.asksaveasfile(mode="w", filetypes=[("Valores separados por comas", "*.csv"), ("Archivo de texto", "*.txt")]) as f:
			n=0
			for star in Stars:
				# Reemplazar; con cualquier caracter separador                                                               v
				#star.PrintData((NAME, SUM, FBACK, AREA, SBR, VALUE, FLUX, MBACK, DBACK, VBACK, BSIZE), header= n==0, sep= "{};", stdout=f)
				star.PrintData((NAME, VALUE, SUM, AREA, FLUX, SUMVBACK, BACKREFS, ABACK, FLUXBACK, NETFLUX, ABSMAG), header= n==0, sep= "{};", stdout=f)
				n+=1



	sidebar_buttons = ttk.Frame(App)
	
	AddButton = ttk.Button(sidebar_buttons, text = "Agregar estrella", command = CommandCreate, style="Highlight.TButton", image=GetIcon("add"), compound="left")

	PrevButton = ttk.Button(sidebar_buttons, text = " Volver", image = GetIcon("prev"), command = CommandBack, compound="left")
	ExpButton = ttk.Button(sidebar_buttons, text= "Exportar datos", image=GetIcon("export"), compound="left", command=CommandExport)
	NextButton = ttk.Button(sidebar_buttons, text = "Continuar", command = cmdTrack, image = GetIcon("next"), compound = "right")

	AddButton.grid(row = 0, column = 0, columnspan=3, sticky = "ew")
	PrevButton.grid(row = 1, column = 0, sticky = "ew")	
	ExpButton.grid(row=1, column=1, sticky="ew")
	NextButton.grid(row = 1, column = 2, sticky = "ew")


def CreateLevels():
	global levelFrame
	levelFrame = Levels(App, ChangeLevels)

#endregion



#region Update Funcions

sidebar_dirty = False
def AddStar(star : StarItem, onlyUI = False):
	global Stars, sidebar_elements
	global SidebarList
	
	index = len(sidebar_elements)

	# onlyUI flag tells whether the program is adding new stars to the list, or just refreshing their UI elements
	if not onlyUI:
		Stars.append(star)

	def SetTrackerDirty():
		Tracker.DataChanged = True
	def SetSidebarDirty():
		global sidebar_dirty
		sidebar_dirty = True

	cmd_star = lambda i=index: SetStar.Awake(Data, Stars[index], OnStarChange, None, i)	
	cmd_delete = lambda i=index: (Stars.pop(i), sidebar_elements.pop(i), OnStarChange(), SetTrackerDirty(), SetSidebarDirty())

	element = StarElement(SidebarList, star, index, cmd_star, SetGuideStar, cmd_delete)
	element.grid(row=index, column=0, sticky= "nsew")
	sidebar_elements.append(element)
def SetGuideStar(index):
	i = 0
	for star in Stars:
		star.type = 1 if i == index else 0
		i += 1
	UpdateStarList()
	
def UpdateStarList():
	global SidebarList, sidebar_elements, sidebar_dirty

	index = 0
	# Checks if sidebar is dirty
	if sidebar_dirty:
		for s in sidebar_elements:
			s.destroy()
		sidebar_elements = []
		sidebar_dirty = False

	# Recreate the list of elements if its size doesn't match the Stars (i.e. Load a trak file)
	if len(sidebar_elements) != len(Stars):
		for star in Stars:
			AddStar(star, onlyUI=True)
	
	# Assing the guide star if all or none  of them are already set
	# brightest star index, guide star count, brightest star value
	if len(Stars) > 0:
		bsi, gs, bs = 0, 0, 0
		for star in Stars:
			if star.type == 1:
				gs += 1
			if star.value > bs:
				bsi = index
				bs = star.value
			index += 1

		if gs > 1 or gs == 0:
			SetGuideStar(bsi)
			return
		
	index = 0
	# Update elements if necessary
	star : StarItem
	for star in Stars:
		element :StarElement = sidebar_elements[index]
		element.update_star(star)
		index += 1
		
	SidebarList.config(height=32 * index)
	Sidebar.update_idletasks()
	Sidebar.config(scrollregion=SidebarList.bbox())
	#Sidebar.after(10, lambda:Sidebar.config(scrollregion=(0,0, 250, 32 * index)))
	#Sidebar.update_idletasks()
	App.after(40, UpdateCanvasOverlay)

def CheckVersion(star : StarItem, index):

	# Version is way too old. needs to recompute
	if not hasattr(star, "version"):
		
		SetStar.Awake(Data, star, OnStarChange, skipUI = True, starIndex=index)
		return True
	changed = False

	# File is from another version, needs to be re-registered
	if star.version != CURRENT_VER:
		SetStar.Awake(Data, star, OnStarChange, skipUI = True, starIndex=index)
		changed = True
	return changed

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
		gizmo_w = size  * scale
		gizmo_h = size * scale * aspect
		gizmo_pos = img_offset[0] - xrange * scale, img_offset[1] + yrange * scale - gizmo_h
		
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

		if implot is None:
			return
			
		if levelFrame.getMin() > levelFrame.getMax():
			levelFrame.setMin(levelFrame.getMax() - 1)

		if levelFrame.getMax() <= levelFrame.getMin():
			levelFrame.setMax(levelFrame.getMin() + 1)


		_min = levelFrame.getMin()
		_max = levelFrame.getMax()
		
		implot.norm.vmax = _max
		implot.norm.vmin = _min + 0.01
		implot.set_cmap(ColorMaps[Settings._VISUAL_COLOR_.get()])
		implot.set_norm(Modes[Settings._VISUAL_MODE_.get()])

		DataManager.Levels =  (_max, _min)
		canvas.draw_idle()

#endregion



def Destroy():
	global img_limits, zoom_factor, img_offset, z_container, z_box

	# Reset current viewport
	zoom_factor =  1
	axis.relim()
	axis.autoscale()
	if z_container is not None:
		z_container.remove()
		z_box.remove()
		z_container = None
		z_box = None
	
	img_offset = (0,0)
	img_limits = (axis.get_xlim(), axis.get_ylim())
	App.pack_forget()
	#gc.collect()

def Apply(root):
	items = DataManager.FileItemList
	
	from tkinter import messagebox
	if len(Stars) > 0:
		Destroy()
		Tracker.Awake(root, Stars, items)
		if DataManager.RuntimeEnabled == True:
			RuntimeAnalysis.StartRuntime(root)
	else:
		messagebox.showerror("Error", "Debe tener al menos una estrella para comenzar el analisis")
		return
	DataManager.StarItemList = Stars

def ClearStars():
	global Stars, sidebar_elements
	Stars = []
	for s in sidebar_elements:
		s.destroy()
	sidebar_elements = []

#endregion
def OnMouseScroll(event):
	global Data, canvas, axis, zoom_factor, img_limits, img_offset

	# Check if for some reason, no limits were defined
	if img_limits is None:
		axis.relim()
		axis.autoscale(True)
		img_limits = (axis.get_xlim(), axis.get_ylim())  # By some reason mpl axis are inverted
	# Modify this for faster/slower increments
	increment = 0.5

	xdata = event.xdata # get event x location
	ydata = event.ydata # get event y location
	# If we are outside the viewport, then stop the function
	if xdata is None or ydata is None:
		return

	xrange = 0.5 * (img_limits[0][1] - img_limits[0][0])
	yrange = 0.5 * (img_limits[1][0] - img_limits[1][1])

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
	img_offset = numpy.clip(xdata * scale + (1-scale)*img_offset[0], xrange * scale, img_limits[0][1] - xrange * scale), numpy.clip(ydata * scale + (1-scale)*img_offset[1], yrange*scale, img_limits[1][0] - yrange * scale)
	
	axis.set_xlim([img_offset[0] - xrange * scale,
					img_offset[0] + xrange * scale])
	axis.set_ylim([img_offset[1] + yrange * scale,
					img_offset[1] - yrange * scale])
	
	UpdateZoomGizmo(scale, xrange, yrange)
	canvas.draw_idle() # force re-draw

	
#drag displacement = lastX, lastY, dispX, dispY
drag_displacement = (0, 0, 0, 0)

def OnMousePress(event):
	global canvas, MousePress, SelectedStar, axis, drag_displacement
	MousePress = 0, 0, event.xdata, event.ydata
	drag_displacement = event.xdata, event.ydata, 0, 0

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

def OnMouseDrag(event):
	global MousePress, Stars, drag_displacement
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
			axis.set_ylim([ycenter + yrange * scale,
						ycenter - yrange * scale])
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

	sx = drag_displacement[2] + abs(event.xdata - drag_displacement[0])
	sy = drag_displacement[3] + abs(event.ydata - drag_displacement[1])
	drag_displacement = event.xdata, event.ydata, sx, sy

def OnMouseRelease(event):
	global MousePress, SelectedStar, drag_displacement
	
	# Change this value for lower/higher drag tolerance
	drag_tolerance = 0.2

	if SelectedStar == -100:
		if z_box is not None:
			setp(z_box, alpha = 0.5)
			setp(z_box, edgecolor = None)
		SelectedStar = -1
		return
	if SelectedStar >= 0:
		OnStarChange()
	SelectedStar = -1

	if  drag_displacement[2] < drag_tolerance and drag_displacement[3] < drag_tolerance:
		OnImageClick(event)
	for a in axis.artists:
		setp(a, linewidth = 1)
	
	MousePress = None
	canvas.draw_idle()
	
	
def OnImageClick(event):
	loc = (int(event.ydata), int(event.xdata))
	SetStar.Awake(Data, None, OnStarChange, AddStar, location = loc, name = "Estrella " + str(len(Stars) + 1))

def OnStarChange(star : StarItem = None, index = -1):
	global Stars

	if star is not None:
		Stars[index] = star
	
	UpdateStarList()
	#UpdateCanvasOverlay()
	DataManager.StarItemList = Stars