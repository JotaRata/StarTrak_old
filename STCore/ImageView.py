from astropy.io import fits
import numpy
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.backends.tkagg as tkagg
from matplotlib.widgets import Slider
import Tkinter as tk
import ttk
from STCore.item.itemStar import ItemStar
import STCore.SetStar

def ImageClick(event):

	print maxval
	loc = (int(event.ydata), int(event.xdata))
	STCore.SetStar.CreateWindow(app, dat, maxval, stars, UpdateStarList, stLoc = loc)

def UpdateImage(val):
	global maxval
	maxval = float(val);
	im.norm.vmax = maxval
	fig.canvas.draw_idle()
	pltCanvas.draw_idle()
	if "_bLb" in globals():
		_bLb.config(text = "Brillo maximo: "+str(int(maxval)))

def CreateCanvas(app, ImageClick):
	viewer = tk.Frame(app, width = 700, height = 400, bg = "white")
	viewer.pack(side=tk.LEFT, fill = tk.BOTH, expand = True, anchor = tk.W)	

	fig = matplotlib.figure.Figure(figsize = (7,4), dpi = 100)
	ax = fig.add_subplot(111)
	im = ax.imshow(dat,vmin = 1000, vmax = numpy.max(dat), cmap="gray")
	pltCanvas = FigureCanvasTkAgg(fig,master=viewer)
	pltCanvas.draw()
	pltCanvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
	pltCanvas.mpl_connect('button_press_event',ImageClick)
	return pltCanvas, fig, im, viewer

def CreateSlider(UpdateImage):
	s = ttk.Scale(viewer, from_=numpy.min(dat), to=numpy.max(dat), orient=tk.HORIZONTAL, command = UpdateImage)
	s.set(numpy.max(dat))
	s.pack(fill = tk.X, anchor = tk.S, side = tk.BOTTOM)
	l = tk.Label(viewer, text = "Brillo maximo: "+str(numpy.max(dat)))
	l.pack(fill = tk.X, anchor = tk.S, side = tk.BOTTOM)
	return s, l

def CreateSidebar(app):
	_l = ttk.Label(text="Opciones de analisis")
	sidebar = tk.LabelFrame(app, relief=tk.RIDGE, width = 400, height = 400, labelwidget = _l)
	sidebar.pack(side = tk.RIGHT, expand = True, fill = tk.BOTH, anchor = tk.NE)

	starFrame = tk.Frame(sidebar)
	starFrame.pack(expand = 1, fill = tk.X, anchor = tk.NW)
	loc = (int(dat.shape[0] * 0.5), int (dat.shape[1] * 0.5))
	cmd = lambda : 	STCore.SetStar.CreateWindow(app, dat, maxval, stars, UpdateStarList, stLoc = loc)

	ttk.Button(sidebar, text = "Agregar estrella", command = cmd).pack()
	return sidebar, starFrame

def UpdateStarList():
	global starFrame
	for child in starFrame.winfo_children():
		child.destroy()
	index = 0
	for s in stars:
		_frame = tk.Frame(starFrame)
		_frame.pack(fill = tk.X, expand = 1, anchor = tk.N, pady = 5)

		cmd = __helperCreateWindow(index, stName = s.name, stLoc = s.location, stRad = s.radius, stType = s.type)
		cmd2= __helperPop(stars, index)
		ttk.Button(_frame, text = s.name, width = 10, command = cmd).pack(side = tk.LEFT, fill = tk.X, expand = 1)
		ttk.Button(_frame, text = "X", width = 1, command = cmd2).pack(side = tk.RIGHT)
		index += 1

#Las funciones lambda no se pueden llamar dentro de un loop for o while,
## para eso hay que crear una funcion que retorne un lambda
def __helperCreateWindow(index, stName, stLoc, stRad, stType):
	return lambda: STCore.SetStar.CreateWindow(app, dat, maxval, stars, UpdateStarList, index, stName, stLoc, stRad, stType)
def __helperPop (list, index):
	return lambda: (list.pop(index), UpdateStarList())

#Main Body
app = tk.Tk()
app.wm_title(string = "StarTrak v1.0.0")
tk.Label(text="Visor de Imagen").pack()
dat = fits.getdata("AEFor/aefor3.fit")
maxval = numpy.max(dat)
stars = []
pltCanvas, fig, im, viewer = CreateCanvas(app, ImageClick)
_bSld, _bLb = CreateSlider(UpdateImage)
sidebar, starFrame = CreateSidebar(app)
UpdateStarList()

app.mainloop()