import Tkinter as tk
import ttk
from matplotlib import figure, use
use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy
import STCore.DataManager
from STCore.utils.backgroundEstimator import GetBackground
from STCore.utils.Exporter import *
import math
from os.path import basename
import STCore.ResultsConfigurator as Config
from time import sleep
from multiprocessing import Pool
#region  Variables
ResultsFrame = None

#endregion


def Awake(root, ItemList, TrackedStars):
	global ResultsFrame
	STCore.DataManager.CurrentWindow = 4
	ResultsFrame = tk.Frame(root)
	ResultsFrame.pack(fill = tk.BOTH, expand = 1)
	canvas = CreateCanvas(root, ResultsFrame, ItemList, TrackedStars)
	Sidebar = tk.Frame(ResultsFrame, width = 400)
	Sidebar.pack(side = tk.RIGHT, fill = tk.Y)
	cmdBack = lambda: (Destroy(), STCore.Tracker.Awake(root, STCore.ImageView.Stars, ItemList, STCore.ImageView.Brightness))
	
	Exportmenu = tk.Menu(root, tearoff=0)
	Exportmenu.add_command(label="Exportar grafico", command=lambda: ExportImage(canvas[1]))
	Exportmenu.add_command(label="Exportar datos", command=lambda: ExportData(TrackedStars, canvas[2], GetTimeLabel(ItemList)))
	Exportmenu.add_command(label="Exportar PDF", command=lambda: ExportPDF(canvas[1], canvas[2], TrackedStars))
	

	exportbutton = ttk.Button(Sidebar, text = "Exportar")
	exportbutton.bind("<Button-1>", lambda event: PopupMenu(event, Exportmenu))
	exportbutton.grid(row = 0, column = 0)

	ttk.Button(Sidebar, text = "Volver", command = cmdBack).grid(row = 1, column = 0)
	ttk.Button(Sidebar, text = "Configurar", command = lambda: STCore.ResultsConfigurator.Awake(root, ItemList, TrackedStars)).grid(row = 2, column = 0)
def PopupMenu(event, Menu):
	Menu.post(event.x_root, event.y_root)

def GetTimeLabel(ItemList):
	t=[]
	for i in range(len(ItemList)):
		t.append(ItemList[i].date)
	return t
def GetNameLabel(ItemList):
	t=[]
	for i in range(len(ItemList)):
		t.append(basename(ItemList[i].path))
	return t
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

def GetDateValue(ItemList):
	t=[]
	for i in range(len(ItemList)):
		ls = list(ItemList[i].date.split(":"))
		t.append(int(ls[0])*3600 + int(ls[1])*60 + int(ls[2]))
	return t
def GetNameValue(ItemList):
	t = range(len(ItemList))
	return t

def CreateCanvas(root, app, ItemList, TrackedStars):
	viewer = tk.Frame(app, width = 700, height = 400, bg = "white")
	viewer.pack(side=tk.LEFT, fill = tk.BOTH, expand = True, anchor = tk.W)
	fig = figure.Figure(figsize = (7,4), dpi = 100)
	ax = fig.add_subplot(111)
	progress = tk.DoubleVar()
	LoadBar = CreateLoadBar(root, progress)
	XAxis = []
	Xlabel = []
	if Config.SettingsObject.sortingMode == 0:
		XAxis = GetDateValue(ItemList)
		Xlabel=GetTimeLabel(ItemList)
	else:
		XAxis = GetNameValue(ItemList)
		Xlabel = GetNameLabel(ItemList)
	progress.set(20)
	sleep(0.01)
	#Xlabel= []
	Constant, BackgroundFlux, StarFlux = GetConstant(ItemList[0].data, TrackedStars, 0, 
												  max(Config.SettingsObject.refStar, 0), Config.SettingsObject.refValue)
	#for item in ItemList:
	#	Xlabel.append(basename(item.path))
	MagData = numpy.empty((0 ,len(ItemList)))
	i = 0
	while i < len(TrackedStars):
		YAxis = GetTrackedValue(ItemList, TrackedStars, i, Constant, BackgroundFlux, StarFlux)
		MagData = numpy.append(MagData, numpy.atleast_2d(numpy.array(YAxis)), 0)
		Plot = ax.scatter(XAxis, YAxis, label = TrackedStars[i].star.name)
		progress.set(20+80*float(i)/len(TrackedStars))
		LoadBar[0].update()
		sleep(0.01)
		i += 1
	print MagData.shape
	LoadBar[0].destroy()
	ax.legend()
	ticks = STCore.ResultsConfigurator.SettingsObject.tickNumber
	ax.set_xticks(XAxis[0::max(1, len(ItemList) / ticks)])
	ax.set_xticklabels(Xlabel[0::max(1, len(ItemList) / ticks)])
	for tick in ax.get_xticklabels():
		tick.set_rotation(30)
	ax.invert_yaxis()	
	ax.grid(axis = "y")
	PlotCanvas = FigureCanvasTkAgg(fig,master=viewer)
	PlotCanvas.draw()
	PlotCanvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
	return PlotCanvas, fig, MagData

def CreateLoadBar(root, progress, title = "Cargando.."):
	popup = tk.Toplevel()
	popup.geometry("300x60+%d+%d" % (root.winfo_width()/2,  root.winfo_height()/2) )
	popup.wm_title(string = title)
	popup.overrideredirect(1)
	pframe = tk.LabelFrame(popup)
	pframe.pack(fill = tk.BOTH, expand = 1)
	label = tk.Label(pframe, text="Analizando datos..")
	bar = ttk.Progressbar(pframe, variable=progress, maximum=100)
	label.pack()
	bar.pack(fill = tk.X)
	return popup, label, bar

def GetTrackedValue(ItemList, TrackedStars, Trackindex, Constant, BackgroundFlux, returnValue):
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
		mag = Constant - 2.5 * numpy.log10(StarFlux - BackgroundFlux)
		if STCore.ResultsConfigurator.SettingsObject.delLostTracks == 1 and index in Track.lostPoints:
			mag = numpy.nan
		values.append(mag)
		index += 1
	returnValue = values   # para usar return en un proceso
	return values

def Destroy():
	ResultsFrame.destroy()

def GetMaxima(crop, value):
	return numpy.max(crop)
	crap = crop.flatten()
	return crap[numpy.abs(-crap + value).argmin()]
