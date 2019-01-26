# coding=utf-8
import numpy
import matplotlib
import Tkinter as tk
import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from STCore.item.Star import StarItem
#import STCore.ImageView

#Star index = -1 para NUEVAS estrellas, > 0 para extrellas existentes
def CreateWindow(Root, Data, Brightness, Stars, OnStarChange, starIndex = -1, name = "Nueva Estrella", location = (20, 20),radius = 20, bounds = 80, Type = 0, threshold = 100):
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
	
	viewer = tk.LabelFrame(rightPanel,text = "Vista previa")
	viewer.grid(row = 0, column = 0, rowspan=2, sticky = tk.NSEW)
	fig, Img = DrawCanvas(rightPanel, location, radius, Data, Brightness)
	ImageCanvas = FigureCanvasTkAgg(fig,master=viewer)
	ImageCanvas.draw()
	ImageCanvas.get_tk_widget().grid(sticky = tk.NSEW)

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
	

	tk.Label(trackFrame, text = "Radio de busqueda:").grid(row = 5, column = 2, sticky = tk.W)
	BoundSpinBox.grid(row = 5, column = 3, columnspan = 1, sticky = tk.EW)
	tk.Label(trackFrame, text = "Tolerancia de busqueda:").grid(row = 6, column = 2, sticky = tk.W)
	ThreSpinBox.grid(row = 6, column = 3, columnspan = 1, sticky = tk.EW)
	BrightLabel = tk.Label(trackFrame, text = "Maximo brillo: ")
	BrightLabel.grid(row = 7, column = 2, sticky = tk.W)
	tk.Label(trackFrame, text = str(numpy.max(Img.get_array()))).grid(row = 7, column = 3, sticky = tk.W)

	cmd = lambda a,b,c : UpdateCanvas(Data, Img,(int(YLoc.get()), int(XLoc.get())), int(StarRadius.get()),ImageCanvas, BrightLabel)
	XLoc.trace("w",cmd)
	YLoc.trace("w",cmd)
	StarRadius.trace("w",cmd)
	
	applycmd = lambda: Apply(Window, StarName.get(),(YLoc.get(), XLoc.get()), StarBounds.get(),
						 StarRadius.get() , typeSelection.get(),
						 GetMaxima(Data,XLoc.get(), YLoc.get(), StarRadius.get()), StarThreshold.get(),
						 Stars, OnStarChange, starIndex)
	controlButtons = tk.Frame(rightPanel)
	controlButtons.grid(row =3)
	ttk.Button(controlButtons, text = "Aceptar", command = applycmd).grid(row = 0, column = 1)
	ttk.Button(controlButtons, text = "Cancelar", command = Window.destroy).grid(row = 0, column = 0)

def GetMaxima(data, xloc, yloc, radius):
	stLoc = (yloc, xloc)
	loc2 = numpy.clip(stLoc, radius, (data.shape[0] - radius, data.shape[1] - radius))
	crop = data[loc2[0]-radius : loc2[0]+radius,loc2[1]-radius : loc2[1]+radius]
	return numpy.max(crop)

def DrawCanvas(app, stLoc, radius, data, brightness):
	fig = matplotlib.figure.Figure(figsize = (2,2), dpi = 100)
	ax = fig.add_subplot(111)
	ax.set_axis_off()
	loc2 = numpy.clip(stLoc, radius, (data.shape[0] - radius, data.shape[1] - radius))
	crop = data[loc2[0]-radius : loc2[0]+radius,loc2[1]-radius : loc2[1]+radius]
	im = ax.imshow(crop, vmin = numpy.min(data), vmax = brightness, cmap="gray")
	return fig, im

def UpdateCanvas(data, im, stLoc, radius, pltCanvas, brightLabel):
	radius = numpy.clip(radius, 2, 1000000)
	loc2 = numpy.clip(stLoc, radius, (data.shape[0] - radius, data.shape[1] - radius))
	crop = data[loc2[0]-radius : loc2[0]+radius,loc2[1]-radius : loc2[1]+radius]
	im.set_array(crop)
	brightLabel.config(text = "Maximo brillo: "+str(int(numpy.max(crop))))
	pltCanvas.draw()

def Apply(window, name, loc, bounds, radius, Type, value, threshold, stars, OnStarChange, starIndex):

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
	st.PrintData()
	window.destroy()