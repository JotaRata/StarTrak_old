import numpy
import matplotlib
import Tkinter as tk
import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from STCore.item.Star import StarItem
#import STCore.ImageView

#Star index = -1 para NUEVAS estrellas, > 0 para extrellas existentes
def CreateWindow(Root, Data, Brightness, Stars, OnStarChange, starIndex = -1,stName = "Nueva Estrella", stLoc = (20, 20), stRad = 20, stType = 0):
	Win = tk.Toplevel()
	Win.wm_title(string = "Configurar Estrella")
	leftPanel = tk.Frame(Win)
	leftPanel.grid(row = 0,column = 0, sticky=tk.NS)
	rightPanel = tk.Frame(Win)
	rightPanel.grid(row=0,column = 1, sticky=tk.NS, padx = 20)

	nameFrame = tk.Frame(leftPanel)
	nameFrame.grid(row = 0, column = 0, sticky = tk.W)
	tk.Label(nameFrame, text = "Nombre de la estrella: ").grid(row = 0, column = 0, sticky = tk.W)
	sName = tk.StringVar(Win, value = stName)
	nameEntry = ttk.Entry(nameFrame, textvariable = sName)
	nameEntry.grid (row =0,column = 1, sticky = tk.EW)
	
	typeSelection = tk.IntVar(Win, value = stType)
	typeFrame = tk.LabelFrame(leftPanel,text = "Tipo de Estrella")
	typeFrame.grid(row = 1, column = 0, columnspan = 1, sticky = tk.W + tk.E)
	ttk.Radiobutton(typeFrame, text = "Variable", variable = typeSelection, value = 0).grid(row = 0, sticky = tk.W)
	ttk.Radiobutton(typeFrame, text = "Referencia", variable = typeSelection, value = 1).grid (row = 1, sticky = tk.W)
	
	viewer = tk.LabelFrame(rightPanel,text = "Vista previa")
	viewer.grid(row = 0, column = 0, rowspan=2, sticky = tk.NSEW)
	fig, im = DrawCanvas(rightPanel, stLoc, stRad, Data, Brightness)
	pltCanvas = FigureCanvasTkAgg(fig,master=viewer)
	pltCanvas.draw()
	pltCanvas.get_tk_widget().grid(sticky = tk.NSEW)

	locFrame = tk.Frame(leftPanel)
	locFrame.grid(row = 2, column = 0, sticky = tk.W)
	xloc = tk.StringVar(locFrame, value = str(stLoc[1]))
	yloc= tk.StringVar(locFrame, value = str(stLoc[0]))
	radius = tk.StringVar(locFrame, value = str(stRad))
	_bLb = tk.Label(locFrame, text = "Maximo brillo: "+ str(numpy.max(im.get_array())))
	_bLb.grid(row = 5, column = 2, sticky = tk.EW)

	tk.Label(locFrame, text = "Posicion:").grid(row = 3, column = 2, sticky = tk.W)
	cmd = lambda a,b,c : UpdateCanvas(Data, im,(int(yloc.get()), int(xloc.get())), int(radius.get()),pltCanvas, _bLb)
	_xSp = tk.Spinbox(locFrame, from_ = 0, to = Data.shape[1], textvariable = xloc, width = 10)
	_ySp = tk.Spinbox(locFrame, from_ = 0, to = Data.shape[0], textvariable = yloc, width = 10)
	_rad = tk.Spinbox(locFrame, from_ = 0, to = min(Data.shape), textvariable = radius, width = 10)

	_xSp.grid(row = 3, column = 3)
	_ySp.grid(row = 3, column = 4, padx = 20)
	tk.Label(locFrame, text = "Radio de busqueda:").grid(row = 4, column = 2, sticky = tk.W)
	_rad.grid(row = 4, column = 3, columnspan = 2, sticky = tk.EW)

	xloc.trace("w",cmd)
	yloc.trace("w",cmd)
	radius.trace("w",cmd)
	
	applycmd = lambda: Apply(Win, sName.get(),(int(yloc.get()), int(xloc.get())), int(radius.get())
						  , typeSelection.get(),
						 GetMaxima(Data,int(xloc.get()), int(yloc.get()), int(radius.get())),
						 Stars, OnStarChange, starIndex)
	
	controlButtons = tk.Frame(rightPanel)
	controlButtons.grid(row =3)
	ttk.Button(controlButtons, text = "Aceptar", command = applycmd).grid(row = 0, column = 1)
	ttk.Button(controlButtons, text = "Cancelar", command = Win.destroy).grid(row = 0, column = 0)

def GetMaxima(data, xloc, yloc, radius):
	vloc = numpy.clip((xloc,yloc), radius, (data.shape[0] - radius, data.shape[1] - radius))
	return  numpy.max(data[vloc[0]-radius : vloc[0]+radius,vloc[1]-radius : vloc[1]+radius])

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

def Apply(window, stName, stLoc, stRad, stType, sval, stars, OnStarChange, starIndex):

	st = StarItem()
	st.name = stName
	st.type = stType
	st.location = stLoc
	st.radius = stRad
	st.value = sval
	if starIndex == -1:
		stars.append(st)
	else:
		stars[starIndex] = st
	OnStarChange()
	window.destroy()