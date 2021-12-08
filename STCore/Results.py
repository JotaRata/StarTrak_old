import tkinter as tk
from tkinter import ttk
from matplotlib import figure, use
use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy
from utils.backgroundEstimator import GetBackground, GetBackgroundMean
from utils.Exporter import *
import math
from os.path import basename
import DataManager, Tracker, ImageView
import ResultsConfigurator as Config
from time import sleep, localtime, gmtime, strftime, time, mktime
from multiprocessing import Pool

from Icons import GetIcon
from functools import partial
import sys
#region  Variables
ResultsFrame = None
PlotAxis = None
Plots = None
MagData = None
PlotCanvas = None
Constant = None
BackgroundFlux = None
TimeLenght = None
DelkeyPressed = False
#endregion

def Reset():
	global ResultsFrame, PlotAxis, Plots, MagData, PlotCanvas, Constant
	ResultsFrame = None
	PlotAxis = None
	Plots = None
	MagData = None
	PlotCanvas = None
	Constant = None
	TimeLenght = None

def Awake(root, ItemList, TrackedStars):
	global ResultsFrame, TimeLenght
	DataManager.CurrentWindow = 4
	TimeLenght = Config.SettingsObject.timeLenght
	ResultsFrame = ttk.Frame(root)
	ResultsFrame.pack(fill = tk.BOTH, expand = 1)
	canvas = CreateCanvas(root, ResultsFrame, ItemList, TrackedStars)
	Sidebar = ttk.Frame(ResultsFrame, width = 400)
	Sidebar.pack(side = tk.RIGHT, fill = tk.Y)
	cmdBack = lambda: (Destroy(), Tracker.Awake(root, ImageView.Stars, ItemList))
	Exportmenu = tk.Menu(root, tearoff=0)
	Exportmenu.add_command(label="Exportar grafico", command=lambda: ExportImage(canvas[1]))
	Exportmenu.add_command(label="Exportar datos", command=lambda: ExportData(TrackedStars, canvas[2], GetTimeLabel(ItemList)))
	Exportmenu.add_command(label="Exportar PDF", command=lambda: ExportPDF(canvas[1], canvas[2], TrackedStars))
	
	buttonFrame = ttk.Frame(Sidebar)
	buttonFrame.pack(side=tk.TOP, fill=tk.X)

	exportbutton = ttk.Button(buttonFrame, text = "Exportar",image = GetIcon("export"), compound = "left")
	exportbutton.bind("<Button-1>", lambda event: PopupMenu(event, Exportmenu))
	exportbutton.pack(side=tk.RIGHT, fill=tk.X)
	if DataManager.RuntimeEnabled == False:
		ttk.Button(buttonFrame, text = "Volver", command = cmdBack, image = GetIcon("prev"), compound = "left").pack(side=tk.LEFT, fill=tk.X)
	else:
		ttk.Button(buttonFrame, text = "Actualizar",image = GetIcon("restart"), compound = "left", command = lambda: (Destroy(), Awake(root, ItemList, Tracker.TrackedStars))).pack(side=tk.CENTER, anchor=tk.NW)
	#ttk.Button(Sidebar, text = "Configurar", image = icons.Icons["settings"], compound = "left", command = lambda: Config.Awake(root, ItemList, mini = True)).pack(side=tk.TOP)
	ttk.Label(Sidebar, text="Leyenda").pack()
	legend = figure.Figure(figsize = (1, len(TrackedStars) / 4.), dpi = 100, facecolor="0.25")
	i = 0
	legend.set_facecolor("0.15")
	names = []
	while i < len(TrackedStars):
		names.append(TrackedStars[i].star.name)
		i += 1
	legend.legend(Plots, names, loc = 'upper center', fancybox = False, mode ="expand", shadow = False, )
	LegendCanvas = FigureCanvasTkAgg(legend, master=Sidebar)
	LegendCanvas.draw()
	LegendCanvas.get_tk_widget().pack(side=tk.TOP, fill=tk.X)
	Config.Awake(Sidebar, ItemList, toplevel=False)

def PopupMenu(event, Menu):
	Menu.post(event.x_root, event.y_root)


def AddPoint(point, stIndex):
	old_off = Plots[stIndex].get_offsets()
	new_off = numpy.concatenate((old_off,numpy.array(point, ndmin=2)))
	Plots[stIndex].set_offsets(new_off)
	Plots[stIndex].axes.figure.canvas.draw_idle()

def UpdateGraph(ItemList):
	global MagData, PlotAxis
	
	TrackedStars = Tracker.TrackedStars

	PlotData = None
	
	if Config.SettingsObject.plotkind == 0:
		PlotData= RegisterMagnitudes(ItemList, TrackedStars)
		DrawGraph(PlotData, ItemList, TrackedStars, flipy=True, label = "Magnitud")
		UpdateScale(flipy=True)
	else:
		PlotData= RegisterSignal(ItemList, TrackedStars)
		DrawGraph(PlotData, ItemList, TrackedStars, flipy=False, label = "SNR")
		UpdateScale(flipy=False)
	
	

def DrawGraph(PlotData, ItemList, TrackedStars,label = "Magnitud", flipy = True):
	global PlotAxis
	XAxis, Xlabel, XTicks = GetXTicks(ItemList)
	PlotAxis.clear()
	
	for a in range(len(Plots)):
		Plots[a] = PlotAxis.scatter(XAxis, PlotData[:,a], label = TrackedStars[a].star.name, picker = 2, marker="*")
	PlotAxis.set_xticks(XTicks)
	PlotAxis.grid(axis = "y")
	PlotAxis.set_xticklabels(Xlabel)
	if flipy:
		PlotAxis.invert_yaxis()	
	PlotAxis.set_xlabel("Tiempo")
	PlotAxis.set_ylabel(label)
	for tick in PlotAxis.get_xticklabels():
		tick.set_rotation(0)

def GetLimits():
	global TimeLenght
	Xmin, Xmax = 0, 1
	Ymin, Ymax = 0, 1
	added_points = []
	i = 0
	while i < len(Plots):
	#for p in Plots:
		try:
			p = Plots[i]
			new_off = p.get_offsets()   #offsets [x],[y]
			xmin=new_off[:,0].min()
			xmax=max(new_off[:,0].max(), xmin + Config.SettingsObject.timeLenght)
			ymin=new_off[:,1].min()+-1
			ymax=new_off[:,1].max()+1
			if i == 0:
				Ymax = ymax
				Ymin = ymin
			Xmax = xmax
			Xmin = xmin
			added_points.append(new_off[-1, 1])
			if ymax > Ymax:	Ymax = ymax
			if ymin < Ymin:	Ymin = ymin
		except:
			pass
		i += 1
	TimeLenght = Xmax
	return Xmin, Xmax, Ymin, Ymax, added_points

def UpdateScale(Realtime = False, flipy = True):
	global MagData, TimeLenght
	Xmin, Xmax, Ymin, Ymax, added_points = GetLimits()
	if not numpy.isnan(Xmin) or not numpy.isnan(Xmax):
		PlotAxis.set_xlim(Xmin-0.1*(Xmax-Xmin),Xmax+0.1*(Xmax-Xmin))
	if not numpy.isnan(Ymin) or not numpy.isnan(Ymax):
		if flipy:
			PlotAxis.set_ylim(Ymax+0.1*(Ymax-Ymin), Ymin-0.1*(Ymax-Ymin))
		else:
			PlotAxis.set_ylim(Ymin-0.1*(Ymax-Ymin), Ymax+0.1*(Ymax-Ymin))
	#PlotAxis.invert_yaxis()	
	#PlotAxis.grid(axis = "y")
	if Realtime == True:
		MagData = numpy.append(MagData,-numpy.array([added_points]), 0)
	PlotAxis.figure.canvas.draw_idle()

def CreateCanvas(root, app, TrackList, TrackedStars):
	global PlotAxis, Plots, MagData, PlotCanvas, BackgroundFlux
	viewer = ttk.Frame(app, width = 700, height = 400)
	viewer.pack(side=tk.LEFT, fill = tk.BOTH, expand = True, anchor = tk.W)
	fig = figure.Figure(figsize = (7,4), dpi = 100)
	fig.set_facecolor("black")
	PlotAxis = fig.add_subplot(111)
	progress = tk.DoubleVar()
	Plots = list(range(len(TrackedStars)))
	RegisterMagnitudes(TrackList, TrackedStars)

	DrawGraph(MagData,TrackList, TrackedStars)
	
	DataManager.ResultData = MagData
	
	GetLimits()
	ticks = Config.SettingsObject.tickNumber


	PlotCanvas = FigureCanvasTkAgg(fig,master=viewer)
	PlotCanvas.draw()
	PlotCanvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
	PlotCanvas.mpl_connect('pick_event', lambda event: (PlotCanvas._tkcanvas.focus_set(), OnMouseClick(event)))
	PlotCanvas.mpl_connect('key_press_event', OnKeyPress)
	PlotCanvas.mpl_connect('key_release_event', OnKeyRelase)
	UpdateScale()
	return PlotCanvas, fig, MagData

def RegisterMagnitudes(TrackList, TrackedStars):
	global MagData
	MagData = numpy.empty((0 ,len(TrackedStars)))
	i = 0
	while i < len(TrackList):
		YAxis = GetTrackedValues(TrackList, TrackedStars, i)
		MagData = numpy.append(MagData, numpy.atleast_2d(numpy.array(YAxis)), 0)
		i += 1
	return MagData

def RegisterSignal(TrackList, TrackedStars):
	SignalData = numpy.empty((0 ,len(TrackedStars)))
	
	def SignalProcess(data, FileIndex, BackgroundMedian):
		values = []
		for Track in TrackedStars:
			radius = Track.star.radius
			pos = list(reversed(Track.trackedPos[FileIndex]))
			clipLoc = numpy.clip(pos, radius, (data.shape[0] - radius, data.shape[1] - radius))
			crop = data[clipLoc[0]-radius : clipLoc[0]+radius,clipLoc[1]-radius : clipLoc[1]+radius]
			StarFlux = numpy.sum(crop)

			BackgroundFlux = BackgroundMedian * (2*radius)**2
			values.append(StarFlux / BackgroundFlux)
		return values
	
	i = 0
	while i < len(TrackList):
		data = TrackList[i].data
		BackgroundMedian = GetBackgroundMean(data)
		YAxis = SignalProcess(data, i, BackgroundMedian)
		SignalData = numpy.append(SignalData, numpy.atleast_2d(numpy.array(YAxis)), 0)
		i += 1
	return SignalData

def CreateLoadBar(root, progress, title = "Cargando.."):
	popup = tk.Toplevel()
	popup.geometry("300x60+%d+%d" % (root.winfo_width()/2,  root.winfo_height()/2) )
	popup.wm_title(string = title)
	popup.attributes('-topmost', 'true')
	popup.overrideredirect(1)
	pframe = tk.LabelFrame(popup)
	pframe.pack(fill = tk.BOTH, expand = 1)
	label = tk.Label(pframe, text="Analizando datos..")
	bar = ttk.Progressbar(pframe, variable=progress, maximum=100)
	label.pack()
	bar.pack(fill = tk.X)
	return popup, label, bar


def GetTrackedValues(TrackList, TrackedStars, Trackindex):
	global prevFlux
	values=[]
	index = 0
	prevFlux = 0
	refIndex = max(Config.SettingsObject.refStar, 0)
	data = TrackList[Trackindex].data

	def GetMagnitude(data, Track, RefMagnitude, FileIndex, BackgroundMedian):
		global prevFlux
		radius = Track.star.radius
		if len(Track.trackedPos) <= FileIndex:
			print ("Star has no enough tracking points, aborting..")
			return numpy.nan
		pos = list(reversed(Track.trackedPos[FileIndex]))
		clipLoc = numpy.clip(pos, radius, (data.shape[0] - radius, data.shape[1] - radius))
		crop = data[clipLoc[0]-radius : clipLoc[0]+radius,clipLoc[1]-radius : clipLoc[1]+radius]
		StarFlux = numpy.sum(crop)
		if FileIndex == 0:
			prevFlux = StarFlux

		BackgroundFlux = BackgroundMedian * (radius **2)
		mag = 2.5 * numpy.log10(StarFlux - BackgroundFlux) - RefMagnitude#0*Constant -  M


		if Config.SettingsObject.delLostTracks == 1 and FileIndex in Track.lostPoints:
			mag = numpy.nan
		if Config.SettingsObject.delError == 1 and abs(numpy.sqrt(StarFlux) - numpy.sqrt(prevFlux)) > numpy.sqrt(Track.star.threshold)*0.5:
			mag = numpy.nan
		prevFlux = StarFlux
		return mag
	#st = time()
	BackgroundMedian = GetBackgroundMean(data)
	RefMag = GetMagnitude(data, TrackedStars[refIndex], -Config.SettingsObject.refValue, Trackindex, BackgroundMedian)

	while index < len(TrackedStars):
		mag = GetMagnitude(data, TrackedStars[index], RefMag, Trackindex, BackgroundMedian)
		values.append(-mag)
		index += 1
	#print "elapsed: ", time() -st
	return values

def Destroy():
	global MagData
	ResultsFrame.destroy()
	MagData = None

def GetMaxima(crop, value):
	return numpy.max(crop)
	crap = crop.flatten()
	return crap[numpy.abs(-crap + value).argmin()]
# Data retrieving functions

def GetTimeLabel(ItemList):
	t=[]
	prevDay = 0
	ref = ItemList[0].date
	l = numpy.linspace(0,len(ItemList) - 1,Config.SettingsObject.tickNumber).astype(int)
	for i in l:
		d = (float(i)/len(ItemList))* TimeLenght
		h = ref.tm_hour + int(d / 3600)
		m = ref.tm_min + int(60*(d/3600 - d//3600))
		if m >= 60:
			m -= 60
			h += 1
		date = str(h)+":"+"{:02}".format(m)
		if ItemList[i].date.tm_mday - ItemList[prevDay].date.tm_mday > 0 or i == 0:
			prevDay = i
			date = strftime('%H:%M\n%d/%m/%Y\n(UTC)',ItemList[i].date)
		t.append(date)
	return t
def GetNameLabel(ItemList):
	t=[]
	l=numpy.linspace(0,len(ItemList) - 1,Config.SettingsObject.tickNumber).astype(int)
	for i in l:
		t.append(basename(ItemList[i].path))
	return t


def GetDateValue(ItemList):
	global TimeLenght
	t=[]
	epoch = mktime(ItemList[0].date)
	for i in range(len(ItemList)):
		val = mktime(ItemList[i].date)-epoch
		t.append(val)
		if val > TimeLenght:
			TimeLenght = val
	return t
def GetDateTicks(ItemList):
	t = []
	epoch = mktime(ItemList[0].date)
	l=numpy.linspace(0,TimeLenght, Config.SettingsObject.tickNumber).astype(int)
	return l

def GetNameValue(ItemList):
	t = range(len(ItemList))
	return t
def GetNameTicks(ItemList):
	t = numpy.linspace(0,len(ItemList) - 1,Config.SettingsObject.tickNumber).astype(int)
	return t
def GetXTicks(ItemList):
	XAxis = []
	Xlabel = []
	XTicks = []
	if Config.SettingsObject.sortingMode == 0:
		XAxis = GetDateValue(ItemList)
		Xlabel= GetTimeLabel(ItemList)
		XTicks = GetDateTicks(ItemList)
	else:
		XAxis = GetNameValue(ItemList)
		Xlabel = GetNameLabel(ItemList)
		XTicks = GetNameTicks(ItemList)
	return XAxis, Xlabel, XTicks

# Events
def OnKeyPress(event):
	global DelkeyPressed
	sys.stdout.flush()
	if event.key == 'alt':
		DelkeyPressed = True
	return

def OnKeyRelase(event):
	global DelkeyPressed
	if event.key == 'alt':
		DelkeyPressed = False
	return

def OnMouseClick(event):
	global DelkeyPressed, MagData
	if event.artist == None or DelkeyPressed == False:
		return
	#try:
	p = event.artist
	pind = Plots.index(p)
	ind = event.ind[0]
	new_off = p.get_offsets()
	new_off[ind, 1] = numpy.nan
	p.set_offsets(new_off)
	MagData[ind, pind] = numpy.nan
	UpdateScale()
	p.axes.figure.canvas.draw_idle()
	#except:
	#	pass
		
