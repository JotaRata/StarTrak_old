from astropy.io import fits
import numpy
from matplotlib import use, figure
use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle
import Tkinter as tk
import ttk
from time import sleep
from os.path import basename
from STCore.item.Track import TrackItem
from STCore.utils.backgroundEstimator import GetBackground
#region Variables
TrackerFrame = None
TitleLabel = None
ImgFrame = None
ImgCanvas = None
Img = None
ImgAxis = None
TrackedStars = []
#endregion
def Awake(root, stars, ItemList):
	global TrackerFrame, TitleLabel, ImgFrame, TrackedStars
	TrackerFrame = tk.Frame(root)
	TrackerFrame.pack(fill = tk.BOTH, expand = 1)
	TitleLabel = tk.Label(TrackerFrame, text = "Analizando imagen..")
	TitleLabel.pack(fill = tk.X)
	ImgFrame = tk.Frame(TrackerFrame)
	ImgFrame.pack(fill = tk.BOTH, expand = 1)
	for s in stars:
		item = TrackItem()
		item.lastValue = s.value
		item.currPos = s.location
		TrackedStars.append(item)

	CreateCanvas(ItemList[0].data)
	UpdateTrack(ItemList, stars)
def CreateCanvas(data):
	global ImgCanvas, ImgFrame, Img, ImgAxis
	fig = figure.Figure(figsize = (7,4), dpi = 100)
	ImgAxis = fig.add_subplot(111)
	Img = ImgAxis.imshow(data, cmap="gray")
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
	Track(ItemList[index].data, stars, TrackedStars, index, 600)
	UpdateCanvasOverlay(stars, index, TrackedStars)
	TitleLabel.config(text = "Analizando imagen: "+ basename(ItemList[index].path))
	TrackerFrame.after(500, lambda: UpdateTrack(ItemList, stars, index + 1))

def UpdateCanvasOverlay(stars, ImgIndex, tracks):
	# Copiado de ImageViewer
	for a in reversed(ImgAxis.artists):
		a.remove()
	for t in reversed(ImgAxis.texts):
		t.remove()
	stIndex = 0
	for s in stars:
		trackPos = tracks[stIndex].currPos
		col = "w"
		if len(trackPos) == 0:
			continue
		if tracks[stIndex].lastSeen != -1:
			col = "r"
		rect_pos = (trackPos[1] - s.radius, trackPos[0] - s.radius)
		rect = Rectangle(rect_pos, s.radius *2, s.radius *2, edgecolor = col, facecolor='none')
		ImgAxis.add_artist(rect)
		text_pos = (trackPos[1], trackPos[0] - s.radius * 2)
		ImgAxis.annotate(s.name, text_pos, color=col, weight='bold',fontsize=6, ha='center', va='center')
		stIndex += 1
	ImgCanvas.draw()

def Track(data, stars, Tracks, fileIndex, sigma = 3):
	starIndex = 0
	back =  GetBackground(data)
	for s in stars:
		DataNoBG = numpy.clip(data - back, 0, numpy.max(data))
		SearchIndices = numpy.swapaxes(numpy.array(numpy.where(numpy.abs(-DataNoBG + Tracks[starIndex].lastValue) < sigma) and numpy.where(DataNoBG > 100)), 0, 1)
		RegPositions = numpy.empty((0,2), int)
		i = 0
		while i < SearchIndices.shape[0]:
			if abs(SearchIndices[i,0] -  Tracks[starIndex].currPos[0]) < s.radius and abs(SearchIndices[i,1] -  Tracks[starIndex].currPos[1]) < s.radius:
				_ind = numpy.atleast_2d(SearchIndices[i,:])
				RegPositions = numpy.append(RegPositions, _ind, axis = 0)
			i += 1
		if len(RegPositions) != 0:
			MeanPos = numpy.mean(RegPositions, axis = 0)
			Tracks[starIndex].currPos = MeanPos
			Tracks[starIndex].lastPos = MeanPos
			Tracks[starIndex].lastValue = GetMaxima(data, int(MeanPos[0]), int(MeanPos[1]), s.radius)
			Tracks[starIndex].trackedPos.append(MeanPos)
			if Tracks[starIndex].lastSeen != -1:
				Tracks[starIndex].lastSeen = -1
		else:
			if Tracks[starIndex].lastSeen == -1:
				Tracks[starIndex].lastSeen = fileIndex
			Tracks[starIndex].trackedPos.append(numpy.array([]))
		starIndex += 1

# Copiado de SetStar
def GetMaxima(data, xloc, yloc, radius):
	vloc = numpy.clip((xloc,yloc), radius, (data.shape[0] - radius, data.shape[1] - radius))
	return  numpy.max(data[vloc[0]-radius : vloc[0]+radius,vloc[1]-radius : vloc[1]+radius])
