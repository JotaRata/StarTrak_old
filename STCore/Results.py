import Tkinter as tk
import ttk
from matplotlib import figure, use
use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy
import STCore.DataManager
from STCore.utils.backgroundEstimator import GetBackground
import math
from os.path import basename
#region  Variables
ResultsFrame = None

#endregion


def Awake(root, ItemList, TrackedStars):
	global ResultsFrame
	STCore.DataManager.CurrentWindow = 4
	ResultsFrame = tk.Frame(root)
	ResultsFrame.pack(fill = tk.BOTH, expand = 1)
	CreateCanvas(ResultsFrame, ItemList, TrackedStars)
	
def tempo(ItemList):
	t=[]
	for i in range(len(ItemList)):
		t.append(ItemList[i].timee)
	return sorted(t)	

def GetConstant(data, TrackedStars, index, StarIndex, Ref):
	track = TrackedStars[StarIndex]
	pos = list(reversed(track.trackedPos[index]))
	radius = track.star.radius
	#data = ItemList[0].data
	clipLoc = numpy.clip(pos, radius, (data.shape[0] - radius, data.shape[1] - radius))
	crop = data[clipLoc[0]-radius : clipLoc[0]+radius,clipLoc[1]-radius : clipLoc[1]+radius]
	Backdata = GetBackground(data)
	RefFlux = numpy.sum(crop)
	BackgroundFlux = Backdata[0] * 4 * (radius **2)
	print RefFlux, BackgroundFlux
	value = Ref + 2.5 * numpy.log10(RefFlux - BackgroundFlux)
	return value, BackgroundFlux, RefFlux


def CreateCanvas(app, ItemList, TrackedStars):
	viewer = tk.Frame(app, width = 700, height = 400, bg = "white")
	viewer.pack(side=tk.LEFT, fill = tk.BOTH, expand = True, anchor = tk.W)
	fig = figure.Figure(figsize = (7,4), dpi = 100)
	ax = fig.add_subplot(111)
	XAxis = range(len(ItemList))
	#Xlabel= []
	wack=tempo(ItemList)
	Constant, BackgroundFlux, StarFlux = GetConstant(ItemList[0].data, TrackedStars, 0, 1, 13.5)
	#for item in ItemList:
	#	Xlabel.append(basename(item.path))
	Xlabel=wack
	i = 0
	while i < len(TrackedStars):
		YAxis = GetTrackedValue(ItemList, TrackedStars, i, Constant, BackgroundFlux, StarFlux)
		Plot = ax.scatter(XAxis, YAxis, label = TrackedStars[i].star.name)
		i += 1
	ax.legend()
	ax.set_xticks(XAxis)
	ax.set_xticklabels(Xlabel)
	for tick in ax.get_xticklabels():
		tick.set_rotation(90)
	ax.invert_yaxis()	
	ax.grid(axis = "y")
	PlotCanvas = FigureCanvasTkAgg(fig,master=viewer)
	PlotCanvas.draw()
	PlotCanvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
	return PlotCanvas

def GetTrackedValue(ItemList, TrackedStars, Trackindex, Constant, BackgroundFlux, RefFlux):
	values=[]
	index = 0
	Track = TrackedStars[Trackindex]
	radius = Track.star.radius
	while index < len(ItemList):
		pos = list(reversed(Track.trackedPos[index]))
		data = ItemList[index].data
		clipLoc = numpy.clip(pos, radius, (data.shape[0] - radius, data.shape[1] - radius))
		crop = data[clipLoc[0]-radius : clipLoc[0]+radius,clipLoc[1]-radius : clipLoc[1]+radius]
		Backdata = GetBackground(data)
		StarFlux = numpy.sum(crop)
		BackgroundFlux = Backdata[0] * 4 * (radius **2)
		values.append(Constant - 2.5 * numpy.log10(StarFlux - BackgroundFlux))
		index += 1
	return values

def Destroy():
	ResultsFrame.destroy()

def GetMaxima(crop, value):
	return numpy.max(crop)
	crap = crop.flatten()
	return crap[numpy.abs(-crap + value).argmin()]
