
import Tkinter as tk
import ttk
from PIL import Image, ImageTk
from astropy.io import fits
from os.path import basename
from time import sleep
import tkFileDialog
import tkMessageBox
from STCore.item.File import FileItem
import STCore.ImageView
#region Variables
SelectorFrame = None
ImagesFrame = None
ScrollView = None
ItemList = []
#endregion

def LoadFiles(paths, root):
	index = 0
	listSize = len(ItemList)
	progress = tk.DoubleVar()
	loadPopup, loadLabel, loadBar = CreateLoadBar(root, progress)
	for p in sorted(paths, key=lambda f: int(filter(str.isdigit, str(f)))):
		item = FileItem()
		item.path = str(p)
		item.data = fits.getdata(item.path)
		item.active = tk.IntVar(value=1)
		ItemList.append(item)
		CreateFileGrid(index + listSize, item, root)
		# Barra de progreso
		progress.set(100*float(index)/len(paths))
		loadLabel.config(text="Cargando archivo "+str(index)+" de "+str(len(paths)))
		loadPopup.update()
		if index % 2 == 0:
			sleep(0.1)
		index += 1
	loadPopup.destroy()
	ScrollView.config(scrollregion=(0,0, root.winfo_width(), len(ItemList)*240/4))

def Awake(root, paths):
	global SelectorFrame, ItemList, ImagesFrame, ScrollView
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

	if len(ItemList) != 0 and len(paths) == 0:
		ind = 0
		while ind < len(ItemList):
			CreateFileGrid(ind, ItemList[ind], root)
			ind += 1
	else:
		LoadFiles(paths, root)
	
	buttonFrame = tk.Frame(SelectorFrame)
	buttonFrame.pack(side = tk.RIGHT, anchor = tk.NE)
	ttk.Button(buttonFrame, text="Limpiar todo", command = lambda: ClearList(root)).grid(row=2, column=0, sticky = tk.EW, pady=5)
	ttk.Button(buttonFrame, text="Agregar archivo", command = lambda: AddFiles(root)).grid(row=1, column=0, sticky = tk.EW, pady=5)
	ttk.Button(buttonFrame, text="Continuar", command = lambda: Apply(root)).grid(row=0, column=0, sticky = tk.EW, pady=5)


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

def CreateFileGrid(index, item, root):
	GridFrame = tk.LabelFrame(ImagesFrame, width = 200, height = 200)
	Row, Col = GridPlace(root, index, 250)
	GridFrame.grid(row = Row, column = Col, sticky = tk.NSEW, padx = 20, pady = 20)
	Pic = Image.fromarray(item.data.astype("uint8"))
	Pic.thumbnail((200, 200))
	Img = ImageTk.PhotoImage(Pic)
	tk.Label(GridFrame, text=basename(item.path)).grid(row=0,column=0, sticky=tk.W)
	Ckeckbox = tk.Checkbutton(GridFrame, variable = ItemList[index].active)
	Ckeckbox.grid(row=0,column=1, sticky=tk.E)
	ImageLabel = tk.Label(GridFrame, image = Img, width = 200, height = 200 * item.data.shape[0]/float(item.data.shape[1]))
	ImageLabel.image = Img
	ImageLabel.grid(row=1,column=0, columnspan=2)

def Apply(root):
	FList = filter(lambda item: item.active.get() == 1, ItemList)
	if len(FList) == 0:
		tkMessageBox.showerror("Error", "Debe seleccionar al menos un archivo")
		return
	Destroy()
	STCore.ImageView.Awake(root, FList)

def ClearList(root):
	global ItemList
	for i in ItemList:
		del i
	ItemList = []
	ScrollView.config(scrollregion=(0,0, root.winfo_width(), 1))
	for child in ImagesFrame.winfo_children():
		child.destroy()

def AddFiles(root):
	paths = tkFileDialog.askopenfilenames(parent = root, filetypes=[("FIT Image", "*.fits;*.fit")])
	paths = root.tk.splitlist(paths)
	LoadFiles(paths, root)

def Destroy():
	SelectorFrame.destroy()