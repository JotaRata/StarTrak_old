# coding=utf-8
import numpy
import matplotlib
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from numpy.lib.function_base import append
from STCore.item.Star import StarItem
import STCore.Tracker
import STCore.utils.Icons as icons
from matplotlib.patches import Circle, Polygon

from STCore.utils.backgroundEstimator import GetBackgroundMean
#region Variables
App = None
leftPanel = None
rightPanel = None
Image = None
canvas = None
ImageViewer = None
BrightLabel = None
ConfIcon = None
MousePress = None
XLoc= YLoc = None
#endregion
lastRadius = 10
lastBounds = 60

def Awake(Data, star : StarItem, OnStarChange, OnStarAdd = None, starIndex = -1, location = (0,0), name = ""):
	global App, Image, canvas, leftPanel, rightPanel, ImageViewer, BrightLabel, XLoc, YLoc, ConfIcon
	if App is not None:
		return
	App = tk.Toplevel()
	App.configure(bg= "gray15")
	App.wm_title(string = "Configurar Estrella")
	App.protocol("WM_DELETE_WINDOW", CloseWindow)
	App.attributes('-topmost', 'true')
	App.resizable(False, False)
	App.grid_columnconfigure(tuple(range(3)), weight=1)
	App.grid_rowconfigure(tuple(range(3)), weight=1)

	bounds = lastBounds
	radius = lastRadius
	threshold = 0.75
	sigma = 2
	if star is not None:
		name = star.name
		location = star.location
		bounds = star.bounds
		radius = star.radius
		threshold = star.threshold
		sigma = star.bsigma

	StarName = tk.StringVar(value = name)
	XLoc = tk.IntVar(value = location[1])
	YLoc= tk.IntVar(value = location[0])
	StarBounds = tk.IntVar(value = bounds)
	StarRadius = tk.IntVar(value = radius)
	StarThreshold = tk.IntVar(value = threshold)
	SigmaFactor = tk.IntVar(value = sigma)

	nameLabel = ttk.Label(App, text = "Nombre de la estrella: ")
	nameEntry = ttk.Entry(App, textvariable = StarName)

	posLabel = ttk.Label(App, text = "Posicion:")
	XLocSpinBox = ttk.Spinbox(App, from_ = 0, to = Data.shape[1], textvariable = XLoc, width = 10)
	YLocSpinBox = ttk.Spinbox(App, from_ = 0, to = Data.shape[0], textvariable = YLoc, width = 10)

	radiusLabel = ttk.Label(App, text = "Tamaño de la estrella:")
	RadiusSpinBox = ttk.Spinbox(App, from_ = 1, to = StarBounds.get(), textvariable = StarRadius, width = 10, increment = 1)

	boundsLabel = ttk.Label(App, text = "Radio de búsqueda:")
	BoundSpinBox = ttk.Spinbox(App, from_ = 0, to = min(Data.shape), textvariable = StarBounds, width = 10, increment = 10)

	nameLabel.grid(row = 0, column = 0, columnspan=2, sticky="w")
	nameEntry.grid (row =0,column = 2)
	posLabel.grid(row = 1, column = 0, sticky="w")
	XLocSpinBox.grid(row = 1, column = 1)
	YLocSpinBox.grid(row = 1, column = 2, padx = 20)
	radiusLabel.grid(row = 2, column = 0, columnspan=2, sticky="w")
	RadiusSpinBox.grid(row = 2, column = 2)
	boundsLabel.grid(row = 3, column = 0, columnspan=2, sticky="w")
	BoundSpinBox.grid(row = 3, column = 2)

	#typeSelection = tk.IntVar(Window, value = Type)
	#typeFrame = tk.LabelFrame(leftPanel,text = "Tipo de Estrella")
	#typeFrame.grid(row = 1, column = 0, columnspan = 1, sticky = tk.W + tk.E)
	#ttk.Radiobutton(typeFrame, text = "Variable", variable = typeSelection, value = 0).grid(row = 0, sticky = tk.W)
	#ttk.Radiobutton(typeFrame, text = "Referencia", variable = typeSelection, value = 1).grid (row = 1, sticky = tk.W)

	
	
	
	#ThreSpinBox = ttk.Scale(trackFrame, from_ = 0, to = 100, variable = StarThreshold, orient=tk.HORIZONTAL)
	#SigSpinBox = ttk.Spinbox(trackFrame, from_ = 0, to = 4, textvariable = SigmaFactor, width=10, increment= 0.5)

	
	#ttk.Label(trackFrame, text = "Variabilidad:").grid(row = 6, column = 2, sticky = tk.W)
	#ThreSpinBox.grid(row = 6, column = 3, columnspan = 2, sticky = tk.EW)
	
	#ttk.Label(trackFrame, text = "Rechazar si Sigma es menor a:").grid(row = 7, column = 2, sticky = tk.W)
	#SigSpinBox.grid(row = 7, column = 3, columnspan = 1, sticky = tk.EW)

	DrawCanvas(location, radius, Data)

	#back_median = float(GetBackgroundMean(Data))
	#area = (2 * radius) ** 2
	#snr = (Image.get_array()[radius:3*radius, radius:3*radius].sum() / (area * back_median))

	snr = 0

	BrightLabel = ttk.Label(App,font="-weight bold", width = 18, anchor = "w")
	_conf = str(numpy.clip(int(snr/2 + 1), 1, 3))
	ConfIcon = ttk.Label(App, image = icons.Icons["conf"+ _conf])
	UpdateCanvas(Data, location, radius)


	ConfIcon.grid(row = 4, column = 2)
	BrightLabel.grid(row = 4, column = 0, columnspan=2)



	cmd = lambda a,b,c : UpdateCanvas(Data,(int(YLoc.get()), int(XLoc.get())), int(StarRadius.get()))
	XLoc.trace("w",cmd)
	YLoc.trace("w",cmd)
	StarRadius.trace("w",cmd)
	
	applycmd = lambda: Apply(name=StarName.get(),loc=(YLoc.get(), XLoc.get()), bounds=StarBounds.get(),
						 radius=StarRadius.get() , Type=1,
						 value=GetMax(Data,XLoc.get(), YLoc.get(), StarRadius.get())
						 , threshold=StarThreshold.get(),
						 stars=star, OnStarChange= OnStarChange, OnStarAdd = OnStarAdd,starIndex=starIndex, sigma = SigmaFactor.get())

	controlButtons = ttk.Frame(App)
	controlButtons.grid(row =4, column=3)

	CancelButton = ttk.Button(controlButtons, text = "Cancelar", command = CloseWindow, image = icons.Icons["delete"], compound = "left")
	ApplyButton = ttk.Button(controlButtons, text = "Aceptar", command = applycmd, image = icons.Icons["check"], compound = "right", style="Highlight.TButton")
	
	CancelButton.grid(row = 0, column = 0)
	ApplyButton.grid(row = 0, column = 1, padx=4)


def GetMax(data, xloc, yloc, radius):
	stLoc = (yloc, xloc)
	clipLoc = numpy.clip(stLoc, radius, (data.shape[0] - radius, data.shape[1] - radius))
	crop = data[clipLoc[0]-radius : clipLoc[0]+radius,clipLoc[1]-radius : clipLoc[1]+radius]

	return int(numpy.max(crop) - Background_Mean), snr

def DrawCanvas(stLoc, radius, data):
	global Image, canvas, rig
	fig = matplotlib.figure.Figure(figsize = (2,2), dpi = 100)
	axis = fig.add_subplot(111)
	axis.set_axis_off()
	fig.subplots_adjust(0,0,1,1)
	fig.set_facecolor("black")

	clipLoc = numpy.clip(stLoc, radius, (data.shape[0] - radius, data.shape[1] - radius))
	crop = data[clipLoc[0]-radius*2 : clipLoc[0]+radius*2,clipLoc[1]-radius*2 : clipLoc[1]+radius*2]

	levels = STCore.DataManager.Levels
	Image = axis.imshow(crop, vmin = levels[1], vmax = levels[0], cmap=STCore.ImageView.ColorMaps[STCore.Settings._VISUAL_COLOR_.get()], norm = STCore.ImageView.Modes[STCore.Settings._VISUAL_MODE_.get()])
	canvas = FigureCanvasTkAgg(fig, master=App)
	canvas.draw()

	Viewport = canvas.get_tk_widget()
	Viewport.configure(bg="black")
	Viewport.config(cursor = "fleur")

	canvas.mpl_connect("button_press_event", OnMousePress) 
	canvas.mpl_connect("motion_notify_event", OnMouseDrag) 
	canvas.mpl_connect("button_release_event", OnMouseRelase) 

	circle = Circle((radius*2 - 0.5, radius*2 - 0.5), radius, facecolor = "none", edgecolor = "lime")

	axis.add_artist(circle)
	Viewport.grid(row = 0, column=3, rowspan=3)

def Get_BackgroundMean(crop):
	Background_Sample_1 = numpy.median(crop[:5, :])
	Background_Sample_2 = numpy.median(crop[:, -5:])
	Background_Sample_3 = numpy.median(crop[-5:, :])
	Background_Sample_4 = numpy.median(crop[:, :5])
	Background_Samples_Mean = numpy.mean([Background_Sample_1, Background_Sample_2, Background_Sample_3, Background_Sample_4])
	return Background_Samples_Mean

def UpdateCanvas(data, stLoc, radius):
	global Image, canvas, BrightLabel, ConfIcon, snr, Background_Mean
	radius = numpy.clip(radius, 2, min(data.shape))
	clipLoc = numpy.clip(stLoc, radius, (data.shape[0] - radius, data.shape[1] - radius))
	crop = data[clipLoc[0]-radius*2 : clipLoc[0]+radius*2,clipLoc[1]-radius*2 : clipLoc[1]+radius*2]
	Image.set_array(crop)
	Background_Mean = Get_BackgroundMean(crop)
	area = (2 * radius) ** 2
	snr = (crop[radius:3*radius, radius:3*radius].sum() / (area * Background_Mean))
	BrightLabel.config(text = "Señal a Ruido: %.2f " % snr)

	_conf = str(numpy.clip(int(snr/2 + 1), 1, 3))
	ConfIcon.config(image = icons.Icons["conf"+_conf])
	canvas.draw_idle()

def Apply(name, loc, bounds, radius, Type, value, threshold, stars, OnStarChange, OnStarAdd, starIndex, sigma):
	
	#Entre comillas iran los headers que llevarian en el print
	st = StarItem()
	st.name = name  #"Nombre"
	st.location = loc #"Ubicacion"
	st.bounds = bounds #NI IDEA (Alonso)
	st.radius = radius #"Tamaño"
	st.value = value[0] #"Brillo"
	st.snr = value[1] #"Señal a ruido"
	st.background = Background_Mean #"Fondo"
	st.threshold = 1#(threshold * 0.01)
	st.bsigma = 2#sigma
	
	if starIndex == -1:
		if OnStarAdd is not None:
			OnStarAdd(st)
		STCore.Tracker.DataChanged = True

	OnStarChange(st, starIndex)
	st.PrintData()
	CloseWindow()

	global XLoc, YLoc, lastRadius, lastBounds
	lastBounds = bounds
	lastRadius = radius
	XLoc = YLoc = None
	

def CloseWindow():
	global App, BrightLabel, ConfIcon
	App.destroy()
	App = None
	BrightLabel = None
	ConfIcon = None

def OnMousePress(event):
	global MousePress
	MousePress = XLoc.get(), YLoc.get(), event.xdata, event.ydata

def OnMouseDrag(event):
	global XLoc, YLoc
	global MousePress
	if MousePress is None or event.inaxes is None: return
	x0, y0, xpress, ypress = MousePress
	dx = event.xdata - xpress
	dy = event.ydata - ypress
	XLoc.set(int(x0 - dx))
	YLoc.set(int(y0 - dy))

def OnMouseRelase(event):
	global MousePress
	MousePress = None