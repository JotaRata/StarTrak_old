# coding=utf-8

from astropy.io.fits.column import FORMATORDER
from item import ResultSettings
import numpy
from matplotlib import use, figure
use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle, Polygon
from matplotlib.artist import setp, getp
import tkinter as tk
from tkinter import ttk
from os.path import basename
from item.Track import TrackItem
from utils.backgroundEstimator import GetBackground
from utils.backgroundEstimator import GetBackgroundMean
import STCore.utils.Icons as icons

from STCore import Results, DataManager, ResultsConfigurator, Composite, RuntimeAnalysis, Settings

from threading import Thread, Lock
from time import sleep, time
from functools import partial
from PIL import Image, ImageTk
from tkinter import messagebox
from scipy.ndimage import median_filter

#region Variables
App = None
FileLabel = None
ImgFrame = None
canvas = None
implot = None
axis = None

Viewport : tk.Canvas = None
Sidebar : tk.Canvas = None
SidebarList : ttk.Frame = None

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

IsInitialized = False

#endregion
def Awake(root, stars, ItemList):
	global App, FileLabel, ImgFrame, TrackedStars, pool, BrightestStar, CurrentFile, DataChanged, IsTracking, ScrollFileLbd
	
	DataManager.CurrentWindow = 3
	IsTracking = False

	App.pack(fill=tk.BOTH, expand=1)

	if len(TrackedStars) == 0 and len(stars) != 0:
		TrackedStars =[]
		for s in stars:
			item = TrackItem()
			item.star = s
			item.lastValue = s.value
			item.currPos = s.location
			item.trackedPos = [list(reversed(s.location))]
			TrackedStars.append(item)
			OnFinishTrack()
	
	ScrollFileLbd = lambda: PrevFile(ItemList, stars), lambda: NextFile(ItemList, stars)
	
	Sidebar.config(scrollregion=(0,0, 300, 64 * len(TrackedStars)))
	FileLabel.config(text = "Imagen: "+ basename(ItemList[CurrentFile].path))

	BuildLayout(root)

	App.after(10, DrawCanvas)

	CurrentFile = 0
	if len(TrackedStars) > 0:
		if DataChanged == True:
			messagebox.showwarning("Aviso", "La lista de estrellas ha sido modificada\nNo se podrán usar los datos de rastreo anteriores.")
			TrackedStars = []
			Results.MagData = None
			if DataManager.RuntimeEnabled == True:
				StartTracking(root, RuntimeAnalysis.filesList, stars)
			else:
				OnFinishTrack()
		else:
			OnFinishTrack()
	brightestStarValue = 0
	for s in stars:
		if s.value > brightestStarValue:
			BrightestStar = s
			brightestStarValue = s.value
	
	UpdateSidebar(ItemList[CurrentFile].data)

# Creates the viewport, but doesn't draw it to the UI
def CreateCanvas():
	global canvas, axis, CurrentFile, Viewport

	ImageFigure = figure.Figure(figsize = (7,4), dpi = 100)
	ImageFigure.set_facecolor("black")
	if CurrentFile >= len(DataManager.FileItemList):
		CurrentFile = 0

	canvas = FigureCanvasTkAgg(ImageFigure,master=App)
	if Settings._SHOW_GRID_.get() == 1:
		axis.grid()

	Viewport = canvas.get_tk_widget()
	Viewport.config(cursor = "fleur", bg="black")

	axis = ImageFigure.add_subplot(111)
	ImageFigure.subplots_adjust(0.01,0.01,0.99,1)

	canvas.mpl_connect("button_press_event", OnMousePress) 
	canvas.mpl_connect("motion_notify_event", OnMouseDrag) 
	canvas.mpl_connect("button_release_event", OnMouseRelase) 
	canvas.mpl_connect('scroll_event',OnMouseScroll)

	
def BuildLayout(root):
	global App, Viewport, Sidebar, IsInitialized

	fresh = Viewport is None
	# Check whether the layout hadn't been built yet
	if IsInitialized == False:
		App = ttk.Frame(root, name="tracker")
		App.pack(fill = tk.BOTH, expand = 1)

		App.columnconfigure(tuple(range(2)), weight=1)
		App.columnconfigure(1, weight=0)
		App.rowconfigure(tuple(range(2)), weight=1)

		CreateCanvas()
		CreateNavigationBar()
		CreateSidebar(root)

		Viewport.grid(row=0, column=0, rowspan=2, sticky=tk.NSEW)
		Sidebar.grid(row=0, column=1, rowspan=3, sticky=tk.NSEW)
		FooterFrame.grid(row=2, column=0, sticky="ew")

		if fresh:
			Destroy()
		IsInitialized = True


# Fill the Canvas window for the viewport
def DrawCanvas():
	from STCore.ImageView import ColorMaps, Modes
	global canvas, implot, ImageFrame, axis

	data = DataManager.FileItemList[CurrentFile].data

	axis.clear()
	implot = axis.imshow(data, vmin = DataManager.Levels[1], vmax = DataManager.Levels[0], cmap=ColorMaps[Settings._VISUAL_COLOR_.get()], norm = Modes[Settings._VISUAL_MODE_.get()])

	axis.relim()
	canvas.draw()

	# Get axis limits and save it as a tuple
	global img_limits

	img_limits = (axis.get_xlim(), axis.get_ylim())
	UpdateCanvasOverlay()


# Creates the sidebar, but doesn't draw it to the UI
def CreateSidebar(root):
	global App, SidebarList, Sidebar, applyButton, TrackButton, buttonsFrame

	Sidebar = tk.Canvas(App, width = 300, relief = "flat", bg = "gray16")
	Sidebar.config(scrollregion=(0,0, 300, 1))

	SidebarList = ttk.Frame(Sidebar, width=300,height=root.winfo_height())
	Sidebar.create_window(300, 0, anchor=tk.NE, window=SidebarList, width=300, height=600)

	SidebarList.grid_columnconfigure(0, weight=1)
	
	ScrollBar = ttk.Scrollbar(App, command=Sidebar.yview)
	ScrollBar.grid(row=0, column=2, rowspan=2, sticky=tk.NS)
	Sidebar.config(yscrollcommand=ScrollBar.set)  

	def CommandBack():
		# TODO: #8 Remove inter-dependence of components
		import STCore.ImageView
		Destroy()
		STCore.ImageView.Awake(root)

	cmdNext = lambda: Apply(root)

	ApplyMenu = tk.Menu(Sidebar, tearoff=0)
	ApplyMenu.add_command(label="Analizar", command=cmdNext)

	if ResultsConfigurator.SettingsObject is not None:
		ApplyMenu.add_command(label="Configurar analisiss", command=lambda: OpenResults(root))
		
	ApplyMenu.add_command(label="Componer imagen", command=lambda : CompositeNow(root))

	buttonsFrame = ttk.Frame(Sidebar, width = 200)
	buttonsFrame.pack(anchor = tk.S, expand = 1, fill = tk.X)
	PrevButton = ttk.Button(buttonsFrame, text = " Volver", command = CommandBack, image = icons.Icons["prev"], compound = "left")
	PrevButton.grid(row = 0, column = 0, sticky = tk.EW)
	if DataManager.RuntimeEnabled == False:
		TrackButton = ttk.Button(buttonsFrame)
		TrackButton.config(text = "Iniciar",image = icons.Icons["play"], compound = "left", command = lambda: (StartTracking(root), SwitchTrackButton(root)))	
		applyButton = ttk.Button(buttonsFrame, text = "Continuar",image = icons.Icons["next"], compound = "right", command = cmdNext, state = tk.DISABLED)
		applyButton.bind("<Button-1>", lambda event: PopupMenu(event, ApplyMenu))
		applyButton.grid(row = 0, column = 2, sticky = tk.EW)
	else:
		TrackButton = ttk.Button(buttonsFrame)
		TrackButton.config(text = "Detener Analisis", image = icons.Icons["stop"], compound = "left", command = lambda: (StopTracking(), SwitchTrackButton(root, True)))
		RestartButton = ttk.Button(buttonsFrame, text = "Reiniciar", image = icons.Icons["restart"], compound = "left", command = lambda: StartTracking(root, RuntimeAnalysis))
		RestartButton.grid(row = 0, column = 2, sticky = tk.EW)
	TrackButton.grid(row = 0, column = 1, sticky = tk.EW)

# Creates the footer
def CreateNavigationBar():
	global FooterFrame, FileLabel

	FooterFrame = ttk.Frame(App)
	FooterFrame.grid_columnconfigure(1, weight=1)
	ttk.Button(FooterFrame, image = icons.Icons["prev"], command = ScrollFileLbd[0]).grid(row=0, column=0)
	FileLabel = ttk.Label(FooterFrame, text="Imagen",justify="center", width=20)
	FileLabel.grid(row=0, column=1)
	ttk.Button(FooterFrame, image = icons.Icons["next"], command = ScrollFileLbd[1]).grid(row=0, column=2)

def Destroy():
	global TrackedStars, implot, axis
	if DataManager.RuntimeEnabled == True:
			if ResultsConfigurator.CheckWindowClear() == False:
				ResultsConfigurator.PlotWindow.destroy()
	
	App.pack_forget()

	#implot = None
	#axis = None


def OnRuntimeWindowClosed(root):
	if DataManager.RuntimeEnabled == False:
		return
	CreateButton = ttk.Button(buttonsFrame, text = "Mostrar Grafico", image = icons.Icons["plot"], compound = "left")
	cmd = lambda: (CreateButton.destroy(), ResultsConfigurator.Awake(root, RuntimeAnalysis.filesList, TrackedStars))
	DataManager.CurrentWindow = 3
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
	Composite.Awake(root, ItemList, TrackedStars)
def OpenResults(root, ItemList):
	if len(TrackedStars[0].trackedPos) > 0:
		Results.Awake(root, ItemList, TrackedStars)
	else:
		messagebox.showerror("Error", "No hay estrellas restreadas.")

def Apply(root, ItemList):
	if len(TrackedStars[0].trackedPos) > 0:
		if (ResultsConfigurator.SettingsObject is None):
			ResultsConfigurator.SettingsObject = ResultSettings.ResultSetting()		
		Destroy()
		Results.Awake(root, ItemList[0:len(TrackedStars[0].trackedPos)], TrackedStars)
	else:
		messagebox.showerror("Error", "No hay estrellas restreadas.")

def UpdateImage():
	global implot
	from ImageView import ColorMaps, Modes
	implot.set_cmap(ColorMaps[Settings._VISUAL_COLOR_.get()])
	implot.set_norm(Modes[Settings._VISUAL_MODE_.get()])
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
			item.trackedPos = [list(reversed(s.location))]
			TrackedStars.append(item)
		if DataManager.RuntimeEnabled == False:
			applyButton.config(state = tk.DISABLED)
		IsTracking = True
		UpdateTrack(root, ItemList, stars)


def UpdateSidebar(data):
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
			clipLoc = numpy.clip(track.trackedPos[CurrentFile], track.star.radius, (data.shape[1] - track.star.radius, data.shape[0] - track.star.radius))
		
		crop = data[clipLoc[1]-track.star.radius : clipLoc[1]+track.star.radius,clipLoc[0]-track.star.radius : clipLoc[0]+track.star.radius].astype(float)
		minv = DataManager.Levels[1]
		maxv = DataManager.Levels[0]
		noisy = numpy.clip(255 * (crop - minv) / (maxv - minv), 0 , 255).astype(numpy.uint8)	
		Pic = Image.fromarray(noisy, mode='L')
		Pic = Pic.resize((50, 50))
		Img = ImageTk.PhotoImage(Pic)
		ImageLabel = ttk.Label(trackFrame, image = Img, width = 50)
		ImageLabel.image = Img
		ImageLabel.grid(row = 0, column = 3, columnspan = 1, rowspan = 3, padx = 20)
		index += 1


def OnFinishTrack():
	global DataChanged, applyButton, TrackButton, IsTracking
	DataManager.TrackItemList = TrackedStars
	DataChanged = False
	if len(TrackedStars) > 0:
		if len(TrackedStars[0].trackedPos) > 0:
			if DataManager.RuntimeEnabled == False:
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
		if BrightestStar != s and Settings._TRACK_PREDICTION_.get() == 1:
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
	if DataManager.RuntimeEnabled == True:
		RuntimeAnalysis.StopRuntime()


def UpdateTrack(root, ItemList, stars, index = 1, auto = True):
	global TrackedStars, SidebarList, CurrentFile, IsTracking, TrackButton
	if (index >= len(ItemList) or IsTracking == False) and auto:
		OnFinishTrack()
		if DataManager.RuntimeEnabled == False:
			TrackButton.config(text = "Iniciar", command = lambda: (StartTracking(root, ItemList, stars), SwitchTrackButton(root, ItemList, stars)))
		for ts in TrackedStars:
			ts.PrintData()
		return
	CurrentFile = index
	implot.set_array(ItemList[index].data)

	#trackThread = Thread(target = Track, args = (index,ItemList, stars))
	#trackThread.start()
	#trackThread.join()

	Track(index,ItemList, stars)	 # Se elimino mutlithreading por ahora..
	UpdateCanvasOverlay(stars, index)
	UpdateSidebar(ItemList[index].data)
	#updsThread = Thread(target = UpdateSidebar, args = (ItemList[index].data, stars))
	#updsThread.start()
	#updsThread.join()
	#UpdateSidebar(ItemList[index].data, stars)
	ScrollFileLbd = lambda: PrevFile(ItemList, stars), lambda: NextFile(ItemList, stars)
	FileLabel.config(text = "Imagen: "+ basename(ItemList[index].path))
	if auto:
		App.after(50, lambda: UpdateTrack(root, ItemList, stars, index + 1))

def UpdateCanvasOverlay():
	for a in reversed(axis.artists):
		if a.label == "zoom_container" or a.label == "zoom_box":
			continue
		a.remove()
	for t in reversed(axis.texts):
		t.remove()
	stIndex = 0
	for ts in TrackedStars:
		trackPos = (TrackedStars[stIndex].currPos[1], TrackedStars[stIndex].currPos[0])
		if len(TrackedStars[stIndex].trackedPos) > 0:
			trackPos = TrackedStars[stIndex].trackedPos[CurrentFile]
		
		col = "w"
		if ts.star == BrightestStar:
			col = "y"
		
		if len(trackPos) == 0:
			continue
		if CurrentFile in TrackedStars[stIndex].lostPoints:
			col = "r"
		if Settings._SHOW_TRACKEDPOS_.get() == 1:
			try:
				points = TrackedStars[stIndex].trackedPos[max(CurrentFile - 4, 0):CurrentFile + 1]
				poly = Polygon(points , closed = False, fill = False, edgecolor = "w", linewidth = 2)
				poly.label = "Poly"+str(stIndex)
				axis.add_artist(poly)
			except:
				pass
		rect_pos = (trackPos[0] - ts.star.radius, trackPos[1] - ts.star.radius)
		rect = Rectangle(rect_pos, ts.star.radius *2, ts.star.radius *2, edgecolor = col, facecolor='none')
		rect.label = "Rect"+str(stIndex)
		axis.add_artist(rect)
		text_pos = (trackPos[0], trackPos[1] - ts.star.radius - 6)
		text = axis.annotate(ts.star.name, text_pos, color=col, weight='bold',fontsize=6, ha='center', va='center')
		text.label = "Text"+str(stIndex)
		stIndex += 1
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
	canvas.draw_idle() # force re-draw

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
	canvas.draw_idle()
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
			canvas.draw_idle() # fo

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
	canvas.draw_idle()

def OnMouseRelase(event):
	global MousePress, SelectedTrack
	
	ItemList = DataManager.FileItemList
	
	MousePress = None

	if SelectedTrack == -100:
		if z_box is not None:
			setp(z_box, alpha = 0.5)
			setp(z_box, edgecolor = None)
		canvas.draw_idle()
		return


	if CurrentFile in TrackedStars[SelectedTrack].lostPoints:
		TrackedStars[SelectedTrack].lostPoints.remove(CurrentFile)
	if DataManager.RuntimeEnabled == True:
		try:
			data = RuntimeAnalysis.filesList[CurrentFile].data
			UpdateSidebar(data)
			if Results.MagData is not None:
				Results.MagData[CurrentFile, SelectedTrack] = Results.GetMagnitude(data, TrackedStars[SelectedTrack], Results.Constant,  CurrentFile, GetBackgroundMean(data))
		except:
			pass
	else:
		UpdateSidebar(ItemList[CurrentFile].data)

	SelectedTrack = -1
	for a in axis.artists:
		if a.label != "Poly":
			setp(a, linewidth = 1)
	canvas.draw_idle()

def NextFile(ItemList, stars):
	global CurrentFile
	if CurrentFile + 1 >= len(ItemList):
		return
	CurrentFile += 1
	UpdateSidebar(ItemList[CurrentFile].data)
	implot.set_array(ItemList[CurrentFile].data)
	UpdateCanvasOverlay(stars, CurrentFile)
	FileLabel.config(text = "Imagen: "+ basename(ItemList[CurrentFile].path))

def PrevFile(ItemList, stars):
	global CurrentFile
	if CurrentFile - 1 < 0:
		return
	CurrentFile -= 1
	UpdateSidebar(ItemList[CurrentFile].data)
	implot.set_array(ItemList[CurrentFile].data)
	UpdateCanvasOverlay(stars, CurrentFile)
	FileLabel.config(text = "Imagen: "+ basename(ItemList[CurrentFile].path))
