
import Tkinter as tk
import ttk
from PIL import Image, ImageTk
from astropy.io import fits
from os.path import basename
from time import sleep
#region Variables
SelectorFrame = None
activeList = []
#endregion
def Awake(root, paths):
	global SelectorFrame, activeList
	SelectorFrame = tk.Frame(root)
	SelectorFrame.pack(fill = tk.BOTH, expand = 1)
	tk.Label(SelectorFrame, text = "Seleccionar Imagenes").pack(fill = tk.X)
	ScrollView = tk.Canvas(SelectorFrame, scrollregion=(0,0, root.winfo_width(), len(paths)*220/4))
	ScrollBar = ttk.Scrollbar(SelectorFrame, command=ScrollView.yview)
	ScrollView.config(yscrollcommand=ScrollBar.set)  
	ScrollView.pack(expand = 1, fill = tk.BOTH, anchor = tk.NW, side = tk.LEFT)
	ScrollBar.pack(side = tk.LEFT,fill=tk.Y) 
	ImagesFrame = tk.Frame()
	ScrollView.create_window(0,0, anchor = tk.NW, window = ImagesFrame, width = root.winfo_width() - 120)
	index = 0

	progress = tk.DoubleVar()
	loadPopup, loadLabel, loadBar = CreateLoadBar(root, progress)
	activeList = [None]*len(paths)
	for p in sorted(paths):
		fr = tk.LabelFrame(ImagesFrame, width = 200, height = 200)
		row_, col = GridPlace(root, index, 250)
		fr.grid(row = row_, column = col, sticky = tk.NSEW, padx = 20, pady = 20)
		# Se usa open ya que la ruta esta en Unicode, que no se soporta en python
		file = open(p, 'rb')
		fit = fits.getdata(file).astype("uint8")
		pic = Image.fromarray(fit)
		pic.thumbnail((200, 200))
		img = ImageTk.PhotoImage(pic)
		tk.Label(fr, text=basename(file.name)).grid(row=0,column=0, sticky=tk.W)
		activeList[index] = tk.IntVar(ImagesFrame, value = 1)
		check = tk.Checkbutton(fr, variable = activeList[index])
		check.grid(row=0,column=1, sticky=tk.E)
		label = tk.Label(fr, image = img, width = 200, height = 200 * fit.shape[0]/float(fit.shape[1]))
		label.image = img
		label.grid(row=1,column=0, columnspan=2)
		# Barra de progreso
		progress.set(100*float(index)/len(paths))
		loadLabel.config(text="Cargando archivo "+str(index)+" de "+str(len(paths)))
		loadPopup.update()
		if index % 2 == 0:
			sleep(0.1)
		index += 1
	loadPopup.destroy()
	buttonFrame = tk.Frame(SelectorFrame)
	buttonFrame.pack(side = tk.RIGHT, anchor = tk.NE)
	ttk.Button(buttonFrame, text="Limpiar todo").grid(row=2, column=0, sticky = tk.EW, pady=5)
	ttk.Button(buttonFrame, text="Agregar archivo").grid(row=1, column=0, sticky = tk.EW, pady=5)
	ttk.Button(buttonFrame, text="Continuar").grid(row=0, column=0, sticky = tk.EW, pady=5)


def GridPlace(root, index, size):
	maxrows = root.winfo_height()/size
	maxcols = root.winfo_width()/size
	col = index
	row = 0
	while col >= maxcols:
		col -= maxcols
		row += 1
	return row, col

def CreateLoadBar(root, progress):
	popup = tk.Toplevel()
	popup.geometry("300x60+%d+%d" % (root.winfo_width()/2,  root.winfo_height()/2) )
	popup.wm_title(string = "Cargando..")
	popup.overrideredirect(1)
	pframe = tk.LabelFrame(popup)
	pframe.pack(fill = tk.BOTH, expand = 1)
	label = tk.Label(pframe, text="Cargando archivo..")
	bar = ttk.Progressbar(pframe, variable=progress, maximum=100)
	label.pack()
	bar.pack(fill = tk.X)
	return popup, label, bar

