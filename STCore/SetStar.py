# coding=utf-8
import numpy
import matplotlib
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from STCore.item.Star import StarItem
import STCore.Tracker
import STCore.utils.Icons as icons
from STCore.utils.backgroundEstimator import GetBackgroundMean
#region Variables
Window = None
leftPanel = None
rightPanel = None
Image = None
ImageCanvas = None
ImageViewer = None
BrightLabel = None
ConfIcon = None
MousePress = None
XLoc= YLoc = None
#endregion


def Awake(root, Data, Stars, OnStarChange, starIndex = -1, name = "Nueva Estrella", location = (20, 20), radius = 15, bounds = 40, Type = 0, threshold = 50, sigma = 2):
	global Window, Image, ImageCanvas, leftPanel, rightPanel, ImageViewer, BrightLabel, XLoc, YLoc, ConfIcon
	if Window is not None:
		return
	Window = tk.Toplevel()
	Window.configure(bg= "black")
	Window.wm_title(string = "Configurar Estrella")
	Window.protocol("WM_DELETE_WINDOW", CloseWindow)
	Window.attributes('-topmost', 'true')
	Window.resizable(False, False)

	leftPanel = ttk.Frame(Window)
	leftPanel.grid(row = 0,column = 0, sticky=tk.NS)
	rightPanel = ttk.Frame(Window)
	rightPanel.grid(row=0,column = 1, sticky=tk.NS, padx = 20)

	nameFrame = ttk.Frame(leftPanel)
	nameFrame.grid(row = 0, column = 0, sticky = tk.W)
	ttk.Label(nameFrame, text = "Nombre de la estrella: ").grid(row = 0, column = 0, sticky = tk.W)
	StarName = tk.StringVar(Window, value = name)
	nameEntry = ttk.Entry(nameFrame, textvariable = StarName)
	nameEntry.grid (row =0,column = 1, sticky = tk.EW)
	
	#typeSelection = tk.IntVar(Window, value = Type)
	#typeFrame = tk.LabelFrame(leftPanel,text = "Tipo de Estrella")
	#typeFrame.grid(row = 1, column = 0, columnspan = 1, sticky = tk.W + tk.E)
	#ttk.Radiobutton(typeFrame, text = "Variable", variable = typeSelection, value = 0).grid(row = 0, sticky = tk.W)
	#ttk.Radiobutton(typeFrame, text = "Referencia", variable = typeSelection, value = 1).grid (row = 1, sticky = tk.W)
	
	ImageViewer = ttk.LabelFrame(rightPanel,text = "Vista previa")
	ImageViewer.grid(row = 0, column = 0, rowspan=2, sticky = tk.NSEW)

	locFrame = ttk.Frame(leftPanel)
	locFrame.grid(row = 2, column = 0, sticky = tk.EW)
	trackFrame = ttk.LabelFrame(leftPanel, text = "Opciones de rastreo")
	trackFrame.grid(row = 3, column = 0, sticky = tk.EW)

	XLoc = tk.IntVar(locFrame, value = location[1])
	YLoc= tk.IntVar(locFrame, value = location[0])
	StarBounds = tk.IntVar(locFrame, value = bounds)
	StarRadius = tk.IntVar(locFrame, value = radius)
	StarThreshold = tk.IntVar(locFrame, value = threshold)
	SigmaFactor = tk.IntVar(locFrame, value = sigma)

	ttk.Label(locFrame, text = "Posicion:").grid(row = 3, column = 2, sticky = tk.W)
	XLocSpinBox = ttk.Spinbox(locFrame, from_ = 0, to = Data.shape[1], textvariable = XLoc, width = 10)
	YLocSpinBox = ttk.Spinbox(locFrame, from_ = 0, to = Data.shape[0], textvariable = YLoc, width = 10)
	RadiusSpinBox = ttk.Spinbox(locFrame, from_ = 0, to = min(Data.shape), textvariable = StarRadius, width = 10, increment = 5)
	
	BoundSpinBox = ttk.Spinbox(trackFrame, from_ = 0, to = min(Data.shape), textvariable = StarBounds, width = 10, increment = 10)
	ThreSpinBox = ttk.Scale(trackFrame, from_ = 0, to = 100, variable = StarThreshold, orient=tk.HORIZONTAL)
	SigSpinBox = ttk.Spinbox(trackFrame, from_ = 0, to = 4, textvariable = SigmaFactor, width=10, increment= 0.5)

	XLocSpinBox.grid(row = 3, column = 3)
	YLocSpinBox.grid(row = 3, column = 4, padx = 20)
	ttk.Label(locFrame, text = "Tamaño de la estrella:").grid(row = 4, column = 2, sticky = tk.W)
	RadiusSpinBox.grid(row = 4, column = 3, columnspan = 2, sticky = tk.EW)
	

	ttk.Label(trackFrame, text = "Radio de búsqueda:").grid(row = 5, column = 2, sticky = tk.W)
	BoundSpinBox.grid(row = 5, column = 3, columnspan = 1, sticky = tk.EW)
	ttk.Label(trackFrame, text = "Variabilidad:").grid(row = 6, column = 2, sticky = tk.W)
	ThreSpinBox.grid(row = 6, column = 3, columnspan = 2, sticky = tk.EW)
	
	ttk.Label(trackFrame, text = "Rechazar si Sigma es menor a:").grid(row = 7, column = 2, sticky = tk.W)
	SigSpinBox.grid(row = 7, column = 3, columnspan = 1, sticky = tk.EW)

	DrawCanvas(location, radius, Data)
	back_median = float(GetBackgroundMean(Data))
	confidence = int(min((numpy.max(Image.get_array()))/ back_median - 1, 1.0)*100)
	BrightLabel = ttk.Label(trackFrame, text = "Confidencia: " + str(confidence)+"%",font="-weight bold", width = 18, anchor = "w")
	_conf = str(numpy.clip(int(confidence/30 + 1), 1, 3))
	ConfIcon = ttk.Label(trackFrame, image = icons.Icons["conf"+ _conf])
	ConfIcon.grid(row = 8, column = 3)
	BrightLabel.grid(row = 8, column = 2, sticky = tk.W)
	cmd = lambda a,b,c : UpdateCanvas(Data,(int(YLoc.get()), int(XLoc.get())), int(StarRadius.get()), back_median)
	XLoc.trace("w",cmd)
	YLoc.trace("w",cmd)
	StarRadius.trace("w",cmd)
	
	applycmd = lambda: Apply(name=StarName.get(),loc=(YLoc.get(), XLoc.get()), bounds=StarBounds.get(),
						 radius=StarRadius.get() , Type=1,
						 value=GetMax(Data,XLoc.get(), YLoc.get(), StarRadius.get(), back_median)
						 , threshold=StarThreshold.get(),
						 stars=Stars, OnStarChange= OnStarChange,starIndex=starIndex, sigma = SigmaFactor.get())

	controlButtons = ttk.Frame(rightPanel)
	controlButtons.grid(row =3)
	ApplyButton = ttk.Button(controlButtons, text = "Aceptar", command = applycmd, image = icons.Icons["check"], compound = "right")
	ApplyButton.grid(row = 0, column = 1)
	CancelButton = ttk.Button(controlButtons, text = "Cancelar", command = CloseWindow, image = icons.Icons["delete"], compound = "left")
	CancelButton.grid(row = 0, column = 0)


def GetMax(data, xloc, yloc, radius, background):
	stLoc = (yloc, xloc)
	clipLoc = numpy.clip(stLoc, radius, (data.shape[0] - radius, data.shape[1] - radius))
	crop = data[clipLoc[0]-radius : clipLoc[0]+radius,clipLoc[1]-radius : clipLoc[1]+radius]
	return int(numpy.max(crop) - background), numpy.std(crop)

def DrawCanvas(stLoc, radius, data):
	global Image, ImageCanvas, rig
	ImageFigure = matplotlib.figure.Figure(figsize = (2,2), dpi = 100)
	ImageAxis = ImageFigure.add_subplot(111)
	ImageAxis.set_axis_off()
	ImageFigure.subplots_adjust(0,0,1,1)
	ImageFigure.set_facecolor("black")
	clipLoc = numpy.clip(stLoc, radius, (data.shape[0] - radius, data.shape[1] - radius))
	crop = data[clipLoc[0]-radius : clipLoc[0]+radius,clipLoc[1]-radius : clipLoc[1]+radius]
	levels = STCore.DataManager.Levels
	Image = ImageAxis.imshow(crop, vmin = levels[1], vmax = levels[0], cmap=STCore.ImageView.ColorMaps[STCore.Settings._VISUAL_COLOR_.get()], norm = STCore.ImageView.Modes[STCore.Settings._VISUAL_MODE_.get()])
	ImageCanvas = FigureCanvasTkAgg(ImageFigure,master=ImageViewer)
	ImageCanvas.draw()
	wdg = ImageCanvas.get_tk_widget()
	wdg.configure(bg="black")
	wdg.config(cursor = "fleur")
	ImageCanvas.mpl_connect("button_press_event", OnMousePress) 
	ImageCanvas.mpl_connect("motion_notify_event", OnMouseDrag) 
	ImageCanvas.mpl_connect("button_release_event", OnMouseRelase) 
	wdg.grid(sticky = tk.NSEW)

def UpdateCanvas(data, stLoc, radius, mean):
	global Image, ImageCanvas, BrightLabel, ConfIcon
	radius = numpy.clip(radius, 2, min(data.shape))
	clipLoc = numpy.clip(stLoc, radius, (data.shape[0] - radius, data.shape[1] - radius))
	crop = data[clipLoc[0]-radius : clipLoc[0]+radius,clipLoc[1]-radius : clipLoc[1]+radius]
	Image.set_array(crop)
	confidence = int(min((numpy.max(crop))/ mean - 1, 1.0)*100)
	BrightLabel.config(text = "Confidencia: "+str(confidence)+"%")
	_conf = str(numpy.clip(int(confidence/30 + 1), 1, 3))
	ConfIcon.config(image = icons.Icons["conf"+_conf])
	ImageCanvas.draw_idle()

def Apply(name, loc, bounds, radius, Type, value, threshold, stars, OnStarChange, starIndex, sigma):

	st = StarItem()
	st.name = name
	st.type = Type
	st.location = loc
	st.bounds = bounds
	st.radius = radius
	st.value = value[0]
	st.std = value[1]
	st.threshold = (threshold * 0.01)
	st.bsigma = sigma
	if starIndex == -1:
		stars.append(st)
		STCore.Tracker.DataChanged = True
	else:
		stars[starIndex] = st
	OnStarChange()
	st.PrintData()
	CloseWindow()
	XLoc = YLoc = None

def CloseWindow():
	global Window, BrightLabel, ConfIcon
	Window.destroy()
	Window = None
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