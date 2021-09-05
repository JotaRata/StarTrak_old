# coding=utf-8

from STCore.item import ResultSettings
import numpy
from matplotlib import use, figure
use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle, Polygon
from matplotlib.artist import setp
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
ImgCanvas = None
Img = None
ImgAxis = None
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
	ttk.Button(TitleFrame, image = icons.Icons["prev"], command = ScrollFileLbd[0]).pack(side = tk.LEFT)
	ttk.Button(TitleFrame, image = icons.Icons["next"], command = ScrollFileLbd[1]).pack(side = tk.RIGHT)
	ImgFrame = ttk.Frame(TrackerFrame)
	ImgFrame.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
	CreateCanvas(ItemList,stars)
	CreateSidebar(root, ItemList, stars)
	Img.set_array(ItemList[CurrentFile].data)
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
	
	
	UpdateCanvasOverlay(stars, CurrentFile, BrightestStar)
	UpdateSidebar(ItemList[CurrentFile].data, stars)

def UpdateImage():
	global Img
	Img.set_cmap(STCore.ImageView.ColorMaps[STCore.Settings._VISUAL_COLOR_.get()])
	Img.set_norm(STCore.ImageView.Modes[STCore.Settings._VISUAL_MODE_.get()])
	ImgCanvas.draw_idle()

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
	global TrackedStars, Img, ImgAxis
	if STCore.DataManager.RuntimeEnabled == True:
			if STCore.ResultsConfigurator.CheckWindowClear() == False:
				STCore.ResultsConfigurator.PlotWindow.destroy()
	TrackerFrame.destroy()
	Img = None
	ImgAxis = None

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
	global ImgCanvas, ImgFrame, Img, ImgAxis, CurrentFile
	ImageFigure = figure.Figure(figsize = (7,4), dpi = 100)
	ImageFigure.set_facecolor("black")
	if CurrentFile >= len(ItemList):
		CurrentFile = 0

	data = ItemList[CurrentFile].data
	ImgAxis = ImageFigure.add_subplot(111)
	ImgAxis.set_axis_off()
	ImageFigure.subplots_adjust(0.01,0.01,0.99,1)
	levels = STCore.DataManager.Levels
	if  not isinstance(levels, tuple):
		#print "Tracker: not tuple!"
		levels = (numpy.max(data), numpy.min(data))
		STCore.DataManager.Levels = STCore.ImageView.Levels = levels
	Img = ImgAxis.imshow(data, vmin = levels[1], vmax = levels[0], cmap=STCore.ImageView.ColorMaps[STCore.Settings._VISUAL_COLOR_.get()], norm = STCore.ImageView.Modes[STCore.Settings._VISUAL_MODE_.get()])
	ImgCanvas = FigureCanvasTkAgg(ImageFigure,master=ImgFrame)
	if STCore.Settings._SHOW_GRID_.get() == 1:
		ImgAxis.grid()
	ImgCanvas.draw()
	ImgCanvas.mpl_connect("button_press_event", OnMousePress) 
	ImgCanvas.mpl_connect("motion_notify_event", OnMouseDrag) 
	ImgCanvas.mpl_connect("button_release_event", lambda event: OnMouseRelase(event, stars, ItemList)) 
	wdg = ImgCanvas.get_tk_widget()
	wdg.config(cursor = "fleur", bg="black")
	wdg.pack(fill=tk.BOTH, expand=1)
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
	Img.set_array(ItemList[index].data)

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
	for a in reversed(ImgAxis.artists):
		a.remove()
	for t in reversed(ImgAxis.texts):
		t.remove()
	stIndex = 0
	for s in stars:
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
				ImgAxis.add_artist(poly)
			except:
				pass
		rect_pos = (trackPos[0] - s.radius, trackPos[1] - s.radius)
		rect = Rectangle(rect_pos, s.radius *2, s.radius *2, edgecolor = col, facecolor='none')
		rect.label = "Rect"+str(stIndex)
		ImgAxis.add_artist(rect)
		text_pos = (trackPos[0], trackPos[1] - s.radius - 6)
		text = ImgAxis.annotate(s.name, text_pos, color=col, weight='bold',fontsize=6, ha='center', va='center')
		text.label = "Text"+str(stIndex)
		stIndex += 1
	ImgCanvas.draw()

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


MousePressTime=0
def OnMousePress(event):
	global ImgCanvas, MousePress, SelectedTrack, ImgAxis, MousePressTime
	if time() - MousePressTime < 0.2:
		return
	for a in ImgAxis.artists:
		if a.label != "Poly":
			contains, attrd = a.contains(event)
			if contains:
				tup = a.xy
				x0, y0 = tup[0], tup[1]
				MousePress = x0, y0, event.xdata, event.ydata
				SelectedTrack = int("".join(next(filter(str.isdigit, a.label))))
				setp(a, linewidth = 4)
			else:
				setp(a, linewidth = 1)
	ImgCanvas.draw()
	MousePressTime = time()

def OnMouseDrag(event):
	global MousePress
	if MousePress is None or SelectedTrack == -1 or len(TrackedStars) == 0 or event.inaxes is  None: return
	x0, y0, xpress, ypress = MousePress
	dx = event.xdata - xpress
	dy = event.ydata - ypress
	sel = list(filter(lambda obj: obj.label == "Rect"+str(SelectedTrack), ImgAxis.artists))
	text = list(filter(lambda obj: obj.label == "Text"+str(SelectedTrack), ImgAxis.texts))
	if len(sel) > 0 and len(text) > 0:
		sel[0].set_x(x0+dx)
		sel[0].set_y(y0+dy)
		text[0].set_x(x0 + dx + TrackedStars[SelectedTrack].star.radius)
		text[0].set_y(y0 - TrackedStars[SelectedTrack].star.radius + 6 +dy)
		TrackedStars[SelectedTrack].trackedPos[CurrentFile][1] = int(y0 + dy + TrackedStars[SelectedTrack].star.radius)
		TrackedStars[SelectedTrack].trackedPos[CurrentFile][0] = int(x0 + dx+ TrackedStars[SelectedTrack].star.radius)
		TrackedStars[SelectedTrack].currPos = list(reversed(TrackedStars[SelectedTrack].trackedPos[CurrentFile]))
	poly = next(filter(lambda obj: obj.label == "Poly"+str(SelectedTrack), ImgAxis.artists))
	poly.set_xy(TrackedStars[SelectedTrack].trackedPos[max(CurrentFile - 4, 0):CurrentFile + 1])
	ImgCanvas.draw()

def OnMouseRelase(event, stars, ItemList):
	global MousePress, SelectedTrack
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
	UpdateCanvasOverlay(stars, CurrentFile)
	MousePress = None
	SelectedTrack = -1
	ImgCanvas.draw()
	for a in ImgAxis.artists:
		if a.label != "Poly":
			setp(a, linewidth = 1)
	ImgCanvas.draw()

def NextFile(ItemList, stars):
	global CurrentFile
	if CurrentFile + 1 >= len(ItemList):
		return
	CurrentFile += 1
	UpdateSidebar(ItemList[CurrentFile].data, stars)
	Img.set_array(ItemList[CurrentFile].data)
	UpdateCanvasOverlay(stars, CurrentFile)
	TitleLabel.config(text = "Analizando imagen: "+ basename(ItemList[CurrentFile].path))

def PrevFile(ItemList, stars):
	global CurrentFile
	if CurrentFile - 1 < 0:
		return
	CurrentFile -= 1
	UpdateSidebar(ItemList[CurrentFile].data, stars)
	Img.set_array(ItemList[CurrentFile].data)
	UpdateCanvasOverlay(stars, CurrentFile)
	TitleLabel.config(text = "Analizando imagen: "+ basename(ItemList[CurrentFile].path))
