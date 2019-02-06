import Tkinter as tk
import ttk
from matplotlib import figure, use
use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy
from STCore.utils.backgroundEstimator import GetBackground
#region  Variables
ResultsFrame = None

#endregion
# Funcion Awake, crea los objetos de tkinter
def Awake(root, ItemList, TrackedStars):
	global ResultsFrame
	ResultsFrame = tk.Frame(root)
	ResultsFrame.pack(fill = tk.BOTH, expand = 1)
	CreateCanvas(ResultsFrame, ItemList, TrackedStars)

def constant(ItemList,trackedPos,radius,Ref):
	pos = list(reversed(trackedPos[0]))
	data = ItemList[0].data
	clipLoc = numpy.clip(pos, radius, (data.shape[0] - radius, data.shape[1] - radius))
	crop = data[clipLoc[0]-radius : clipLoc[0]+radius,clipLoc[1]-radius : clipLoc[1]+radius]
	co=Ref+2.5*numpy.log10(numpy.sum(crop)/(radius**2)-GetBackground(data)[0])
	print co
	return co

# Esta funcion crea los objetos de matplotlib, desde la linea 23 hasta la 29 es igual que cualquier otro script
def CreateCanvas(app, ItemList, TrackedStars):
	viewer = tk.Frame(app, width = 700, height = 400, bg = "white")
	viewer.pack(side=tk.LEFT, fill = tk.BOTH, expand = True, anchor = tk.W)	  # Modifica desde aqui
	fig = figure.Figure(figsize = (7,4), dpi = 100)
	ax = fig.add_subplot(111)
	XAxis = range(len(ItemList))
#calculo de la constante, se ingresa la magnitud y se debe seleccionar la estrella correcta
	for s in TrackedStars:
		c=constant(ItemList,s.trackedPos,s.star.radius,0.0)
		break
	for t in TrackedStars:
		YAxis = GetTrackedValue(ItemList, t.trackedPos, t.star.radius,c)
		print YAxis
		Plot = ax.scatter(XAxis, YAxis)
	ax.invert_yaxis()	
	PlotCanvas = FigureCanvasTkAgg(fig,master=viewer)                        # Hasta aqui
	PlotCanvas.draw()
	PlotCanvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
	return PlotCanvas

# Esta funcion SOLO toma el brillo maximo de la estrella
# Utiliza los parametros ItemList: Lista de archivos (objetos FileItem), trackedPos: Lista de posiciones (fil, col)
# radius que es el valor dado por StarItem.radius (mira la linea 25)

def GetTrackedValue(ItemList, trackedPos, radius,constant):
	values=[]
	index = 0
	while index < len(ItemList):
		pos = list(reversed(trackedPos[index]))
		data = ItemList[index].data
		clipLoc = numpy.clip(pos, radius, (data.shape[0] - radius, data.shape[1] - radius))
		crop = data[clipLoc[0]-radius : clipLoc[0]+radius,clipLoc[1]-radius : clipLoc[1]+radius]
		#values.append(numpy.sum(crop)/(radius**2))
		values.append(constant-2.5*numpy.log10(numpy.sum(crop)/(radius**2)-GetBackground(data)[0]))
		index += 1
	return values
