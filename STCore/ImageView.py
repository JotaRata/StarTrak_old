from astropy.io import fits
import numpy
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import Slider

import Tkinter as tkinter

maxval = 7000
fig = matplotlib.figure.Figure(figsize=(5,5), dpi=100)
ax = fig.add_subplot(111)
dat = fits.getdata("AEFor/aefor3.fit")
im = ax.imshow(dat,vmin = 1000, vmax = maxval, cmap="gray")
canvas = None
def ImageClick(event):
	if event.inaxes is not None:
		print event.xdata, event.ydata
	else:
		print ('Clicked ouside axes bounds but inside plot window')

def UpdateImage(val):
	maxval = int(val);
	im.set_data(dat)
	im.norm.vmax = maxval
	fig.canvas.draw_idle()
	canvas.draw_idle()

app = tkinter.Tk()
label = tkinter.Label( text="Visor de Imagen")
label.pack()
canvas = FigureCanvasTkAgg(fig,master=app)
canvas.draw()
canvas.get_tk_widget().pack(side=tkinter.BOTTOM, fill=tkinter.BOTH, expand=True)
canvas.callbacks.connect('button_press_event', ImageClick)
w = tkinter.Scale(app, from_=1100, to=16000, orient=tkinter.HORIZONTAL, command = UpdateImage)
w.pack()

app.mainloop()