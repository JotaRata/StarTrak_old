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
from time import sleep, localtime, gmtime, strftime, time
from multiprocessing import Pool
#region  Variables
ResultsFrame = None
PlotAxis = None
Plots = None
MagData = None
PlotCanvas = None
Constant = None
BackgroundFlux = None
#endregion


def Awake(root, ItemList, TrackedStars):
	global ResultsFrame
	STCore.DataManager.CurrentWindow = 4
	ResultsFrame = tk.Frame(root)
	ResultsFrame.pack(fill = tk.BOTH, expand = 1)
	canvas = CreateCanvas(root, ResultsFrame, ItemList, TrackedStars)
	Sidebar = tk.Frame(ResultsFrame, width = 400)
	Sidebar.pack(side = tk.RIGHT, fill = tk.Y)
	cmdBack = lambda: (Destroy(), STCore.Tracker.Awake(root, STCore.ImageView.Stars, ItemList))
	
	Exportmenu = tk.Menu(root, tearoff=0)
	Exportmenu.add_command(label="Exportar grafico", command=lambda: ExportImage(canvas[1]))
	Exportmenu.add_command(label="Exportar datos", command=lambda: ExportData(TrackedStars, canvas[2], GetTimeLabel(ItemList)))
	Exportmenu.add_command(label="Exportar PDF", command=lambda: ExportPDF(canvas[1], canvas[2], TrackedStars))
	

	exportbutton = ttk.Button(Sidebar, text = "Exportar")
	exportbutton.bind("<Button-1>", lambda event: PopupMenu(event, Exportmenu))
	exportbutton.grid(row = 0, column = 0)

	ttk.Button(Sidebar, text = "Volver", command = cmdBack).grid(row = 0, column = 1)
	ttk.Button(Sidebar, text = "Configurar", command = lambda: STCore.ResultsConfigurator.Awake(root, ItemList, TrackedStars, mini = True)).grid(row = 0, column =2)
def PopupMenu(event, Menu):
	Menu.post(event.x_root, event.y_root)

def GetTimeLabel(ItemList):
	t=[]
	prevDay = 0
	for i in range(len(ItemList)):
		date =  strftime('%H:%M:%S',gmtime(ItemList[i].date))
		if ItemList[i].date - ItemList[prevDay].date > 43200 or i == 0:
			prevDay = i
			date = strftime('%H:%M:%S\n%d/%m/%Y\n(UTC)',gmtime(ItemList[i].date))
		t.append(date)
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
	epoch = time()
	for i in range(len(ItemList)):
		#ls = list(ItemList[i].date.split(":"))
		t.append(ItemList[i].date - epoch)
		print ItemList[i].date - epoch
	return t
def GetNameValue(ItemList):
	t = range(len(ItemList))
	return t
def GetXTicks(ItemList):
	XAxis = []
	Xlabel = []
	if Config.SettingsObject.sortingMode == 0:
		XAxis = GetDateValue(ItemList)
		Xlabel=GetTimeLabel(ItemList)
	else:
		XAxis = GetNameValue(ItemList)
		Xlabel = GetNameLabel(ItemList)
	return XAxis, Xlabel

def AddPoint(point, stIndex):
	old_off = Plots[stIndex].get_offsets()
	new_off = numpy.concatenate((old_off,numpy.array(point, ndmin=2)))
	Plots[stIndex].set_offsets(new_off)
	Plots[stIndex].axes.figure.canvas.draw_idle()

def UpdateScale():
	global MagData
	Xmin, Xmax = 0, 1
	Ymin, Ymax = 0, 1
	added_points = []
	for p in Plots:
		new_off = p.get_offsets()
		xmin=new_off[:,0].min()
		xmax=max(new_off[:,0].max(), xmin + 3600)
		ymin=new_off[:,1].min()
		ymax=new_off[:,1].max()
		Xmax = xmax
		Xmin = xmin
		added_points.append(new_off[-1, 1])
		if ymax > Ymax:	Ymax = ymax
		if ymin < Ymin:	Ymin = ymin
	print Xmin, Xmax
	print Ymin, Ymax
	PlotAxis.set_xlim(Xmin-0.1*(Xmax-Xmin),Xmax+0.1*(Xmax-Xmin))
	PlotAxis.set_ylim(Ymin-0.1*(Ymax-Ymin),Ymax+0.1*(Ymax-Ymin))
	PlotAxis.invert_yaxis()	
	PlotAxis.grid(axis = "y")
	PlotAxis.figure.canvas.draw_idle()
	print "added_points",added_points, numpy.swapaxes(numpy.array([added_points]), 0, 1).shape
	print "Magdata", MagData, MagData.shape
	MagData = numpy.append(MagData,numpy.swapaxes(numpy.array([added_points]), 0, 1), 1)

def CreateCanvas(root, app, ItemList, TrackedStars):
	global PlotAxis, Plots, MagData, PlotCanvas, Constant, BackgroundFlux
	viewer = tk.Frame(app, width = 700, height = 400, bg = "white")
	viewer.pack(side=tk.LEFT, fill = tk.BOTH, expand = True, anchor = tk.W)
	fig = figure.Figure(figsize = (7,4), dpi = 100)
	PlotAxis = fig.add_subplot(111)
	progress = tk.DoubleVar()
	LoadBar = CreateLoadBar(root, progress)

	XAxis, Xlabel = GetXTicks(ItemList)
	progress.set(20)
	sleep(0.01)
	#Xlabel= []
	Constant, BackgroundFlux, StarFlux = GetConstant(ItemList[0].data, TrackedStars, 0, 
												  max(Config.SettingsObject.refStar, 0), Config.SettingsObject.refValue)
	#for item in ItemList:
	#	Xlabel.append(basename(item.path))
	Plots = range(len(TrackedStars))
	if (MagData is None):
		MagData = numpy.empty((0 ,len(ItemList)))
		i = 0
		while i < len(TrackedStars):
			YAxis = GetTrackedValues(ItemList, TrackedStars, i, Constant, BackgroundFlux, StarFlux)
			MagData = numpy.append(MagData, numpy.atleast_2d(numpy.array(YAxis)), 0)
			progress.set(20+80*float(i)/len(TrackedStars))
			LoadBar[0].update()
			sleep(0.01)
			i += 1
	for a in range(len(Plots)):
		Plots[a] = PlotAxis.scatter(XAxis, MagData[a], label = TrackedStars[a].star.name)
	STCore.DataManager.ResultData = MagData
	#print MagData.shape
	LoadBar[0].destroy()
	PlotAxis.legend()
	ticks = STCore.ResultsConfigurator.SettingsObject.tickNumber
	PlotAxis.set_xticks(XAxis[0::max(1, len(ItemList) / ticks)])
	PlotAxis.set_xticklabels(Xlabel[0::max(1, len(ItemList) / ticks)])
	for tick in PlotAxis.get_xticklabels():
		tick.set_rotation(0)
	PlotAxis.invert_yaxis()	
	PlotAxis.grid(axis = "y")
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

def GetValue(ItemList, Track, Constant, BackgroundFlux, FileIndex):
	global prevFlux
	radius = Track.star.radius
	pos = list(reversed(Track.trackedPos[FileIndex]))
	data = ItemList[FileIndex].data
	clipLoc = numpy.clip(pos, radius, (data.shape[0] - radius, data.shape[1] - radius))
	crop = data[clipLoc[0]-radius : clipLoc[0]+radius,clipLoc[1]-radius : clipLoc[1]+radius]
	Backdata = GetBackground(data)
	StarFlux = numpy.sum(crop)
	if FileIndex == 0:
		prevFlux = StarFlux
	BackgroundFlux = Backdata[0] * 4 * (radius **2)
	mag = Constant - 2.5 * numpy.log10(StarFlux - BackgroundFlux)
	if STCore.ResultsConfigurator.SettingsObject.delLostTracks == 1 and FileIndex in Track.lostPoints:
		mag = numpy.nan
	print abs(numpy.sqrt(StarFlux) - numpy.sqrt(prevFlux))
	if STCore.ResultsConfigurator.SettingsObject.delError == 1 and abs(numpy.sqrt(StarFlux) - numpy.sqrt(prevFlux)) > numpy.sqrt(Track.star.threshold)*0.5:
		mag = numpy.nan
	prevFlux = StarFlux
	return mag

def GetTrackedValues(ItemList, TrackedStars, Trackindex, Constant, BackgroundFlux, returnValue):
	global prevFlux
	values=[]
	index = 0
	Track = TrackedStars[Trackindex]
	radius = Track.star.radius
	prevFlux = 0
	while index < len(ItemList):
		mag = GetValue(ItemList, Track, Constant, BackgroundFlux, index)
		values.append(mag)
		index += 1
	returnValue = values   # para usar return en un proceso
	return values

def Destroy():
	global MagData
	ResultsFrame.destroy()
	MagData = None

def GetMaxima(crop, value):
	return numpy.max(crop)
	crap = crop.flatten()
	return crap[numpy.abs(-crap + value).argmin()]
