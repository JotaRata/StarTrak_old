from astropy.io import fits
import numpy
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.backends.tkagg as tkagg
from matplotlib.widgets import Slider
import Tkinter as tk
import ttk

def ImageClick(event):
	print event.x, event.y
	canvas.create_circle(event.x, event.y, 24, outline = "white")

def Create_circle(self,x, y, r, **kwargs):
    return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
tk.Canvas.create_circle = Create_circle

def UpdateImage(val):
	maxval = float(val);
	im.norm.vmax = maxval
	fig.canvas.draw_idle()
	figImage = DisplayImage(canvas, fig)
	if "_bLb" in globals():
		_bLb.config(text = "Brillo maximo: "+str(int(maxval)))

def DisplayImage(canvas, figure):
	pltCanvas.draw()
	figure_x, figure_y, figure_w, figure_h = figure.bbox.bounds
	figure_w, figure_h = int(figure_w), int(figure_h)
	canvas.itemconfig(canvasImage, image = figImage)
	tkagg.blit(figImage, pltCanvas.get_renderer()._renderer, colormode=2)

def CreateCanvas(app, ImageClick):
	viewer = tk.Frame(app, width = 700, height = 400, bg = "white")
	viewer.pack(side=tk.LEFT, fill = tk.BOTH, expand = True, anchor = tk.W)	
	canvas = tk.Canvas(viewer, width=700, height=400, borderwidth=0, highlightthickness=0, bg="white")
	canvas.bind("<Button-1>", ImageClick)
	canvas.pack(anchor = tk.W, expand = True, fill = tk.BOTH)
	
	figImage = tk.PhotoImage(master=canvas, width=700, height=400)
	fig = matplotlib.figure.Figure(figsize = (7,4), dpi = 100)
	ax = fig.add_subplot(111)
	im = ax.imshow(dat,vmin = 1000, vmax = numpy.max(dat), cmap="gray")
	pltCanvas = FigureCanvasTkAgg(fig,master=app)
	canvasImage = canvas.create_image(700/2, 400/2, tag = "Image")
	return canvas, canvasImage, fig, figImage, im, pltCanvas, viewer

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
	
	ttk.Button(sidebar, text = "Agregar estrella").pack()
	return sidebar

#Main Body
app = tk.Tk()
tk.Label(text="Visor de Imagen").pack()
dat = fits.getdata("AEFor/aefor3.fit")

canvas, canvasImage, fig, figImage, im, pltCanvas, viewer = CreateCanvas(app, ImageClick)

DisplayImage(canvas, fig)
_bSld, _bLb = CreateSlider(UpdateImage)
CreateSidebar(app)


app.mainloop()