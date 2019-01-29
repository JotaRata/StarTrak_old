import tkinter as tk
import tkk
from matplotlib import figure, use
use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

#region  Variables
ResultsFrame = None

#endregion
def Awake(root, ItemList, TrackedStars):
	global ResultsFrame
	ResultsFrame = tk.Frame(root)
	ResultsFrame.pack(fill = tk.BOTH, expand = 1)

def CreateCanvas(app, ItemList, TrackedStars):
	viewer = tk.Frame(app, width = 700, height = 400, bg = "white")
	viewer.pack(side=tk.LEFT, fill = tk.BOTH, expand = True, anchor = tk.W)	
	fig = figure.Figure(figsize = (7,4), dpi = 100)
	ax = fig.add_subplot(111)
	XAxis = range(len(ItemList))
	YAxis = TrackedStars[0].trackedPos
	Plot = ax.scatter(XAxis, YAxis, vmin = min(Data), vmax = max(Data), cmap="gray")
	PlotCanvas = FigureCanvasTkAgg(fig,master=viewer)
	PlotCanvas.draw()
	PlotCanvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
	return PlotCanvas, Plot

