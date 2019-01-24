from astropy.io import fits
from  numpy import min, max
from matplotlib import use, figure
use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle
import Tkinter as tk
import ttk
from STCore.item.Star import StarItem
from STCore import SetStar, Tracker
from STCore.utils.backgroundEstimator import GetBackground
#from STCore.utils import backgroundEstimator

#region Messages and Events

def OnImageClick(event):
	loc = (int(event.ydata), int(event.xdata))
	SetStar.CreateWindow(ViewerFrame, Data, Brightness, Stars, OnStarChange, stLoc = loc)

def OnStarChange():
	UpdateStarList()
	UpdateCanvasOverlay()
#endregion

#region Update Funcions

def UpdateStarList():
	global SidebarList
	for child in SidebarList.winfo_children():
		child.destroy()
	index = 0
	for s in Stars:
		_frame = tk.Frame(SidebarList)
		_frame.pack(fill = tk.X, expand = 1, anchor = tk.N, pady = 5)

		cmd = __helperCreateWindow(index, stName = s.name, stLoc = s.location, stRad = s.radius, stType = s.type)
		cmd2= __helperPop(Stars, index)
		ttk.Button(_frame, text = s.name, width = 10, command = cmd).pack(side = tk.LEFT, fill = tk.X, expand = 1)
		ttk.Button(_frame, text = "X", width = 1, command = cmd2).pack(side = tk.RIGHT)
		index += 1
#Las funciones lambda no se pueden llamar dentro de un loop for o while,
## para eso hay que crear una funcion que retorne un lambda
def __helperCreateWindow(index, stName, stLoc, stRad, stType):
	return lambda: SetStar.CreateWindow(ViewerFrame, Data, Brightness, Stars, OnStarChange, index, stName, stLoc, stRad, stType)
def __helperPop (list, index):
	return lambda: (list.pop(index), OnStarChange())

def UpdateCanvasOverlay():
	# Si se elimina el primer elemento de un lista en un ciclo for, entonces
	# ya no podra seguir iterando, lo que producir errores, se utiliza reversed para eliminar
	# el ultimo elemento de la lista primero y asi.
	for a in reversed(ImageAxis.artists):
		a.remove()
	for t in reversed(ImageAxis.texts):
		t.remove()
	for s in Stars:
		rect_pos = (s.location[1] - s.radius, s.location[0] - s.radius)
		rect = Rectangle(rect_pos, s.radius *2, s.radius *2, edgecolor = "w", facecolor='none')
		ImageAxis.add_artist(rect)
		text_pos = (s.location[1], s.location[0] - s.radius * 2)
		ImageAxis.annotate(s.name, text_pos, color='w', weight='bold',fontsize=6, ha='center', va='center')
	ImageCanvas.draw()

def UpdateImage(val):
	global Brightness
	Brightness = float(val);
	Image.norm.vmax = Brightness
	ImageCanvas.draw_idle()
	if SliderLabel is not None:
		SliderLabel.config(text = "Brillo maximo: "+str(int(Brightness)))
#endregion

#region Create Funcions

def CreateCanvas(app, ImageClick):
	viewer = tk.Frame(app, width = 700, height = 400, bg = "white")
	viewer.pack(side=tk.LEFT, fill = tk.BOTH, expand = True, anchor = tk.W)	

	fig = figure.Figure(figsize = (7,4), dpi = 100)
	ax = fig.add_subplot(111)
	im = ax.imshow(Data, vmin = min(Data), vmax = max(Data), cmap="gray")
	pltCanvas = FigureCanvasTkAgg(fig,master=viewer)
	pltCanvas.draw()
	pltCanvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
	pltCanvas.mpl_connect('button_press_event',ImageClick)
	return pltCanvas, im, viewer, ax

def CreateSlider(UpdateImage):
	s = ttk.Scale(ImageFrame, from_=min(Data), to=max(Data), orient=tk.HORIZONTAL, command = UpdateImage)
	s.set(max(Data))
	s.pack(fill = tk.X, anchor = tk.S, side = tk.BOTTOM)
	l = tk.Label(ImageFrame, text = "Brillo maximo: "+str(max(Data)))
	l.pack(fill = tk.X, anchor = tk.S, side = tk.BOTTOM)
	return l
def CreateSidebar(app, root, items):
	import STCore.ImageSelector
	_l = ttk.Label(text="Opciones de analisis")
	sidebar = tk.LabelFrame(app, relief=tk.RIDGE, width = 400, height = 400, labelwidget = _l)
	sidebar.pack(side = tk.RIGHT, expand = True, fill = tk.BOTH, anchor = tk.NE)

	list = tk.Frame(sidebar)
	list.pack(expand = 1, fill = tk.X, anchor = tk.NW)
	loc = (int(Data.shape[0] * 0.5), int (Data.shape[1] * 0.5))
	
	cmd = lambda : 	(Destroy(), STCore.ImageSelector.Awake(root, []))
	cmd2 = lambda : 	SetStar.CreateWindow(app, Data, Brightness, Stars, OnStarChange, stLoc = loc)
	cmdTrack = lambda : (Destroy(), Tracker.Awake(root, Stars, items))
	#Tracker.Track(fits.getdata("AEFor/aefor7.fit"), Stars, 4000)
	ttk.Button(sidebar, text = "Volver", command = cmd).pack(side = tk.LEFT)
	ttk.Button(sidebar, text = "Agregar estrella", command = cmd2).pack(side = tk.LEFT)
	ttk.Button(sidebar, text = "Analizar", command = cmdTrack).pack(side = tk.RIGHT)

	return sidebar, list
#endregion

#region Global Variables
ViewerFrame = None
Data = None
Brightness = 0
Stars = []
ImageCanvas = None
Image = None 
ImageFrame = None 
ImageAxis = None
Sidebar = None 
SidebarList = None
SliderLabel = None
#endregion

#region Main Body

def Awake(root, items):
	global ViewerFrame, Data, Brightness, Stars, ImageCanvas, Image, ImageFrame, ImageAxis, Sidebar, SidebarList, SliderLabel

	ViewerFrame = tk.Frame(root)
	ViewerFrame.pack( fill = tk.BOTH, expand = 1)
	tk.Label(ViewerFrame,text="Visor de Imagen").pack(fill = tk.X)
	Data =  items[0].data
	Brightness = max(Data)
	Stars = []
	ImageCanvas, Image, ImageFrame, ImageAxis = CreateCanvas(ViewerFrame, OnImageClick)
	SliderLabel = CreateSlider(UpdateImage)
	Sidebar, SidebarList = CreateSidebar(ViewerFrame, root, items)
	OnStarChange()

def Destroy():
	ViewerFrame.destroy()

#endregion