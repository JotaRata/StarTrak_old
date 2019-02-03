# coding=utf-8
import numpy
import matplotlib
import Tkinter as tk
import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from STCore.item.Star import StarItem

#region Variables
Window = None
leftPanel = None
rightPanel = None
Image = None
ImageCanvas = None
ImageViewer = None
BrightLabel = None
#endregion

def Awake(root, Data, Brightness, Stars, OnStarChange, starIndex = -1, name = "Nueva Estrella", location = (20, 20),radius = 20, bounds = 80, Type = 0, threshold = 100):
	global Window, Image, ImageCanvas, leftPanel, rightPanel, ImageViewer, BrightLabel
	Window = tk.Toplevel()
	Window.wm_title(string = "Configurar Estrella")
	leftPanel = tk.Frame(Window)
	leftPanel.grid(row = 0,column = 0, sticky=tk.NS)
	rightPanel = tk.Frame(Window)
	rightPanel.grid(row=0,column = 1, sticky=tk.NS, padx = 20)

	nameFrame = tk.Frame(leftPanel)
	nameFrame.grid(row = 0, column = 0, sticky = tk.W)
	tk.Label(nameFrame, text = "Nombre de la estrella: ").grid(row = 0, column = 0, sticky = tk.W)
	StarName = tk.StringVar(Window, value = name)
	nameEntry = ttk.Entry(nameFrame, textvariable = StarName)
	nameEntry.grid (row =0,column = 1, sticky = tk.EW)
	
	typeSelection = tk.IntVar(Window, value = Type)
	typeFrame = tk.LabelFrame(leftPanel,text = "Tipo de Estrella")
	typeFrame.grid(row = 1, column = 0, columnspan = 1, sticky = tk.W + tk.E)
	ttk.Radiobutton(typeFrame, text = "Variable", variable = typeSelection, value = 0).grid(row = 0, sticky = tk.W)
	ttk.Radiobutton(typeFrame, text = "Referencia", variable = typeSelection, value = 1).grid (row = 1, sticky = tk.W)
	
	ImageViewer = tk.LabelFrame(rightPanel,text = "Vista previa")
	ImageViewer.grid(row = 0, column = 0, rowspan=2, sticky = tk.NSEW)
	DrawCanvas(location, radius, Data, Brightness)

	locFrame = tk.Frame(leftPanel)
	locFrame.grid(row = 2, column = 0, sticky = tk.EW)
	trackFrame = tk.LabelFrame(leftPanel, text = "Opciones de rastreo")
	trackFrame.grid(row = 3, column = 0, sticky = tk.EW)

	XLoc = tk.IntVar(locFrame, value = location[1])
	YLoc= tk.IntVar(locFrame, value = location[0])
	StarBounds = tk.IntVar(locFrame, value = bounds)
	StarRadius = tk.IntVar(locFrame, value = radius)
	StarThreshold = tk.IntVar(locFrame, value = threshold)

	tk.Label(locFrame, text = "Posicion:").grid(row = 3, column = 2, sticky = tk.W)
	XLocSpinBox = tk.Spinbox(locFrame, from_ = 0, to = Data.shape[1], textvariable = XLoc, width = 10)
	YLocSpinBox = tk.Spinbox(locFrame, from_ = 0, to = Data.shape[0], textvariable = YLoc, width = 10)
	RadiusSpinBox = tk.Spinbox(locFrame, from_ = 0, to = min(Data.shape), textvariable = StarRadius, width = 10)
	
	BoundSpinBox = tk.Spinbox(trackFrame, from_ = 0, to = min(Data.shape), textvariable = StarBounds, width = 10)
	ThreSpinBox = tk.Spinbox(trackFrame, from_ = 0, to = numpy.max(Data), textvariable = StarThreshold, width = 10)
	
	XLocSpinBox.grid(row = 3, column = 3)
	YLocSpinBox.grid(row = 3, column = 4, padx = 20)
	tk.Label(locFrame, text = "Tamaño de la estrella:").grid(row = 4, column = 2, sticky = tk.W)
	RadiusSpinBox.grid(row = 4, column = 3, columnspan = 2, sticky = tk.EW)
	

	tk.Label(trackFrame, text = "Radio de búsqueda:").grid(row = 5, column = 2, sticky = tk.W)
	BoundSpinBox.grid(row = 5, column = 3, columnspan = 1, sticky = tk.EW)
	tk.Label(trackFrame, text = "Tolerancia de busqueda:").grid(row = 6, column = 2, sticky = tk.W)
	ThreSpinBox.grid(row = 6, column = 3, columnspan = 1, sticky = tk.EW)
	BrightLabel = tk.Label(trackFrame, text = "Máximo brillo: ")
	BrightLabel.grid(row = 7, column = 2, sticky = tk.W)
	tk.Label(trackFrame, text = str(numpy.max(Image.get_array()))).grid(row = 7, column = 3, sticky = tk.W)

	cmd = lambda a,b,c : UpdateCanvas(Data,(int(YLoc.get()), int(XLoc.get())), int(StarRadius.get()))
	XLoc.trace("w",cmd)
	YLoc.trace("w",cmd)
	StarRadius.trace("w",cmd)
	
	applycmd = lambda: Apply(StarName.get(),(YLoc.get(), XLoc.get()), StarBounds.get(),
						 StarRadius.get() , typeSelection.get(),
						 GetMaxima(Data,XLoc.get(), YLoc.get(), StarRadius.get()), StarThreshold.get(),
						 Stars, OnStarChange, starIndex)
	controlButtons = tk.Frame(rightPanel)
	controlButtons.grid(row =3)
	ttk.Button(controlButtons, text = "Aceptar", command = applycmd).grid(row = 0, column = 1)
	ttk.Button(controlButtons, text = "Cancelar", command = Window.destroy).grid(row = 0, column = 0)

def GetMaxima(data, xloc, yloc, radius):
	stLoc = (yloc, xloc)
	clipLoc = numpy.clip(stLoc, radius, (data.shape[0] - radius, data.shape[1] - radius))
	crop = data[clipLoc[0]-radius : clipLoc[0]+radius,clipLoc[1]-radius : clipLoc[1]+radius]
	return numpy.max(crop)

def DrawCanvas(stLoc, radius, data, brightness):
	global Image, ImageCanvas, rig
	ImageFigure = matplotlib.figure.Figure(figsize = (2,2), dpi = 100)
	ImageAxis = ImageFigure.add_subplot(111)
	ImageAxis.set_axis_off()

	clipLoc = numpy.clip(stLoc, radius, (data.shape[0] - radius, data.shape[1] - radius))
	crop = data[clipLoc[0]-radius : clipLoc[0]+radius,clipLoc[1]-radius : clipLoc[1]+radius]

	Image = ImageAxis.imshow(crop, vmin = numpy.min(data), vmax = brightness, cmap="gray")
	ImageCanvas = FigureCanvasTkAgg(ImageFigure,master=ImageViewer)
	ImageCanvas.draw()
	ImageCanvas.get_tk_widget().grid(sticky = tk.NSEW)

def UpdateCanvas(data, stLoc, radius):
	global Image, ImageCanvas, BrightLabel
	radius = numpy.clip(radius, 2, min(data.shape))
	clipLoc = numpy.clip(stLoc, radius, (data.shape[0] - radius, data.shape[1] - radius))
	crop = data[clipLoc[0]-radius : clipLoc[0]+radius,clipLoc[1]-radius : clipLoc[1]+radius]
	Image.set_array(crop)
	BrightLabel.config(text = "Maximo brillo: "+str(int(numpy.max(crop))))
	ImageCanvas.draw()

def Apply(name, loc, bounds, radius, Type, value, threshold, stars, OnStarChange, starIndex):

	st = StarItem()
	st.name = name
	st.type = Type
	st.location = loc
	st.bounds = bounds
	st.radius = radius
	st.value = value
	st.threshold = threshold
	if starIndex == -1:
		stars.append(st)
	else:
		stars[starIndex] = st
	OnStarChange()
	Window.destroy()