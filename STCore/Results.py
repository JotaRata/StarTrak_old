import Tkinter as tk
import ttk
from matplotlib import figure, use
use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy
import STCore.DataManager
from STCore.utils.backgroundEstimator import GetBackground
#region  Variables
ResultsFrame = None

#endregion


def Awake(root, ItemList, TrackedStars):
	global ResultsFrame
	STCore.DataManager.CurrentWindow = 4
	ResultsFrame = tk.Frame(root)
	ResultsFrame.pack(fill = tk.BOTH, expand = 1)
	CreateCanvas(ResultsFrame, ItemList, TrackedStars)
	

def GetConstant(ItemList, TrackedStars, StarIndex, Ref):
	track = TrackedStars[StarIndex]
	pos = list(reversed(track.trackedPos[0]))
	radius = track.star.radius
	data = ItemList[0].data
	clipLoc = numpy.clip(pos, radius, (data.shape[0] - radius, data.shape[1] - radius))
	crop = data[clipLoc[0]-radius : clipLoc[0]+radius,clipLoc[1]-radius : clipLoc[1]+radius]
	StarFlux = numpy.sum(crop) / (radius ** 2)
	BackgroundFlux = GetBackground(data)[0]
	value = Ref + 2.5 * numpy.log10(StarFlux - BackgroundFlux)
	return value


def CreateCanvas(app, ItemList, TrackedStars):
	viewer = tk.Frame(app, width = 700, height = 400, bg = "white")
	viewer.pack(side=tk.LEFT, fill = tk.BOTH, expand = True, anchor = tk.W)
	fig = figure.Figure(figsize = (7,4), dpi = 100)
	ax = fig.add_subplot(111)
	XAxis = range(len(ItemList))

	c = GetConstant(ItemList, TrackedStars, 0, 0.0)

	for t in TrackedStars:
		YAxis = GetTrackedValue(ItemList, t.trackedPos, t.star.radius, c)
		Plot = ax.scatter(XAxis, YAxis)

	ax.invert_yaxis()	
	PlotCanvas = FigureCanvasTkAgg(fig,master=viewer)
	PlotCanvas.draw()
	PlotCanvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
	return PlotCanvas

def GetTrackedValue(ItemList, trackedPos, radius, Constant):
	values=[]
	index = 0
	while index < len(ItemList):
		pos = list(reversed(trackedPos[index]))
		data = ItemList[index].data
		clipLoc = numpy.clip(pos, radius, (data.shape[0] - radius, data.shape[1] - radius))
		crop = data[clipLoc[0]-radius : clipLoc[0]+radius,clipLoc[1]-radius : clipLoc[1]+radius]
		StarFlux = numpy.sum(crop) / (radius ** 2)
		BackgroundFlux = GetBackground(data)[0]
		values.append(Constant - 2.5 * numpy.log10(StarFlux - BackgroundFlux))
		index += 1
	return values

def Destroy():
	ResultsFrame.destroy()
