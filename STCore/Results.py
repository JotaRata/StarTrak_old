import Tkinter as tk
import ttk
from matplotlib import figure, use
use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy
import STCore.DataManager
from STCore.utils.backgroundEstimator import GetBackground, GetBackgroundMean
from STCore.utils.Exporter import *
import math
from os.path import basename
import STCore.ResultsConfigurator as Config
from time import sleep, localtime, gmtime, strftime, time, mktime
from multiprocessing import Pool
import STCore.utils.Icons as icons
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
	STCore.DataManager.CurrentWindow = 4
	TimeLenght = Config.SettingsObject.timeLenght
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
	

	exportbutton = ttk.Button(Sidebar, text = "Exportar",image = icons.Icons["export"], compound = "left")
	exportbutton.bind("<Button-1>", lambda event: PopupMenu(event, Exportmenu))
	exportbutton.grid(row = 0, column = 3)
	if STCore.DataManager.RuntimeEnabled == False:
		ttk.Button(Sidebar, text = "Volver", command = cmdBack, image = icons.Icons["prev"], compound = "left").grid(row = 0, column = 0)
	else:
		ttk.Button(Sidebar, text = "Actualizar",image = icons.Icons["restart"], compound = "left", command = lambda: (Destroy(), Awake(root, ItemList, STCore.Tracker.TrackedStars))).grid(row = 0, column = 1)
	ttk.Button(Sidebar, text = "Configurar", image = icons.Icons["settings"], compound = "left", command = lambda: Config.Awake(root, ItemList, mini = True)).grid(row = 0, column =2)
	legend = figure.Figure(figsize = (3,4), dpi = 100, facecolor="0.95")
	i = 0
	names = []
	while i < len(TrackedStars):
		names.append(TrackedStars[i].star.name)
		i += 1
	legend.legend(Plots, names, loc = 'upper center', fancybox = False, mode ="expand", shadow = False, )
	LegendCanvas = FigureCanvasTkAgg(legend, master=Sidebar)
	LegendCanvas.draw()
	LegendCanvas.get_tk_widget().grid(row = 1, column = 0, columnspan = 3, rowspan = 4, sticky = tk.NSEW)

def PopupMenu(event, Menu):
	Menu.post(event.x_root, event.y_root)

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
def GetConstant(data, index, StarIndex, TrackedStars, Ref):
	track = TrackedStars[StarIndex]
	pos = list(reversed(track.trackedPos[index]))
	radius = track.star.radius
	clipLoc = numpy.clip(pos, radius, (data.shape[0] - radius, data.shape[1] - radius))
	crop = data[clipLoc[0]-radius : clipLoc[0]+radius,clipLoc[1]-radius : clipLoc[1]+radius]
	Backdata = GetBackground(data)
	RefFlux = numpy.sum(crop)
	BackgroundFlux = Backdata[0] * 4 * (radius **2)
	value = Ref + 2.5 * numpy.log10(RefFlux - BackgroundFlux)
	return value

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

def AddPoint(point, stIndex):
	old_off = Plots[stIndex].get_offsets()
	new_off = numpy.concatenate((old_off,numpy.array(point, ndmin=2)))
	Plots[stIndex].set_offsets(new_off)
	Plots[stIndex].axes.figure.canvas.draw_idle()

def UpdateConstant(ItemList):
	global MagData, PlotAxis, Constant
	temp = GetLimits()
	temp = None
	XAxis, Xlabel, XTicks = GetXTicks(ItemList)
	TrackedStars = STCore.Tracker.TrackedStars
	PlotAxis.clear()
	for a in range(len(Plots)):
		Plots[a] = None
	for a in range(len(Plots)):
		Plots[a] = PlotAxis.scatter(XAxis, -MagData[:,a] + Constant, label = TrackedStars[a].star.name, picker = 2)
	PlotAxis.set_xticks(XTicks)
	PlotAxis.grid(axis = "y")
	PlotAxis.set_xticklabels(Xlabel)
	UpdateScale()

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

def UpdateScale(Realtime = False):
	global MagData, TimeLenght, Constant
	Xmin, Xmax, Ymin, Ymax, added_points = GetLimits()
	if not numpy.isnan(Xmin) or not numpy.isnan(Xmax):
		PlotAxis.set_xlim(Xmin-0.1*(Xmax-Xmin),Xmax+0.1*(Xmax-Xmin))
	if not numpy.isnan(Ymin) or not numpy.isnan(Ymax):
		PlotAxis.set_ylim(Ymax+0.1*(Ymax-Ymin), Ymin-0.1*(Ymax-Ymin))
	#PlotAxis.invert_yaxis()	
	#PlotAxis.grid(axis = "y")
	if Realtime == True:
		MagData = numpy.append(MagData,-numpy.array([added_points]) + Constant, 0)
	PlotAxis.figure.canvas.draw_idle()

def CreateCanvas(root, app, ItemList, TrackedStars):
	global PlotAxis, Plots, MagData, PlotCanvas, Constant, BackgroundFlux
	viewer = tk.Frame(app, width = 700, height = 400, bg = "white")
	viewer.pack(side=tk.LEFT, fill = tk.BOTH, expand = True, anchor = tk.W)
	fig = figure.Figure(figsize = (7,4), dpi = 100)
	PlotAxis = fig.add_subplot(111)
	progress = tk.DoubleVar()
	LoadBar = CreateLoadBar(root, progress)

	XAxis, Xlabel, XTicks = GetXTicks(ItemList)
	progress.set(20)
	sleep(0.001)
	#Xlabel= []
	Constant = GetConstant(ItemList[0].data, 0, 
												  max(Config.SettingsObject.refStar, 0),TrackedStars, Config.SettingsObject.refValue)
	#for item in ItemList:
	#	Xlabel.append(basename(item.path))
	Plots = range(len(TrackedStars))
	if (MagData is None):
		MagData = numpy.empty((0 ,len(TrackedStars)))
		i = 0
		print len(ItemList)
		while i < len(ItemList):
			YAxis = GetTrackedValues(ItemList, TrackedStars, i, Constant)
			MagData = numpy.append(MagData, numpy.atleast_2d(numpy.array(YAxis)), 0)
			progress.set(20+80*float(i)/len(ItemList))
			LoadBar[0].update()
			sleep(0.001)
			i += 1
	for a in range(len(Plots)):
		Plots[a] = PlotAxis.scatter(XAxis, -MagData[:,a] + Constant, label = TrackedStars[a].star.name, picker=2)
	STCore.DataManager.ResultData = MagData
	STCore.DataManager.ResultConstant = Constant
	#print MagData.shape
	LoadBar[0].destroy()
	#PlotAxis.legend()
	#UpdateScale()
	GetLimits()
	ticks = Config.SettingsObject.tickNumber
	PlotAxis.set_xticks(XTicks)
	PlotAxis.set_xticklabels(Xlabel)
	for tick in PlotAxis.get_xticklabels():
		tick.set_rotation(0)
	#PlotAxis.invert_yaxis()	
	PlotAxis.grid(axis = "y")
	PlotCanvas = FigureCanvasTkAgg(fig,master=viewer)
	PlotCanvas.draw()
	PlotCanvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
	PlotCanvas.mpl_connect('pick_event', lambda event: (PlotCanvas._tkcanvas.focus_set(), OnMouseClick(event)))
	PlotCanvas.mpl_connect('key_press_event', OnKeyPress)
	PlotCanvas.mpl_connect('key_release_event', OnKeyRelase)
	UpdateScale()
	return PlotCanvas, fig, MagData

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

def GetValue(data, Track, Constant, FileIndex, Backdata):
	global prevFlux
	radius = Track.star.radius
	if len(Track.trackedPos) <= FileIndex:
		print "Star has no enough tracking points, aborting.."
		return numpy.nan
	pos = list(reversed(Track.trackedPos[FileIndex]))
	clipLoc = numpy.clip(pos, radius, (data.shape[0] - radius, data.shape[1] - radius))
	crop = data[clipLoc[0]-radius : clipLoc[0]+radius,clipLoc[1]-radius : clipLoc[1]+radius]
	StarFlux = numpy.sum(crop)
	if FileIndex == 0:
		prevFlux = StarFlux
	BackgroundFlux = Backdata * 4 * (radius **2)
	mag = 2.5 * numpy.log10(StarFlux - BackgroundFlux) #0*Constant -  M
	if Config.SettingsObject.delLostTracks == 1 and FileIndex in Track.lostPoints:
		mag = numpy.nan
	if Config.SettingsObject.delError == 1 and abs(numpy.sqrt(StarFlux) - numpy.sqrt(prevFlux)) > numpy.sqrt(Track.star.threshold)*0.5:
		mag = numpy.nan
	prevFlux = StarFlux
	return mag

def GetTrackedValues(ItemList, TrackedStars, Trackindex, Constant):
	global prevFlux
	values=[]
	index = 0
	prevFlux = 0
	data = ItemList[Trackindex].data
	#st = time()
	Backdata = GetBackgroundMean(data)
	while index < len(TrackedStars):
		mag = GetValue(data, TrackedStars[index], Constant, Trackindex, Backdata)
		values.append(mag)
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
		
