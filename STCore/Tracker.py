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
#from multiprocessing import Pool
#from threading import Lock
from time import sleep
from functools import partial
#region Variables
TrackerFrame = None
TitleLabel = None
ImgFrame = None
ImgCanvas = None
Img = None
ImgAxis = None
TrackedStars = []
#endregion
def Awake(root, stars, ItemList, brightness):
	global TrackerFrame, TitleLabel, ImgFrame, TrackedStars, pool
	TrackerFrame = tk.Frame(root)
	TrackerFrame.pack(fill = tk.BOTH, expand = 1)
	TitleLabel = tk.Label(TrackerFrame, text = "Analizando imagen..")
	TitleLabel.pack(fill = tk.X)
	ImgFrame = tk.Frame(TrackerFrame)
	ImgFrame.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
	for s in stars:
		item = TrackItem()
		item.name = s.name
		item.lastValue = s.value
		item.currPos = s.location
		TrackedStars.append(item)
	CreateCanvas(ItemList[0].data, brightness)
	CreateSidebar(root, ItemList)
	#map(partial(UpdateTrack, ItemList = ItemList, stars = stars), range(0, len(ItemList)))
	#CreatePools(ItemList, stars)
	UpdateTrack(ItemList, stars)
def Destroy():
	TrackerFrame.destroy()
	TrackedStars =[]

def CreateSidebar(root, ItemList):
	import STCore.ImageView
	global TrackerFrame
	sidebar = tk.Frame(TrackerFrame, width = 400)
	sidebar.pack(side = tk.RIGHT, expand = True, fill = tk.BOTH, anchor = tk.NE)

	cmd = lambda: (Destroy(), STCore.ImageView.Awake(root, ItemList))
	cmd2 = lambda: (Destroy(), STCore.ImageView.Awake(root, ItemList))

	buttonsFrame = tk.Frame(sidebar)
	buttonsFrame.pack(anchor = tk.S, expand = 1, fill = tk.X)
	ttk.Button(buttonsFrame, text = "Volver", command = cmd).grid(row = 0, column = 0, sticky = tk.EW)
	ttk.Button(buttonsFrame, text = "Continuar", command = cmd2).grid(row = 0, column = 1, sticky = tk.EW)

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

def UpdateTrack(ItemList, stars, index = 0):
	global TrackedStars
	if index >= len(ItemList):
		for ts in TrackedStars:
			ts.PrintData()
		return
	Img.set_array(ItemList[index].data)
	Track(index,ItemList, stars)	
	UpdateCanvasOverlay(stars, index, ItemList[index].data)
	TitleLabel.config(text = "Analizando imagen: "+ basename(ItemList[index].path))
	TrackerFrame.after(200, lambda: UpdateTrack(ItemList, stars, index + 1))

def UpdateCanvasOverlay(stars, ImgIndex, data):
	# Copiado de ImageViewer
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
		poly = Polygon(TrackedStars[stIndex].trackedPos, closed = False, fill = False, edgecolor = "w", linewidth = 2)
		rect_pos = (trackPos[1] - s.radius, trackPos[0] - s.radius)
		rect = Rectangle(rect_pos, s.radius *2, s.radius *2, edgecolor = col, facecolor='none')
		ImgAxis.add_artist(rect)
		ImgAxis.add_artist(poly)
		text_pos = (trackPos[1], trackPos[0] - s.radius - 6)
		ImgAxis.annotate(s.name, text_pos, color=col, weight='bold',fontsize=6, ha='center', va='center')
		stIndex += 1
	ImgCanvas.draw()

def Track(index, ItemList, stars):
	global TrackedStars
	starIndex = 0
	data = ItemList[index].data
	back, bgStD =  GetBackground(data)
	for s in stars:
		Pos = TrackedStars[starIndex].currPos
		vloc = numpy.clip(Pos, s.bounds, (data.shape[0] - s.bounds, data.shape[1] - s.bounds))
		crop = data[vloc[0]-s.bounds : vloc[0]+s.bounds,vloc[1]-s.bounds : vloc[1]+s.bounds]
		#indices = numpy.where((numpy.abs(-data + s.value) < s.threshold) & (DataNoBG > 100))
		indices = numpy.unravel_index(numpy.flatnonzero((numpy.abs(-crop + s.value) < s.threshold) & (crop > bgStD + back)),crop.shape)
		SearchIndices = numpy.swapaxes(numpy.array(indices), 0, 1)
		RegPositions = numpy.empty((0,2), int)
		i = 0
		while i < SearchIndices.shape[0]:
			_ind = numpy.atleast_2d(SearchIndices[i,:]) + vloc - s.bounds
			RegPositions = numpy.append(RegPositions, _ind, axis = 0)
			i += 1
		if len(RegPositions) != 0:
			MeanPos = numpy.mean(RegPositions, axis = 0)
			TrackedStars[starIndex].currPos = (int(MeanPos[0]), int(MeanPos[1]))
			TrackedStars[starIndex].lastPos = (int(MeanPos[0]), int(MeanPos[1]))
			TrackedStars[starIndex].lastValue = GetMaxima(data, int(MeanPos[0]), int(MeanPos[1]), s.radius, s.value)
			TrackedStars[starIndex].trackedPos.append(list(reversed(TrackedStars[starIndex].lastPos)))
			if TrackedStars[starIndex].lastSeen != -1:
				TrackedStars[starIndex].lastSeen = -1
		else:
			if TrackedStars[starIndex].lastSeen == -1:
				TrackedStars[starIndex].lastSeen = index
			TrackedStars[starIndex].lostPoints.append(index)
			TrackedStars[starIndex].trackedPos.append(list(reversed(TrackedStars[starIndex].lastPos)))
		print TrackedStars[starIndex].lastValue
		starIndex += 1
	#sleep(0.1)
# Copiado de SetStar
def GetMaxima(data, xloc, yloc, radius, value):
	vloc = numpy.clip((xloc,yloc), radius, (data.shape[0] - radius, data.shape[1] - radius))
	crop = data[vloc[0]-radius : vloc[0]+radius,vloc[1]-radius : vloc[1]+radius].flatten()
	return crop[numpy.abs(-crop + value).argmin()]
	#return  numpy.max(data[vloc[0]-radius : vloc[0]+radius,vloc[1]-radius : vloc[1]+radius])
