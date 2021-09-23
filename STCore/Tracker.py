# coding=utf-8

from STCore.item import ResultSettings
import numpy
from matplotlib import use, figure
use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle, Polygon
from matplotlib.artist import setp, getp
import tkinter as tk
from tkinter import ttk
from os.path import basename
from STCore.item.Track import TrackItem
from STCore.utils.backgroundEstimator import GetBackground
from STCore.utils.backgroundEstimator import GetBackgroundMean
import STCore.utils.Icons as icons

import STCore.Results
import STCore.DataManager
import STCore.ResultsConfigurator
import STCore.Composite
from threading import Thread, Lock
from time import sleep, time
from functools import partial
from PIL import Image, ImageTk
from tkinter import messagebox
from scipy.ndimage import median_filter

#region Variables
TrackerFrame = None
TitleLabel = None
ImgFrame = None
canvas = None
img = None
axis = None
Sidebar = None
SidebarList = None
BrightestStar = None
TrackedStars = []
DataChanged = False
buttonsFrame = None
lock = Lock()

IsTracking = False
SelectedTrack = -1
MousePress = None
CurrentFile = 0
ScrollFileLbd = (None, None)


img_limits : tuple = None
img_offset : tuple = (0,0)
zoom_factor = 1

z_container : Rectangle = None
z_box : Rectangle = None

#endregion
def Awake(root, stars, ItemList):
	global TrackerFrame, TitleLabel, ImgFrame, TrackedStars, pool, BrightestStar, CurrentFile, DataChanged, IsTracking, ScrollFileLbd
	STCore.DataManager.CurrentWindow = 3
	IsTracking = False
	TrackerFrame = ttk.Frame(root)
	TrackerFrame.pack(fill = tk.BOTH, expand = 1)
	TitleFrame = ttk.Frame(TrackerFrame)
	TitleFrame.pack(fill = tk.X)
	TitleLabel = ttk.Label(TitleFrame, text = "Analizando imagen..")
	TitleLabel.pack(fill = tk.X)
	ScrollFileLbd = lambda: PrevFile(ItemList, stars), lambda: NextFile(ItemList, stars)
	
	if len(TrackedStars) == 0 and len(stars) != 0:
		TrackedStars =[]
		for s in stars:
			item = TrackItem()
			item.star = s
			item.lastValue = s.value
			item.currPos = s.location
			item.trackedPos = []
			TrackedStars.append(item)
			OnFinishTrack()
			
	ttk.Button(TitleFrame, image = icons.Icons["prev"], command = ScrollFileLbd[0]).pack(side = tk.LEFT)
	ttk.Button(TitleFrame, image = icons.Icons["next"], command = ScrollFileLbd[1]).pack(side = tk.RIGHT)
	ImgFrame = ttk.Frame(TrackerFrame)
	ImgFrame.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
	CreateCanvas(ItemList,stars)
	CreateSidebar(root, ItemList, stars)
	img.set_array(ItemList[CurrentFile].data)
	CurrentFile = 0
	if len(TrackedStars) > 0:
		if DataChanged == True:
			messagebox.showwarning("Aviso", "La lista de estrellas ha sido modificada\nNo se podrán usar los datos de rastreo anteriores.")
			TrackedStars = []
			STCore.Results.MagData = None
			if STCore.DataManager.RuntimeEnabled == True:
				StartTracking(root, STCore.RuntimeAnalysis.filesList, stars)
			else:
				OnFinishTrack()
		else:
			OnFinishTrack()
	brightestStarValue = 0
	for s in stars:
		if s.value > brightestStarValue:
			BrightestStar = s
			brightestStarValue = s.value

	
	UpdateSidebar(ItemList[CurrentFile].data, stars)

def UpdateImage():
	global img
	img.set_cmap(STCore.ImageView.ColorMaps[STCore.Settings._VISUAL_COLOR_.get()])
	img.set_norm(STCore.ImageView.Modes[STCore.Settings._VISUAL_MODE_.get()])
	canvas.draw_idle()

def StartTracking(root, ItemList, stars):
	global TrackedStars, IsTracking, applyButton, CurrentFile
	if len(TrackedStars) > 0:
		condition = (len(TrackedStars[0].trackedPos) > 0 and messagebox.askyesno("Confirmar sobreescritura", "Ya existen datos de rastreo, desea sobreescribirlos?")) or len(TrackedStars[0].trackedPos) == 0
	else:
		condition = True
	if condition:
		TrackedStars =[]
		CurrentFile = 0
		for s in stars:
			item = TrackItem()
			item.star = s
			item.lastValue = s.value
			item.currValue = s.value
			item.currPos = s.location
			item.trackedPos = []
			TrackedStars.append(item)
		if STCore.DataManager.RuntimeEnabled == False:
			applyButton.config(state = tk.DISABLED)
		IsTracking = True
		UpdateTrack(root, ItemList, stars)

def Destroy():
	global TrackedStars, img, axis
	if STCore.DataManager.RuntimeEnabled == True:
			if STCore.ResultsConfigurator.CheckWindowClear() == False:
				STCore.ResultsConfigurator.PlotWindow.destroy()
	TrackerFrame.destroy()
	img = None
	axis = None

def CreateSidebar(root, ItemList, stars):
	import STCore.ImageView
	global TrackerFrame, SidebarList, Sidebar, applyButton, TrackButton, buttonsFrame
	Sidebar = ttk.LabelFrame(TrackerFrame, width = 200, text = "Detalles de análisis")
	Sidebar.pack(side = tk.RIGHT, expand = 0, fill = tk.BOTH, anchor = tk.NE)
	
	SidebarList = ttk.Frame(Sidebar)
	SidebarList.pack(expand = 1, fill = tk.X, anchor = tk.NW)

	cmdBack = lambda: (Destroy(), STCore.ImageView.Awake(root, ItemList))
	cmdNext = lambda: Apply(root, ItemList)

	ApplyMenu = tk.Menu(Sidebar, tearoff=0)
	ApplyMenu.add_command(label="Analizar", command=cmdNext)
	if STCore.ResultsConfigurator.SettingsObject is not None:
		ApplyMenu.add_command(label="Configurar analisiss", command=lambda: OpenResults(root, ItemList))
	ApplyMenu.add_command(label="Componer imagen", command=lambda : CompositeNow(root, ItemList))

	buttonsFrame = ttk.Frame(Sidebar, width = 200)
	buttonsFrame.pack(anchor = tk.S, expand = 1, fill = tk.X)
	PrevButton = ttk.Button(buttonsFrame, text = " Volver", command = cmdBack, image = icons.Icons["prev"], compound = "left")
	PrevButton.grid(row = 0, column = 0, sticky = tk.EW)
	if STCore.DataManager.RuntimeEnabled == False:
		TrackButton = ttk.Button(buttonsFrame)
		TrackButton.config(text = "Iniciar",image = icons.Icons["play"], compound = "left", command = lambda: (StartTracking(root, ItemList, stars), SwitchTrackButton(root, ItemList, stars)))	
		applyButton = ttk.Button(buttonsFrame, text = "Continuar",image = icons.Icons["next"], compound = "right", command = cmdNext, state = tk.DISABLED)
		applyButton.bind("<Button-1>", lambda event: PopupMenu(event, ApplyMenu))
		applyButton.grid(row = 0, column = 2, sticky = tk.EW)
	else:
		TrackButton = ttk.Button(buttonsFrame)
		TrackButton.config(text = "Detener Analisis", image = icons.Icons["stop"], compound = "left", command = lambda: (StopTracking(), SwitchTrackButton(root, ItemList, stars, True)))
		RestartButton = ttk.Button(buttonsFrame, text = "Reiniciar", image = icons.Icons["restart"], compound = "left", command = lambda: StartTracking(root, STCore.RuntimeAnalysis.filesList, stars))
		RestartButton.grid(row = 0, column = 2, sticky = tk.EW)
	TrackButton.grid(row = 0, column = 1, sticky = tk.EW)

def OnRuntimeWindowClosed(root):
	if STCore.DataManager.RuntimeEnabled == False:
		return
	CreateButton = ttk.Button(buttonsFrame, text = "Mostrar Grafico", image = icons.Icons["plot"], compound = "left")
	cmd = lambda: (CreateButton.destroy(), STCore.ResultsConfigurator.Awake(root, STCore.RuntimeAnalysis.filesList, TrackedStars))
	STCore.DataManager.CurrentWindow = 3
	CreateButton.grid(row = 0, column = 3, sticky = tk.EW)
	CreateButton.config(command = cmd)

def SwitchTrackButton(root, ItemList, stars, RuntimeEnd = False):
	global TrackButton, IsTracking
	if RuntimeEnd == True:
		TrackButton.config(text = "Componer Imagen", command = lambda: CompositeNow(root, ItemList), state = tk.NORMAL, image = icons.Icons["image"], compound = "left")
		return;
	if not IsTracking:
		TrackButton.config(text = "Iniciar", image = icons.Icons["play"],command = lambda: (StartTracking(root, ItemList, stars), SwitchTrackButton(root, ItemList, stars)))
	else:
		TrackButton.config(text = "Detener",image = icons.Icons["stop"], command = lambda: (StopTracking(), SwitchTrackButton(root, ItemList, stars)))
def PopupMenu(event, ApplyMenu):
	ApplyMenu.post(event.x_root, event.y_root)

def CompositeNow(root, ItemList):
	if len(TrackedStars[0].trackedPos) == 0:
		messagebox.showerror("Error", "No hay estrellas restreadas.")
		return
	if len(TrackedStars) < 2:
		messagebox.showerror("Error", "Se necesitan al menos dos estrellas para iniciar una composicion.")
		return
	Destroy()
	STCore.Composite.Awake(root, ItemList, TrackedStars)
def OpenResults(root, ItemList):
	if len(TrackedStars[0].trackedPos) > 0:
		STCore.Results.Awake(root, ItemList, TrackedStars)
	else:
		messagebox.showerror("Error", "No hay estrellas restreadas.")

def Apply(root, ItemList):
	if len(TrackedStars[0].trackedPos) > 0:
		if (STCore.ResultsConfigurator.SettingsObject is None):
			STCore.ResultsConfigurator.SettingsObject = ResultSettings.ResultSetting()		
		Destroy()
		STCore.Results.Awake(root, ItemList[0:len(TrackedStars[0].trackedPos)], TrackedStars)
	else:
		messagebox.showerror("Error", "No hay estrellas restreadas.")

def UpdateSidebar(data, stars):
	global SidebarList
	index = 0
	for child in SidebarList.winfo_children():
		child.destroy()
	for track in TrackedStars:
		trackFrame = ttk.Frame(SidebarList, style="TButton")
		col = "black"
		if CurrentFile in track.lostPoints:
			col = "red"
		#frame.config(highlightbackground = col, borderwidth = 2, highlightthickness = 2)
		tk.Grid.columnconfigure(trackFrame, 2, weight=0)
		trackFrame.pack(fill = tk.X, anchor = tk.N, pady=4)
		ttk.Label(trackFrame, text = track.star.name,font="-weight bold").grid(row = 0, column = 0,sticky = tk.W, columnspan = 2)
		if len(track.trackedPos) > 0:
			
			_trust = 100 *  numpy.clip(1 - numpy.abs(-GetMaxima(data, track, CurrentFile) + track.star.value) / track.star.threshold, 0, 1) 
			_trust = int(_trust)

			ttk.Label(trackFrame, text = "Posicion: " + str(track.trackedPos[CurrentFile]), width = 18).grid(row = 1, column = 0,sticky = tk.W)
			ttk.Label(trackFrame, text = "Confianza: " + str(_trust)+"%", width = 18).grid(row = 1, column = 1,sticky = tk.W)
			ttk.Label(trackFrame, text = "Rastreados: " + str(len(track.trackedPos) - len(track.lostPoints)), width = 15).grid(row = 2, column = 0,sticky = tk.W)
			ttk.Label(trackFrame, text = "Perdidos: " + str(len(track.lostPoints)), width = 15).grid(row = 2, column = 1,sticky = tk.W)
		clipLoc = (track.currPos[1], track.currPos[0]) 
		if len(track.trackedPos) > 0:
			clipLoc = numpy.clip(track.trackedPos[CurrentFile], stars[index].radius, (data.shape[1] - stars[index].radius, data.shape[0] - stars[index].radius))
		crop = data[clipLoc[1]-stars[index].radius : clipLoc[1]+stars[index].radius,clipLoc[0]-stars[index].radius : clipLoc[0]+stars[index].radius].astype(float)
		minv = STCore.DataManager.Levels[1]
		maxv = STCore.DataManager.Levels[0]
		noisy = numpy.clip(255 * (crop - minv) / (maxv - minv), 0 , 255).astype(numpy.uint8)	
		Pic = Image.fromarray(noisy, mode='L')
		Pic = Pic.resize((50, 50))
		Img = ImageTk.PhotoImage(Pic)
		ImageLabel = ttk.Label(trackFrame, image = Img, width = 50)
		ImageLabel.image = Img
		ImageLabel.grid(row = 0, column = 3, columnspan = 1, rowspan = 3, padx = 20)
		index += 1

def CreateCanvas(ItemList, stars):
	global canvas, ImgFrame, img, axis, CurrentFile
	ImageFigure = figure.Figure(figsize = (7,4), dpi = 100)
	ImageFigure.set_facecolor("black")
	if CurrentFile >= len(ItemList):
		CurrentFile = 0

	data = ItemList[CurrentFile].data
	axis = ImageFigure.add_subplot(111)
	axis.set_axis_off()
	ImageFigure.subplots_adjust(0.01,0.01,0.99,1)
	levels = STCore.DataManager.Levels
	if  not isinstance(levels, tuple):
		#print "Tracker: not tuple!"
		levels = (numpy.max(data), numpy.min(data))
		STCore.DataManager.Levels = STCore.ImageView.Levels = levels
	img = axis.imshow(data, vmin = levels[1], vmax = levels[0], cmap=STCore.ImageView.ColorMaps[STCore.Settings._VISUAL_COLOR_.get()], norm = STCore.ImageView.Modes[STCore.Settings._VISUAL_MODE_.get()])
	canvas = FigureCanvasTkAgg(ImageFigure,master=ImgFrame)
	if STCore.Settings._SHOW_GRID_.get() == 1:
		axis.grid()
	canvas.draw()
	
	# Get axis limits and save it as a tuple
	global img_limits

	img_limits = (axis.get_xlim(), axis.get_ylim())

	canvas.mpl_connect("button_press_event", OnMousePress) 
	canvas.mpl_connect("motion_notify_event", OnMouseDrag) 
	canvas.mpl_connect("button_release_event", lambda event: OnMouseRelase(event, stars, ItemList)) 
	canvas.mpl_connect('scroll_event',OnMouseScroll)

	wdg = canvas.get_tk_widget()
	wdg.config(cursor = "fleur", bg="black")
	wdg.pack(fill=tk.BOTH, expand=1)

	UpdateCanvasOverlay(stars, CurrentFile, BrightestStar)
	#wdg.wait_visibility()

def OnFinishTrack():
	global DataChanged, applyButton, TrackButton, IsTracking
	STCore.DataManager.TrackItemList = TrackedStars
	DataChanged = False
	if len(TrackedStars) > 0:
		if len(TrackedStars[0].trackedPos) > 0:
			if STCore.DataManager.RuntimeEnabled == False:
				applyButton.config(state = tk.NORMAL)
				TrackButton.config(state = tk.NORMAL, image = icons.Icons["play"])
	IsTracking = False

def Track(index, ItemList, stars):
	global TrackedStars, BrightestStar
	#starIndex = 0
	#print ("Tracking Thread started")
	data = ItemList[index].data
	back, bgStD =  GetBackground(data)
	deltaPos = numpy.array([0,0])
	indices = range(len(stars))
	sortedIndices = sorted(indices, key = lambda e: stars[e].value, reverse = True)

	for starIndex in sortedIndices:
		s = stars[starIndex]
		Pos = numpy.array(TrackedStars[starIndex].currPos)
		clipLoc = numpy.clip(Pos, s.bounds, (data.shape[0] - s.bounds, data.shape[1] - s.bounds))
		if BrightestStar != s and STCore.Settings._TRACK_PREDICTION_.get() == 1:
			clipLoc = numpy.clip(Pos + deltaPos, s.bounds, (data.shape[0] - s.bounds, data.shape[1] - s.bounds))
		crop = data[clipLoc[0]-s.bounds : clipLoc[0]+s.bounds,clipLoc[1]-s.bounds : clipLoc[1]+s.bounds]
		crop = median_filter(crop, 2)
		#indices = numpy.where((numpy.abs(-crop + s.value) < s.threshold) & (crop > bgStD*2 + back))

		lvalue = s.value + back#TrackedStars[starIndex].lastValue 
		

		sigma_criterion = (numpy.abs(crop - back) > s.bsigma * bgStD)		# Determina cuando la imagen se encuentra a (threshold) sigma del fondo
		value_criterion = ((-crop + lvalue) < numpy.abs(lvalue - max(numpy.max(crop) - back, back) ) * (1 + s.threshold)/2 )			# Compara el brillo de la estrella con su referencia
		#spread_criterion = sigma_criterion.sum() > 4							# Se asegura de que no se detecten hot pixels como estrellas
		# \operatorname{abs}\left(L-\max\left(b-c,\ 1\right)\right)+d\cdot2
		indices = numpy.unravel_index(numpy.flatnonzero( value_criterion &  sigma_criterion),  crop.shape)
		SearchIndices = numpy.swapaxes(numpy.array(indices), 0, 1)
		RegPositions = numpy.empty((0,2), int)

		print (s.name, lvalue,"||", crop.max(), "||", numpy.sum(indices), "||b", back)
		i = 0

		while i < SearchIndices.shape[0]:
			_ind = numpy.atleast_2d(SearchIndices[i,:]) + clipLoc - s.bounds
			RegPositions = numpy.append(RegPositions, _ind, axis = 0)
			i += 1
		if len(RegPositions) != 0:
			MeanPos = numpy.mean(RegPositions, axis = 0).astype(int)
			TrackedStars[starIndex].lastPos = TrackedStars[starIndex].currPos
			TrackedStars[starIndex].lastValue = TrackedStars[starIndex].currValue 
			TrackedStars[starIndex].currPos = MeanPos.tolist()
			TrackedStars[starIndex].trackedPos.append(list(reversed(TrackedStars[starIndex].currPos)))
			TrackedStars[starIndex].currValue = GetMaxima(data, TrackedStars[starIndex], index, back)
			if TrackedStars[starIndex].lastSeen != -1:
				TrackedStars[starIndex].lastSeen = -1
		else:
			if TrackedStars[starIndex].lastSeen == -1:
				TrackedStars[starIndex].lastSeen = index
			TrackedStars[starIndex].lostPoints.append(index)
			TrackedStars[starIndex].trackedPos.append(list(reversed(TrackedStars[starIndex].lastPos)))
		if BrightestStar == s:
			deltaPos = numpy.array(TrackedStars[starIndex].currPos) - Pos
		#starIndex += 1
	
def StopTracking():
	global IsTracking
	if IsTracking:
		IsTracking = False
	if STCore.DataManager.RuntimeEnabled == True:
		STCore.RuntimeAnalysis.StopRuntime()


def UpdateTrack(root, ItemList, stars, index = 0, auto = True):
	global TrackedStars, SidebarList, CurrentFile, IsTracking, TrackButton
	if (index >= len(ItemList) or IsTracking == False) and auto:
		OnFinishTrack()
		if STCore.DataManager.RuntimeEnabled == False:
			TrackButton.config(text = "Iniciar", command = lambda: (StartTracking(root, ItemList, stars), SwitchTrackButton(root, ItemList, stars)))
		for ts in TrackedStars:
			ts.PrintData()
		return
	CurrentFile = index
	img.set_array(ItemList[index].data)

	#trackThread = Thread(target = Track, args = (index,ItemList, stars))
	#trackThread.start()
	#trackThread.join()

	Track(index,ItemList, stars)	 # Se elimino mutlithreading por ahora..
	UpdateCanvasOverlay(stars, index)
	UpdateSidebar(ItemList[index].data, stars)
	#updsThread = Thread(target = UpdateSidebar, args = (ItemList[index].data, stars))
	#updsThread.start()
	#updsThread.join()
	#UpdateSidebar(ItemList[index].data, stars)
	ScrollFileLbd = lambda: PrevFile(ItemList, stars), lambda: NextFile(ItemList, stars)
	TitleLabel.config(text = "Analizando imagen: "+ basename(ItemList[index].path))
	if auto:
		TrackerFrame.after(50, lambda: UpdateTrack(root, ItemList, stars, index + 1))

def UpdateCanvasOverlay(stars, ImgIndex, brightest =  None):
	for a in reversed(axis.artists):
		if a.label == "zoom_container" or a.label == "zoom_box":
			continue
		a.remove()
	for t in reversed(axis.texts):
		t.remove()
	stIndex = 0
	for s in stars:
		print(len(TrackedStars), len(stars))
		trackPos = (TrackedStars[stIndex].currPos[1], TrackedStars[stIndex].currPos[0])
		if len(TrackedStars[stIndex].trackedPos) > 0:
			trackPos = TrackedStars[stIndex].trackedPos[ImgIndex]
		
		col = "w"
		if s == BrightestStar:
			col = "y"
		
		if len(trackPos) == 0:
			continue
		if ImgIndex in TrackedStars[stIndex].lostPoints:
			col = "r"
		if STCore.Settings._SHOW_TRACKEDPOS_.get() == 1:
			try:
				points = TrackedStars[stIndex].trackedPos[max(ImgIndex - 4, 0):ImgIndex + 1]
				poly = Polygon(points , closed = False, fill = False, edgecolor = "w", linewidth = 2)
				poly.label = "Poly"+str(stIndex)
				axis.add_artist(poly)
			except:
				pass
		rect_pos = (trackPos[0] - s.radius, trackPos[1] - s.radius)
		rect = Rectangle(rect_pos, s.radius *2, s.radius *2, edgecolor = col, facecolor='none')
		rect.label = "Rect"+str(stIndex)
		axis.add_artist(rect)
		text_pos = (trackPos[0], trackPos[1] - s.radius - 6)
		text = axis.annotate(s.name, text_pos, color=col, weight='bold',fontsize=6, ha='center', va='center')
		text.label = "Text"+str(stIndex)
		stIndex += 1
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

# Copiado de SetStar
def GetMaxima(data, track, fileIndex, background=0):
	xloc = track.trackedPos[fileIndex][1]
	yloc = track.trackedPos[fileIndex][0]
	radius = track.star.radius
	value = track.star.value
	clipLoc = numpy.clip((xloc,yloc), radius, (data.shape[0] - radius, data.shape[1] - radius))
	crop = data[clipLoc[0]-radius : clipLoc[0]+radius,clipLoc[1]-radius : clipLoc[1]+radius]
	return int(numpy.max(crop) - background)
	#return  numpy.max(data[vloc[0]-radius : vloc[0]+radius,vloc[1]-radius : vloc[1]+radius])


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

MousePressTime=0	# Global
def OnMousePress(event):
	global canvas, MousePress, SelectedTrack, axis, MousePressTime
	if time() - MousePressTime < 0.2:
		return
	for a in axis.artists:
		if a.label != "Poly":
			contains, attrd = a.contains(event)
			if contains:
				tup = a.xy
				x0, y0 = tup[0], tup[1]
				MousePress = x0, y0, event.xdata, event.ydata

				# Check if we selected the zoom controls (copied from ImageView.py)
				if a.label == "zoom_container" or a.label == "zoom_box":
					setp(z_box, alpha = 1)
					setp(z_box, edgecolor = "w")
					SelectedTrack = -100  # We'll use the code -100 to identify whether the zoom controls are selected (to avoid declaring more global variables)
					break
				
				SelectedTrack = int("".join(next(filter(str.isdigit, a.label))))
				setp(a, linewidth = 4)
			else:
				setp(a, linewidth = 1)
	canvas.draw()
	MousePressTime = time()

def OnMouseDrag(event):
	global MousePress
	if MousePress is None or event.inaxes is None:
			return
		
	x0, y0, xpress, ypress = MousePress
	dx = event.xdata - xpress
	dy = event.ydata - ypress

	# Check whether the zoom controls are selected
	if SelectedTrack == -100:
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
	if SelectedTrack == -1 or len(TrackedStars) == 0: return


	sel = list(filter(lambda obj: obj.label == "Rect"+str(SelectedTrack), axis.artists))
	text = list(filter(lambda obj: obj.label == "Text"+str(SelectedTrack), axis.texts))
	if len(sel) > 0 and len(text) > 0:
		sel[0].set_x(x0+dx)
		sel[0].set_y(y0+dy)
		text[0].set_x(x0 + dx + TrackedStars[SelectedTrack].star.radius)
		text[0].set_y(y0 - TrackedStars[SelectedTrack].star.radius + 6 +dy)
		TrackedStars[SelectedTrack].trackedPos[CurrentFile][1] = int(y0 + dy + TrackedStars[SelectedTrack].star.radius)
		TrackedStars[SelectedTrack].trackedPos[CurrentFile][0] = int(x0 + dx+ TrackedStars[SelectedTrack].star.radius)
		TrackedStars[SelectedTrack].currPos = list(reversed(TrackedStars[SelectedTrack].trackedPos[CurrentFile]))
	poly = next(filter(lambda obj: obj.label == "Poly"+str(SelectedTrack), axis.artists))
	poly.set_xy(TrackedStars[SelectedTrack].trackedPos[max(CurrentFile - 4, 0):CurrentFile + 1])
	canvas.draw()

def OnMouseRelase(event, stars, ItemList):
	global MousePress, SelectedTrack
	
	MousePress = None

	if SelectedTrack == -100:
		if z_box is not None:
			setp(z_box, alpha = 0.5)
			setp(z_box, edgecolor = None)
		canvas.draw()
		return


	if CurrentFile in TrackedStars[SelectedTrack].lostPoints:
		TrackedStars[SelectedTrack].lostPoints.remove(CurrentFile)
	if STCore.DataManager.RuntimeEnabled == True:
		try:
			data = STCore.RuntimeAnalysis.filesList[CurrentFile].data
			UpdateSidebar(data, stars)
			if STCore.Results.MagData is not None:
				STCore.Results.MagData[CurrentFile, SelectedTrack] = STCore.Results.GetMagnitude(data, TrackedStars[SelectedTrack], STCore.Results.Constant,  STCore.Tracker.CurrentFile, GetBackgroundMean(data))
		except:
			pass
	else:
		UpdateSidebar(ItemList[CurrentFile].data, stars)

	SelectedTrack = -1
	canvas.draw()
	for a in axis.artists:
		if a.label != "Poly":
			setp(a, linewidth = 1)
	canvas.draw()

def NextFile(ItemList, stars):
	global CurrentFile
	if CurrentFile + 1 >= len(ItemList):
		return
	CurrentFile += 1
	UpdateSidebar(ItemList[CurrentFile].data, stars)
	img.set_array(ItemList[CurrentFile].data)
	UpdateCanvasOverlay(stars, CurrentFile)
	TitleLabel.config(text = "Analizando imagen: "+ basename(ItemList[CurrentFile].path))

def PrevFile(ItemList, stars):
	global CurrentFile
	if CurrentFile - 1 < 0:
		return
	CurrentFile -= 1
	UpdateSidebar(ItemList[CurrentFile].data, stars)
	img.set_array(ItemList[CurrentFile].data)
	UpdateCanvasOverlay(stars, CurrentFile)
	TitleLabel.config(text = "Analizando imagen: "+ basename(ItemList[CurrentFile].path))
