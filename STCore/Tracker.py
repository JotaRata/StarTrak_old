# coding=utf-8

from astropy.io import fits
import numpy
from matplotlib import use, figure
use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle, Polygon
from matplotlib.artist import setp
import Tkinter as tk
import ttk
from os.path import basename
from STCore.item.Track import TrackItem
from STCore.utils.backgroundEstimator import GetBackground
import STCore.Results
import STCore.DataManager
from threading import Thread, Lock
from time import sleep, time
from functools import partial
from PIL import Image, ImageTk
import tkMessageBox

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
lock = Lock()

TrackFinished = False
SelectedTrack = -1
MousePress = None
CurrentFile = 0
#endregion
def Awake(root, stars, ItemList, brightness):
	global TrackerFrame, TitleLabel, ImgFrame, TrackedStars, pool, BrightestStar, CurrentFile
	STCore.DataManager.CurrentWindow = 3
	TrackerFrame = tk.Frame(root)
	TrackerFrame.pack(fill = tk.BOTH, expand = 1)
	TitleFrame = tk.Frame(TrackerFrame)
	TitleFrame.pack(fill = tk.X)
	TitleLabel = tk.Label(TitleFrame, text = "Analizando imagen..")
	TitleLabel.pack(fill = tk.X)
	tk.Button(TitleFrame, text = "<", command = lambda: PrevFile(ItemList, stars)).pack(side = tk.LEFT)
	tk.Button(TitleFrame, text = ">", command = lambda: NextFile(ItemList, stars)).pack(side = tk.RIGHT)
	ImgFrame = tk.Frame(TrackerFrame)
	ImgFrame.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
	CurrentFile = 0
	if (len(TrackedStars) > 0 and DataChanged):
		tkMessageBox.showwarning("Aviso", "La lista de estrellas ha sido modificada\nNo se podrán usar los datos de rastreo anteriores.")
		TrackedStars = []
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
			TrackedStars.append(item)
	CreateCanvas(ItemList,stars, brightness)
	CreateSidebar(root, ItemList, stars)
	UpdateSidebar(ItemList[CurrentFile].data, stars)
	UpdateCanvasOverlay(stars, CurrentFile)
	Img.set_array(ItemList[CurrentFile].data)

def UpdateImage():
	global Img
	Img.set_cmap(STCore.ImageView.ColorMaps[STCore.Settings._VISUAL_COLOR_.get()])
	Img.set_norm(STCore.ImageView.Modes[STCore.Settings._VISUAL_MODE_.get()])
	ImgCanvas.draw_idle()

def StartTracking(ItemList, stars):
	global TrackedStars
	if (len(TrackedStars) > 0 and tkMessageBox.askyesno("Confirmar sobreescritura", "Ya existen datos de rastreo, desea sobreescribirlos?")) or len(TrackedStars) == 0:
		TrackedStars =[]
		for s in stars:
			item = TrackItem()
			item.star = s
			item.lastValue = s.value
			item.currPos = s.location
			TrackedStars.append(item)
		UpdateTrack(ItemList, stars)

def Destroy():
	global TrackedStars, Img, ImgAxis
	print len(TrackedStars)
	TrackerFrame.destroy()
	Img = None
	ImgAxis = None

def CreateSidebar(root, ItemList, stars):
	import STCore.ImageView
	global TrackerFrame, SidebarList, Sidebar
	Sidebar = tk.LabelFrame(TrackerFrame, width = 400, text = "Detalles de análisis")
	Sidebar.pack(side = tk.RIGHT, expand = True, fill = tk.BOTH, anchor = tk.NE)
	
	SidebarList = tk.Frame(Sidebar)
	SidebarList.pack(expand = 1, fill = tk.X, anchor = tk.NW)
	
	cmdBack = lambda: (Destroy(), STCore.ImageView.Awake(root, ItemList))
	cmdNext = lambda: Apply(root, ItemList)
	cmdTrack = lambda: StartTracking(ItemList, stars)

	buttonsFrame = tk.Frame(Sidebar, width = 400)
	buttonsFrame.pack(anchor = tk.S, expand = 1, fill = tk.X)
	ttk.Button(buttonsFrame, text = "Volver", command = cmdBack).grid(row = 0, column = 0, sticky = tk.EW)
	ttk.Button(buttonsFrame, text = "Iniciar", command = cmdTrack).grid(row = 0, column = 1, sticky = tk.EW)
	ttk.Button(buttonsFrame, text = "Continuar", command = cmdNext).grid(row = 0, column = 2, sticky = tk.EW)

def Apply(root, ItemList):
	if len(TrackedStars) > 0:
		Destroy()
		STCore.Results.Awake(root, ItemList, TrackedStars)
	else:
		tkMessageBox.showerror("Error", "No hay estrellas restreadas.")

def UpdateSidebar(data, stars):
	global SidebarList
	index = 0
	for child in SidebarList.winfo_children():
		child.destroy()
	for track in TrackedStars:
		frame = tk.Frame(SidebarList)
		frame.pack(fill = tk.X, anchor = tk.N)
		tk.Label(frame, text = track.star.name,font="-weight bold").grid(row = 0, column = 0,sticky = tk.W, columnspan = 2)
		tk.Label(frame, text = "Pos: " + str(track.currPos), width = 12).grid(row = 1, column = 0,sticky = tk.W)
		tk.Label(frame, text = "Brillo: " + str(track.currValue), width = 9).grid(row = 1, column = 1,sticky = tk.W)
		tk.Label(frame, text = "Rastreados: " + str(len(track.trackedPos) - len(track.lostPoints)), width = 15).grid(row = 2, column = 0,sticky = tk.W)
		tk.Label(frame, text = "Perdidos: " + str(len(track.lostPoints)), width = 15).grid(row = 2, column = 1,sticky = tk.W)
		clipLoc = (track.currPos[1], track.currPos[0])
		if len(track.trackedPos) > 0:
			clipLoc = numpy.clip(track.trackedPos[CurrentFile], stars[index].radius, (data.shape[1] - stars[index].radius, data.shape[0] - stars[index].radius))
		crop = data[clipLoc[1]-stars[index].radius : clipLoc[1]+stars[index].radius,clipLoc[0]-stars[index].radius : clipLoc[0]+stars[index].radius].astype(float)
		minv = numpy.min(crop)
		maxv = numpy.max(crop)
		noisy = numpy.clip(255 * (crop - minv) / (maxv - minv), 0 , 255).astype(numpy.uint8)	
		Pic = Image.fromarray(noisy, mode='L')
		Pic = Pic.resize((50, 50))
		Img = ImageTk.PhotoImage(Pic)
		ImageLabel = tk.Label(frame, image = Img, width = 50, height = 50)
		ImageLabel.image = Img
		ImageLabel.grid(row = 0, column = 2, columnspan = 1, rowspan = 3, padx = 20)
		index += 1

def CreateCanvas(ItemList, stars, brightness):
	global ImgCanvas, ImgFrame, Img, ImgAxis
	fig = figure.Figure(figsize = (7,4), dpi = 100)
	data = ItemList[CurrentFile].data
	ImgAxis = fig.add_subplot(111)
	Img = ImgAxis.imshow(data, vmin = numpy.min(data), vmax = brightness, cmap=STCore.ImageView.ColorMaps[STCore.Settings._VISUAL_COLOR_.get()], norm = STCore.ImageView.Modes[STCore.Settings._VISUAL_MODE_.get()])
	ImgCanvas = FigureCanvasTkAgg(fig,master=ImgFrame)
	if STCore.Settings._SHOW_GRID_.get() == 1:
		ImgAxis.grid()
	ImgCanvas.draw()
	ImgCanvas.mpl_connect("button_press_event", OnMousePress) 
	ImgCanvas.mpl_connect("motion_notify_event", OnMouseDrag) 
	ImgCanvas.mpl_connect("button_release_event", lambda event: OnMouseRelase(event, stars, ItemList)) 
	wdg = ImgCanvas.get_tk_widget()
	wdg.config(cursor = "fleur")
	wdg.pack(fill=tk.BOTH, expand=1)
	wdg.wait_visibility()

def OnFinishTrack():
	STCore.DataManager.TrackItemList = TrackedStars

def UpdateTrack(ItemList, stars, index = 0):
	global TrackedStars, SidebarList, CurrentFile
	if index >= len(ItemList):
		OnFinishTrack()
		for ts in TrackedStars:
			ts.PrintData()
		return
	CurrentFile = index
	Img.set_array(ItemList[index].data)
	trackThread = Thread(target = Track, args = (index,ItemList, stars))
	trackThread.start()
	trackThread.join()
	#Track(index,ItemList, stars)	
	UpdateCanvasOverlay(stars, index)
	UpdateSidebar(ItemList[index].data, stars)
	#updsThread = Thread(target = UpdateSidebar, args = (ItemList[index].data, stars))
	#updsThread.start()
	#updsThread.join()
	#UpdateSidebar(ItemList[index].data, stars)
	TitleLabel.config(text = "Analizando imagen: "+ basename(ItemList[index].path))
	TrackerFrame.after(50, lambda: UpdateTrack(ItemList, stars, index + 1))

def UpdateCanvasOverlay(stars, ImgIndex):
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
		if len(trackPos) == 0:
			continue
		if TrackedStars[stIndex].lastSeen != -1:
			col = "r"
		if STCore.Settings._SHOW_TRACKEDPOS_.get() == 1:
			points = TrackedStars[stIndex].trackedPos[max(ImgIndex - 4, 0):ImgIndex + 1]
			poly = Polygon(points , closed = False, fill = False, edgecolor = "w", linewidth = 2)
			poly.aname = "Poly"+str(stIndex)
			ImgAxis.add_artist(poly)
		rect_pos = (trackPos[0] - s.radius, trackPos[1] - s.radius)
		rect = Rectangle(rect_pos, s.radius *2, s.radius *2, edgecolor = col, facecolor='none')
		rect.aname = "Rect"+str(stIndex)
		ImgAxis.add_artist(rect)
		text_pos = (trackPos[0], trackPos[1] - s.radius - 6)
		text = ImgAxis.annotate(s.name, text_pos, color=col, weight='bold',fontsize=6, ha='center', va='center')
		text.aname = "Text"+str(stIndex)
		stIndex += 1
	ImgCanvas.draw()

def Track(index, ItemList, stars):
	global TrackedStars, BrightestStar
	#starIndex = 0
	data = ItemList[index].data
	back, bgStD =  GetBackground(data)
	deltaPos = numpy.array([0,0])
	indexes = range(len(stars))
	for starIndex in sorted(indexes, key = lambda e: stars[e].value, reverse = True):
		s = stars[starIndex]
		Pos = numpy.array(TrackedStars[starIndex].currPos)
		clipLoc = numpy.clip(Pos, s.bounds, (data.shape[0] - s.bounds, data.shape[1] - s.bounds))
		if BrightestStar != s and STCore.Settings._TRACK_PREDICTION_.get() == 1:
			clipLoc = numpy.clip(Pos + deltaPos, s.bounds, (data.shape[0] - s.bounds, data.shape[1] - s.bounds))
		crop = data[clipLoc[0]-s.bounds : clipLoc[0]+s.bounds,clipLoc[1]-s.bounds : clipLoc[1]+s.bounds]
		#indices = numpy.where((numpy.abs(-crop + s.value) < s.threshold) & (crop > bgStD*2 + back))
		indices = numpy.unravel_index(numpy.flatnonzero((numpy.abs(-crop + s.value) < s.threshold) & (crop > bgStD*2 + back)),crop.shape)
		SearchIndices = numpy.swapaxes(numpy.array(indices), 0, 1)
		RegPositions = numpy.empty((0,2), int)
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
			TrackedStars[starIndex].currValue = GetMaxima(data, int(MeanPos[0]), int(MeanPos[1]), s.radius, s.value)
			TrackedStars[starIndex].trackedPos.append(list(reversed(TrackedStars[starIndex].currPos)))
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
def GetMaxima(data, xloc, yloc, radius, value):
	clipLoc = numpy.clip((xloc,yloc), radius, (data.shape[0] - radius, data.shape[1] - radius))
	crop = data[clipLoc[0]-radius : clipLoc[0]+radius,clipLoc[1]-radius : clipLoc[1]+radius].flatten()
	return crop[numpy.abs(-crop + value).argmin()]
	#return  numpy.max(data[vloc[0]-radius : vloc[0]+radius,vloc[1]-radius : vloc[1]+radius])
MousePressTime=0
def OnMousePress(event):
	global ImgCanvas, MousePress, SelectedTrack, ImgAxis, MousePressTime
	if time() - MousePressTime < 0.2:
		return
	for a in ImgAxis.artists:
		if a.aname != "Poly":
			contains, attrd = a.contains(event)
			if contains:
				tup = a.xy
				x0, y0 = tup[0], tup[1]
				MousePress = x0, y0, event.xdata, event.ydata
				SelectedTrack = int(filter(str.isdigit, a.aname)[0])
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
	sel = filter(lambda obj: obj.aname == "Rect"+str(SelectedTrack), ImgAxis.artists)
	text = filter(lambda obj: obj.aname == "Text"+str(SelectedTrack), ImgAxis.texts)
	if len(sel) > 0 and len(text) > 0:
		sel[0].set_x(x0+dx)
		sel[0].set_y(y0+dy)
		text[0].set_x(x0 + dx + TrackedStars[SelectedTrack].star.radius)
		text[0].set_y(y0 - TrackedStars[SelectedTrack].star.radius + 6 +dy)
		TrackedStars[SelectedTrack].trackedPos[CurrentFile][1] = int(y0 + dy)
		TrackedStars[SelectedTrack].trackedPos[CurrentFile][0] = int(x0 + dx)
	poly = filter(lambda obj: obj.aname == "Poly"+str(SelectedTrack), ImgAxis.artists)[0]
	poly.set_xy(TrackedStars[SelectedTrack].trackedPos[max(CurrentFile - 4, 0):CurrentFile + 1])
	ImgCanvas.draw()

def OnMouseRelase(event, stars, ItemList):
	global MousePress, SelectedTrack
	UpdateSidebar(ItemList[CurrentFile].data, stars)
	MousePress = None
	SelectedTrack = -1
	ImgCanvas.draw()
	for a in ImgAxis.artists:
		if a.aname != "Poly":
			setp(a, linewidth = 1)
	ImgCanvas.draw()

def NextFile(ItemList, stars):
	global CurrentFile
	if CurrentFile + 1 > len(ItemList):
		return
	CurrentFile += 1
	UpdateSidebar(ItemList[CurrentFile].data, stars)
	Img.set_array(ItemList[CurrentFile].data)
	UpdateCanvasOverlay(stars, CurrentFile)
	TitleLabel.config(text = "Analizando imagen: "+ basename(ItemList[CurrentFile].path))
	print CurrentFile

def PrevFile(ItemList, stars):
	global CurrentFile
	if CurrentFile - 1 < 0:
		return
	CurrentFile -= 1
	UpdateSidebar(ItemList[CurrentFile].data, stars)
	Img.set_array(ItemList[CurrentFile].data)
	UpdateCanvasOverlay(stars, CurrentFile)
	TitleLabel.config(text = "Analizando imagen: "+ basename(ItemList[CurrentFile].path))
	print CurrentFile