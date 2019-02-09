# coding=utf-8

from astropy.io import fits
import numpy
from matplotlib import use, figure
use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle, Polygon
import Tkinter as tk
import ttk
from os.path import basename
from STCore.item.Track import TrackItem
from STCore.utils.backgroundEstimator import GetBackground
import STCore.Results
import STCore.DataManager
from threading import Thread, Lock
from time import sleep
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
lock = Lock()
#endregion
def Awake(root, stars, ItemList, brightness):
	global TrackerFrame, TitleLabel, ImgFrame, TrackedStars, pool, BrightestStar
	STCore.DataManager.CurrentWindow = 3
	TrackerFrame = tk.Frame(root)
	TrackerFrame.pack(fill = tk.BOTH, expand = 1)
	TitleLabel = tk.Label(TrackerFrame, text = "Analizando imagen..")
	TitleLabel.pack(fill = tk.X)
	ImgFrame = tk.Frame(TrackerFrame)
	ImgFrame.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
	brightestStarValue = 0
	for s in stars:
		if s.value > brightestStarValue:
			BrightestStar = s
			brightestStarValue = s.value
	CreateCanvas(ItemList[0].data, brightness)
	CreateSidebar(root, ItemList)
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

def CreateSidebar(root, ItemList):
	import STCore.ImageView
	global TrackerFrame, SidebarList, Sidebar
	Sidebar = tk.LabelFrame(TrackerFrame, width = 400, text = "Detalles de análisis")
	Sidebar.pack(side = tk.RIGHT, expand = True, fill = tk.BOTH, anchor = tk.NE)
	
	SidebarList = tk.Frame(Sidebar)
	SidebarList.pack(expand = 1, fill = tk.X, anchor = tk.NW)
	
	cmdBack = lambda: (Destroy(), STCore.ImageView.Awake(root, ItemList))
	cmdNext = lambda: (Destroy(), STCore.Results.Awake(root, ItemList, GetTrackedStars()))

	buttonsFrame = tk.Frame(Sidebar, width = 400)
	buttonsFrame.pack(anchor = tk.S, expand = 1, fill = tk.X)
	ttk.Button(buttonsFrame, text = "Volver", command = cmdBack).grid(row = 0, column = 0, sticky = tk.EW)
	ttk.Button(buttonsFrame, text = "Continuar", command = cmdNext).grid(row = 0, column = 1, sticky = tk.EW)

def GetTrackedStars():
	global TrackedStars
	return TrackedStars

def UpdateSidebar(data, stars):
	global SidebarList
	index = 0
	with lock:
		for track in TrackedStars:
			frame = tk.LabelFrame(SidebarList)
			frame.pack(fill = tk.X, anchor = tk.N)
			tk.Label(frame, text = track.star.name,font="-weight bold").grid(row = 0, column = 0,sticky = tk.W, columnspan = 2)
			tk.Label(frame, text = "Pos: " + str(track.currPos), width = 12).grid(row = 1, column = 0,sticky = tk.W)
			tk.Label(frame, text = "Brillo: " + str(track.currValue), width = 9).grid(row = 1, column = 1,sticky = tk.W)
			tk.Label(frame, text = "Rastreados: " + str(len(track.trackedPos) - len(track.lostPoints)), width = 15).grid(row = 2, column = 0,sticky = tk.W)
			tk.Label(frame, text = "Perdidos: " + str(len(track.lostPoints)), width = 15).grid(row = 2, column = 1,sticky = tk.W)
			clipLoc = numpy.clip(track.currPos, stars[index].radius, (data.shape[0] - stars[index].radius, data.shape[1] - stars[index].radius))
			crop = data[clipLoc[0]-stars[index].radius : clipLoc[0]+stars[index].radius,clipLoc[1]-stars[index].radius : clipLoc[1]+stars[index].radius].astype(float)
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

def CreateCanvas(data, brightness):
	global ImgCanvas, ImgFrame, Img, ImgAxis
	fig = figure.Figure(figsize = (7,4), dpi = 100)
	ImgAxis = fig.add_subplot(111)
	Img = ImgAxis.imshow(data, cmap="gray", vmax = brightness)
	ImgCanvas = FigureCanvasTkAgg(fig,master=ImgFrame)
	ImgCanvas.draw()
	wdg = ImgCanvas.get_tk_widget()
	wdg.pack(fill=tk.BOTH, expand=1)
	wdg.wait_visibility()

def OnFinishTrack():
	STCore.DataManager.TrackItemList = TrackedStars

def UpdateTrack(ItemList, stars, index = 0):
	global TrackedStars, SidebarList
	if index >= len(ItemList):
		OnFinishTrack()
		for ts in TrackedStars:
			ts.PrintData()
		return
	Img.set_array(ItemList[index].data)
	trackThread = Thread(target = Track, args = (index,ItemList, stars))
	trackThread.start()
	trackThread.join()
	#Track(index,ItemList, stars)	
	UpdateCanvasOverlay(stars, index, ItemList[index].data)
	for child in SidebarList.winfo_children():
		child.destroy()
	updsThread = Thread(target = UpdateSidebar, args = (ItemList[index].data, stars))
	updsThread.start()
	updsThread.join()
	#UpdateSidebar(ItemList[index].data, stars)
	TitleLabel.config(text = "Analizando imagen: "+ basename(ItemList[index].path))
	TrackerFrame.after(50, lambda: UpdateTrack(ItemList, stars, index + 1))

def UpdateCanvasOverlay(stars, ImgIndex, data):
	for a in reversed(ImgAxis.artists):
		a.remove()
	for t in reversed(ImgAxis.texts):
		t.remove()
	stIndex = 0
	for s in stars:
		trackPos = TrackedStars[stIndex].currPos
		col = "w"
		if len(trackPos) == 0:
			continue
		if TrackedStars[stIndex].lastSeen != -1:
			col = "r"
		points = TrackedStars[stIndex].trackedPos[-4:]
		poly = Polygon(points , closed = False, fill = False, edgecolor = "w", linewidth = 2)
		rect_pos = (trackPos[1] - s.radius, trackPos[0] - s.radius)
		rect = Rectangle(rect_pos, s.radius *2, s.radius *2, edgecolor = col, facecolor='none')
		ImgAxis.add_artist(rect)
		ImgAxis.add_artist(poly)
		text_pos = (trackPos[1], trackPos[0] - s.radius - 6)
		ImgAxis.annotate(s.name, text_pos, color=col, weight='bold',fontsize=6, ha='center', va='center')
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
		if BrightestStar != s:
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
