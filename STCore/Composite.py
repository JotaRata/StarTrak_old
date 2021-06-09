import tkinter as tk
from tkinter import ttk
import numpy
import scipy.ndimage
from matplotlib import use, figure
use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import STCore.Settings
from matplotlib.colors import LogNorm
from STCore.utils.Exporter import *
import STCore.DataManager
from time import time, sleep
import STCore.utils.Icons as icons
#region Variables
CompositeFrame = None
CompositeData = None
Img = None
ImgCanvas = None
_LEVEL_MIN_ = None
_LEVEL_MAX_ = None
_MODE_ = None
_COLOR_ = None
loadBar = None
prog = None
#endregion
def UpdateImage(ItemList):
	
		if _LEVEL_MIN_.get() >_LEVEL_MAX_.get():
			_LEVEL_MIN_.set(float(_LEVEL_MAX_.get()) + 0.01)
		Img.norm.vmax = float(_LEVEL_MAX_.get())
		Img.norm.vmin = float(_LEVEL_MIN_.get()) + 0.01
		Img.set_cmap(STCore.ImageView.ColorMaps[_COLOR_.get()])
		Img.set_norm(STCore.ImageView.Modes[_MODE_.get()])
		ImgCanvas.draw_idle()

def Awake(root, ItemList, TrackedStars):
	global CompositeFrame, _LEVEL_MIN_, _LEVEL_MAX_, _MODE_, _COLOR_, loadBar, prog
	STCore.DataManager.CurrentWindow = 5
	CompositeFrame = tk.Frame(root)
	CompositeFrame.pack(fill = tk.BOTH, expand = 1)
	prog = tk.DoubleVar()
	loadBar = CreateLoadBar(root, prog)
	canvas = CreateCanvas(ItemList, TrackedStars)
	loadBar[0].destroy()
	Sidebar = tk.Frame(CompositeFrame, width = 400)
	Sidebar.pack(side = tk.RIGHT, fill = tk.BOTH, anchor = tk.N, expand = 1)
	cmdBack = lambda: (Destroy(), STCore.Tracker.Awake(root, STCore.ImageView.Stars, ItemList))
	_LEVEL_MIN_ = tk.DoubleVar(value = numpy.min(canvas[2]))
	_LEVEL_MAX_ = tk.DoubleVar(value = numpy.max(canvas[2]))
	_LEVEL_MIN_.trace("w", lambda a,b,c: UpdateImage(ItemList))
	_LEVEL_MAX_.trace("w", lambda a,b,c: UpdateImage(ItemList))
	_MODE_ = STCore.Settings._VISUAL_MODE_
	_COLOR_ = STCore.Settings._VISUAL_COLOR_
	_COLOR_.trace("w", lambda a,b,c: UpdateImage(ItemList))
	_MODE_.trace("w", lambda a,b,c: UpdateImage(ItemList))
	#Exportmenu = tk.Menu(root, tearoff=0)
	#Exportmenu.add_command(label="Exportar grafico", command=lambda: ExportImage(canvas[1]))
	#Exportmenu.add_command(label="Exportar datos", command=lambda: ExportData(TrackedStars, canvas[2], GetTimeLabel(ItemList)))
	#Exportmenu.add_command(label="Exportar PDF", command=lambda: ExportPDF(canvas[1], canvas[2], TrackedStars))
	buttonFrame = tk.LabelFrame(Sidebar)
	buttonFrame.grid(row = 0,column = 0, columnspan = 2, sticky = tk.EW)
	exportbutton = ttk.Button(buttonFrame, text = " Exportar",image = icons.Icons["export"], compound = "left", command = lambda: Export(ItemList, canvas[2]))
	exportbutton.grid(row = 0, column = 1)
	ttk.Button(buttonFrame, text = " Volver",image = icons.Icons["prev"], compound = "left", command = cmdBack).grid(row = 0, column = 0)
	for c in range(3):
		tk.Grid.columnconfigure(Sidebar, c, weight=1)
	levelFrame = tk.LabelFrame(Sidebar, text = "Niveles:")
	levelFrame.grid(row = 1,column = 0, columnspan = 2, sticky = tk.EW)
	tk.Label(levelFrame, text = "Maximo:").grid(row = 0,column = 0)
	ttk.Scale(levelFrame, from_=numpy.min(canvas[2]), to=numpy.max(canvas[2]), orient=tk.HORIZONTAL, variable = _LEVEL_MAX_, length = 300).grid(row = 0, column = 1, columnspan = 1, sticky = tk.EW)
	tk.Label(levelFrame, text = "Minimo:").grid(row = 1,column = 0)
	ttk.Scale(levelFrame, from_=numpy.min(canvas[2]), to=numpy.max(canvas[2]), orient=tk.HORIZONTAL, variable = _LEVEL_MIN_, length = 300).grid(row = 1, column = 1, columnspan = 1, sticky = tk.EW)

	tk.Label(Sidebar, text = "Modo de Imagen:").grid(row = 2, column = 0, sticky = tk.W)
	ttk.OptionMenu(Sidebar, _MODE_,_MODE_.get(), *STCore.Settings.VisModes).grid(row = 2, column = 1, sticky = tk.E)
	tk.Label(Sidebar, text = "Mapa de color:").grid(row = 3, column = 0, sticky = tk.W)
	ttk.OptionMenu(Sidebar, _COLOR_,_COLOR_.get(), *STCore.Settings.VisColors).grid(row = 3, column = 1, sticky = tk.E)
	#ttk.Button(Sidebar, text = "Configurar", command = lambda: STCore.ResultsConfigurator.Awake(root, ItemList, TrackedStars)).grid(row = 2, column = 0)

def Export(ItemList, data):
	lmin = _LEVEL_MIN_.get()/float(len(ItemList)) + 0.01
	lmax =  _LEVEL_MAX_.get()/float(len(ItemList))
	imMin = numpy.min(ItemList[0].data)
	imMax = numpy.max(ItemList[0].data)
	ExportImageExt(data, _MODE_.get(), _COLOR_.get(), lmin, lmax, imMin, imMax)

def CreateCanvas(ItemList, TrackedStars):
	global CompositeFrame, Img, ImgCanvas
	fig = figure.Figure(figsize = (7,4), dpi = 100)
	data = Composite(ItemList, TrackedStars)
	ImgAxis = fig.add_subplot(111)
	fig.subplots_adjust(0.01,0,0.99,1)
	ImgAxis.set_axis_off()
	Img = ImgAxis.imshow(data, cmap = "gray") #, cmap=STCore.ImageView.ColorMaps[STCore.Settings._VISUAL_COLOR_.get()], norm = STCore.ImageView.Modes[STCore.Settings._VISUAL_MODE_.get()])
	ImgCanvas = FigureCanvasTkAgg(fig,master=CompositeFrame)
	if STCore.Settings._SHOW_GRID_.get() == 1:
		ImgAxis.grid()
	ImgCanvas.draw()
	wdg = ImgCanvas.get_tk_widget()
	wdg.pack(fill=tk.BOTH, expand=1, side = tk.LEFT)
	#wdg.wait_visibility()
	return ImgCanvas, fig, data

def Composite(ItemList, TrackedStars):
	
	data = Normalize(ItemList[0].data)
	i = 1
	track0 = TrackedStars[0]
	track1 = TrackedStars[1]
	rot = numpy.arctan2(-(numpy.array(track1.trackedPos[0])[1] - numpy.array(track0.trackedPos[0])[1]) , (numpy.array(track1.trackedPos[0])[0] - numpy.array(track0.trackedPos[0])[0]))
	while i < len(ItemList):
		deltaPos = numpy.array(track0.trackedPos[i]) - numpy.array(track0.trackedPos[0])
		newRot = numpy.arctan2(-(numpy.array(track1.trackedPos[i])[1] - numpy.array(track0.trackedPos[i])[1]) , (numpy.array(track1.trackedPos[i])[0] - numpy.array(track0.trackedPos[i])[0]))
		deltaRot = newRot - rot
		#deltaRot = numpy.radians(deltaRot)
		newdata = Normalize(ItemList[i].data)
		centerPos =  numpy.flip(numpy.array(track0.trackedPos[i]))
		deltaPos = -numpy.flip(numpy.array(deltaPos))
		#st = time()
		translation_matrix = numpy.array([[1, 0, -centerPos[0]], [0, 1, -centerPos[1]], [0, 0, 1]])
		translation_matrix_2 = numpy.array([[1, 0, -deltaPos[0]], [0, 1, -deltaPos[1]], [0, 0, 1]])
		rotation_matrix = numpy.array([[numpy.cos(-deltaRot), numpy.sin(-deltaRot), 0], [-numpy.sin(-deltaRot), numpy.cos(-deltaRot), 0], [0, 0, 1]])
		transform_matrix = translation_matrix_2.dot(numpy.linalg.inv(translation_matrix)).dot(rotation_matrix).dot(translation_matrix)
		newdata = scipy.ndimage.affine_transform(newdata, transform_matrix, order = 1, prefilter = False)
		#print "elapsed: ", time() -st
		#newdata = scipy.ndimage.shift(newdata, -centerPos)
		#newdata = scipy.ndimage.rotate(newdata, - deltaRot, reshape =False)	# Transofrmacion de Rotacion en un punto
		#newdata = scipy.ndimage.shift(newdata, centerPos)					#  M = T**(-1) * R * T
		#newdata = scipy.ndimage.shift(newdata, -numpy.array([numpy.sin(numpy.radians(deltaRot)), numpy.cos(numpy.radians(deltaRot))]))
		#newdata = scipy.ndimage.shift(newdata, -numpy.flip(numpy.array(deltaPos)))
		newdata.resize(data.shape)
		data = data + newdata
		prog.set(100*float(i)/len(ItemList))
		loadBar[0].update()
		sleep(0.001)
		i += 1
	return data

def Normalize(a):
	m = float(numpy.min (a))
	M = float(numpy.max(a))
	return numpy.abs((a - m) / (M - m))

def Destroy():
	global CompositeFrame
	CompositeFrame.destroy()

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