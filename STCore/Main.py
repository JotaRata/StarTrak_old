# coding=utf-8
#en esta linea se cargan los modulos principales
#en esta linea se cargan los modulos principales
#en esta linea se cargan los modulos principales
try:
	print("Cargando modulos principales..", end=" ") #en esta linea se cargan los modulos principales
	import sys
	if sys.version_info < (3, 0):
		raise  SystemError("StarTrak debe ser ejecutado usando  Python3")
		
	from logging import log
	from os.path import dirname, abspath, basename, isfile
	import gc
	import warnings
	warnings.filterwarnings("ignore")	
	print ("Listo")
except:
	raise ImportError("StarTrak no pudo cargar los modulos del sistema.\nCompruebe su instalacion de python.")

try:
	print ("Iniciando modulos Tk..", end=" ")
	from tkinter import Toplevel, font
	from tkinter.filedialog import FileDialog
	import tkinter as tk
	from tkinter import filedialog
	from tkinter import messagebox
	from tkinter import ttk
	print ("Listo")
except:
	raise ImportError("No se pudo cargar los modulos de Tcl/Tk\nAsegurese que estos modulos esten activados en su instalacion de python.")

try:
	print("Iniciando NumPy..", end=" ")
	from numpy.lib.npyio import load
	print ("Listo")
except:
	raise ImportError("NumPy no se pudo cargar o no esta instalado\nAsegurate de instalar la ultima version de NumPy usando:\npip3 install numpy")

try:
	print("Iniciando MatplotLib..", end=" ")
	import matplotlib.pyplot as plt
	print ("Listo")
except:
	raise ImportError("MatplotLib no se pudo cargar o no esta instalado\nAsegurate de instalar la ultima version de MatplotLib usando:\npip3 install matplotlib")
try:
	print ("Iniciando AstroPy..", end=" ")
	from astropy.io.fits.card import HIERARCH_VALUE_INDICATOR
	from astropy.io.fits.convenience import info
	print ("Listo")
except:
	raise ImportError("AstroPy no se pudo cargar o no esta instalado\nAsegurate de instalar la ultima version de AstroPy usando:\npip3 install astropy")

try:
	print ("Iniciando PIL..", end=" ")
	from PIL import Image, ImageTk
	print ("Listo")
except:
	raise ImportError("No se pudo cargar Python Image Library\nAsegurate de instalarlo usando:\npip3 install pillow")

try:
	sys.path.append(dirname(dirname(abspath(__file__))))
except NameError:  # We are the main py2exe script, not a module
	sys.path.append(dirname(dirname(abspath(sys.argv[0]))))

try:
	print ("Cargando paquetes..", end=" ")
	import STCore.utils.Icons as icons
	from STCore import ImageSelector, ImageView, Results, Tracker, DataManager
	from STCore import Settings
	
	from STCore import Composite, ResultsConfigurator, RuntimeAnalysis, Tools
	print ("Listo")
except Exception as e:
	raise ImportError("Algunos archivos de StarTrak no existen o no pudieron ser cargados\nAsegurate de descargar la ultima version e intenta de nuevo\n", e)


print ("=" * 60)
	

def Awake(root):
	global StartFrame, sidebar, bottombar
	DataManager.CurrentWindow = 0

	WindowName()
	gc.collect()

	StartFrame = tk.Frame(root, width = 1100, height = 400, bg="gray18")
	Tracker.DataChanged = False
	StartFrame.pack(side = tk.RIGHT, anchor=tk.NE, expand = 1, fill = tk.BOTH)

	# Sidebar Area
	sidebar = tk.Frame(root, bg="gray15", width=400)
	sidebar.pack(side = tk.LEFT, anchor = tk.NW, fill = tk.Y, expand = 0)
	sidebar.pack_propagate(0)

	logo = ImageTk.PhotoImage(file ="STCore/StarTrak.png")
	logo_label = tk.Label(sidebar,image= logo, bg = "gray15")
	logo_label.image = logo
	logo_label.pack(pady=16)

	tk.Label(sidebar, text = "Bienvenido a StarTrak",font="-weight bold", bg = "gray15", fg = "gray80").pack(pady=16)
	
	# Bottombar Area

	bottombar = tk.Frame(StartFrame, bg ="gray18", height=64)
	bottombar.pack(expand=1, side=tk.BOTTOM, anchor=tk.SW, fill = tk.X)
	bottombar.pack_propagate(0)
	SessionButton = ttk.Button(bottombar, text = "Nueva Sesion",image = icons.GetIcon("run"), compound = "left", command = lambda: NewSessionTopLevel(root), width=32, style="Highlight.TButton")
	SessionButton.pack(side= tk.RIGHT, anchor = tk.E)
	FilesButton = ttk.Button(StartFrame, text = "Abrir Imagenes",image = icons.GetIcon("multi"), compound = "left", command = lambda:LoadFiles(root), width = 100)
	#FilesButton.pack()
	#tk.Label(StartFrame, text = "\n O tambien puede ").pack(anchor = tk.CENTER)
	LoadButton = ttk.Button(bottombar, text = "Cargar Sesion",image = icons.GetIcon("open"), compound = "left", command = Tools.OpenFileCommand, width=32)
	LoadButton.pack(side= tk.RIGHT, anchor = tk.E, after=SessionButton)

	# Right panel Area
	CreateRecent(root)


def CreateRecent(root):
	global StartFrame, recentlabel
	if Settings._RECENT_FILES_.get() == 1:
		recentlabel = tk.LabelFrame(StartFrame, text = "Archivos recientes:", bg="gray18", fg="gray90", relief="flat", font="-weight bold")
		recentlabel.pack(anchor = tk.NW, pady=16, expand=1, fill=tk.BOTH)

		ttk.Label(recentlabel).pack()
		for p in reversed(DataManager.RecentFiles):

			file_el = ttk.Button(recentlabel, text = p[0], cursor="hand2", style= "Highlight.TButton", command= lambda : _helperLoadData(p[1], root))
			#l.bind("<Button-1>", _helperOpenFile(p, root))
			file_el.pack(anchor = tk.W, pady=4, fill=tk.X)

			ttk.Button(file_el, image=icons.GetIcon("delete"), command=lambda:RemoveRecent(p, root), style="Highlight.TButton").pack(side=tk.RIGHT)
			
def _helperLoadData(path, root):
	if isfile(path):
		DataManager.LoadData(path)
	else:
		messagebox.showerror("Error", "Este archivo ya no existe")
		DataManager.RecentFiles.remove(path)
		DataManager.SaveRecent()
		Destroy()
		Awake(root)

def RemoveRecent(path, root):
	DataManager.RecentFiles.remove(path)
	DataManager.SaveRecent()
	recentlabel.destroy()
	
	CreateRecent(root)

def LoadFiles(root):
	paths = filedialog.askopenfilenames(parent = root, filetypes=[("FIT Image", "*.fits;*.fit"), ("Todos los archivos",  "*.*")])
	Destroy()
	ImageSelector.Awake(root, paths)

def Destroy():
	StartFrame.destroy()
	sidebar.destroy()
	bottombar.destroy()

def WindowName():
	if len(DataManager.CurrentFilePath) > 0:
		Window.wm_title(string = "StarTrak 1.1.0 - "+ basename(DataManager.CurrentFilePath))
	else:
		Window.wm_title(string = "StarTrak 1.1.0")


def LoadData(window):
	win = Window
	ImageSelector.ItemList = DataManager.FileItemList
	ImageView.Stars = DataManager.StarItemList
	Tracker.TrackedStars = DataManager.TrackItemList
	Tracker.DataChanged = False
	ResultsConfigurator.SettingsObject = DataManager.ResultSetting
	ImageView.level_perc = DataManager.Levels
	Results.MagData = DataManager.ResultData
	DataManager.RuntimeEnabled =  DataManager.RuntimeEnabled
	Results.Constant = 0
	Results.BackgroundFlux = 0
	if  DataManager.RuntimeEnabled == True:
		RuntimeAnalysis.directoryPath = DataManager.RuntimeDirectory
		RuntimeAnalysis.filesList = DataManager.FileItemList
		RuntimeAnalysis.startFile = ""
		RuntimeAnalysis.dirState = DataManager.RuntimeDirState

		print ("---------------------------")
		print ("DirState: ", len(DataManager.RuntimeDirState))
	else:
		RuntimeAnalysis.directoryPath = ""
		RuntimeAnalysis.dirState = []
		RuntimeAnalysis.filesList = []
		RuntimeAnalysis.startFile = ""
	if window == 0:
		# No hacer nada #
		return
	if window == 1:
		Destroy()
		ImageSelector.Awake(win)
		return

	if (window == 2) and DataManager.RuntimeEnabled == True:
		Destroy()
		ImageView.Awake(win)
		return

	if window == 2:
		Destroy()
		ImageSelector.Awake(win)
		ImageSelector.Apply(win)
		return

	if (window == 4 or window == 3) and DataManager.RuntimeEnabled == True:
		Destroy()
		Tracker.CurrentFile = 0
		Tracker.Awake(win, ImageView.Stars, DataManager.FileItemList)
		RuntimeAnalysis.StartRuntime(win)
		return
	if window == 3 or window == 5:
		Destroy()
		ImageSelector.Awake(win)
		ImageSelector.Destroy()
		Tracker.Awake(win, ImageView.Stars, ImageSelector.FilteredList)
		return
	if window == 4:
		Destroy()
		ImageSelector.Awake(win)
		ImageSelector.Destroy()
		Results.Awake(win, ImageSelector.FilteredList, Tracker.TrackedStars)
		return

def Reset():
	win = Window
	ResultsConfigurator.SettingsObject = None
	ImageSelector.ItemList = []
	Tracker.TrackedStars = []
	Tracker.CurrentFile = 0
	Tracker.DataChanged = False
	Tracker.ClearData()

	ImageView.level_perc = -1
	ImageView.ClearStars()
	ImageView.implot = None
	Results.MagData = None
	
	DataManager.RuntimeEnabled = False
	DataManager.Levels = -1
	DataManager.FileItemList = []
	DataManager.StarItemList = []
	
	Results.Constant = 0
	Results.BackgroundFlux = 0
	RuntimeAnalysis.directoryPath = ""
	RuntimeAnalysis.dirState = []
	RuntimeAnalysis.filesList = []
	RuntimeAnalysis.startFile = ""

	print ("Window Reset")
	if DataManager.CurrentWindow == 0:
		# No hacer nada #
		return
	if DataManager.CurrentWindow == 1:
		ImageSelector.Destroy()
		ImageSelector.ClearList(win)
		Awake(win)
		return
	if DataManager.CurrentWindow == 2:
		ImageView.Destroy()
		ImageView.ClearStars()
		Awake(win)
		return
	if DataManager.CurrentWindow == 3:
		Tracker.Destroy()
		Awake(win)
		return
	if DataManager.CurrentWindow == 4:
		Results.Destroy()
		Awake(win)
		return
	if DataManager.CurrentWindow == 5:
		Composite.Destroy()
		Awake(win)
		return

def NewSessionTopLevel(root):
	global sessionName
	Destroy()
	sessionType = -1
	top = tk.Toplevel(root)
	top.geometry("720x480+%d+%d" % (root.winfo_width()/2 + root.winfo_x() - 360,  root.winfo_height()/2 + root.winfo_y() - 240) )
	top.wm_title(string = "Nueva Sesion")
	#top.attributes('-topmost', 'true')
	#top.overrideredirect(1)
	
	TopFrame = ttk.Frame(top)
	TopFrame.pack(expand=1, fill=tk.BOTH)

	file_paths = []
	directory_path = ""
	load_frame = ttk.Frame(TopFrame)
	load_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1, pady=16)

	info_label = None

	def GetFilePaths():
		nonlocal file_paths, info_label
		file_paths = filedialog.askopenfilenames(parent = top, filetypes=[("FIT Image", "*.fits;*.fit"), ("Todos los archivos",  "*.*")])
		if info_label is not None:
			info_label.config(text="Se seleccionaron %o archivos" % len(file_paths))
	def GetDirectory():
		nonlocal directory_path, info_label
		directory_path = filedialog.askopenfilename(parent=top, filetypes=[("FIT Image", "*.fits;*.fit"), ("Todos los archivos",  "*.*")])
		if info_label is not None:
			info_label.config(text="Directorio de la sesion:\n"+dirname(directory_path))

	def SetSessionType(index, rtbutton, asbutton):
		nonlocal load_frame, sessionType, info_label
		sessionType = index
		
		rtcolor = "gray20"
		ascolor = "gray20"
		selectText = ""
		if index == 0:
			rtcolor="gray30"
			ascolor="gray20"
			
			for c in load_frame.winfo_children():
				c.destroy()
			ttk.Label(load_frame, text="Abrir la primera imagen de la sesion").pack()
			ttk.Button(load_frame, text="Arbir archivo", command=GetDirectory, width=28).pack()
		
		if index == 1:
			rtcolor ="gray20"
			ascolor ="gray30"

			for c in load_frame.winfo_children():
				c.destroy()
			
			ttk.Label(load_frame, text="Abrir varias imagenes").pack()
			ttk.Button(load_frame, text="Arbir archivos", command=GetFilePaths, width=28).pack()

		info_label = ttk.Label(load_frame, text = "")
		info_label.pack()

		rtbutton.config(bg=rtcolor)
		for c in rtbutton.winfo_children():
			c.config(bg=rtcolor)

		asbutton.config(bg=ascolor)
		for c in asbutton.winfo_children():
			c.config(bg=ascolor)

	def CloseLevel(wakemain = True):
		nonlocal root
		top.destroy()
		if wakemain:
			Awake(root)
	
	def Continue():
		nonlocal sessionType, root, file_paths, directory_path
		DataManager.SessionName = str(sessionName.get())
		if sessionType == 0:
			CloseLevel(False)
			RuntimeAnalysis.startFile = directory_path
			RuntimeAnalysis.Awake(root)
		if sessionType == 1:
			CloseLevel(False)
			Destroy()
			ImageSelector.Awake(root, file_paths)

	ttk.Label(TopFrame, text="Crear nueva sesion", font="-weight bold").pack(side=tk.TOP, anchor=tk.NW, fill=tk.X, pady=16, padx=8)
	ttk.Label(TopFrame, text="Nombre de la sesion").pack(side=tk.TOP, anchor=tk.N, fill=tk.X, pady=16, padx=16)
	sessionName = tk.StringVar(top, value="Nueva Sesion")
	entry = ttk.Entry(TopFrame, textvariable=sessionName)
	entry.pack(side=tk.TOP, anchor=tk.N, fill=tk.X, padx=32)

	rtsession = tk.Frame(TopFrame, relief=tk.FLAT, bg="gray18", height=4)
	rtsession.pack(anchor=tk.CENTER, fill=tk.X, pady=8)
	assession = tk.Frame(TopFrame, relief=tk.FLAT, bg="gray18", height=4)
	assession.pack(anchor=tk.CENTER, fill=tk.X, pady=8)

	rt_cmd = lambda e: SetSessionType(0, rtsession, assession)
	as_cmd = lambda e: SetSessionType(1, rtsession, assession)

	rtsession.bind('<Button-1>', rt_cmd)
	assession.bind('<Button-1>', as_cmd)

	rt_title = tk.Label(rtsession,text="Analisis en tiempo real", font="-weight bold", fg="gray80")
	rt_title.pack(side=tk.TOP)
	
	as_title = tk.Label(assession,text="Analisis asincrono", font="-weight bold", fg="gray80")
	as_title.pack(side=tk.TOP)
	
	rt_label = tk.Label(rtsession, text="Comienza un analisis fotometrico en tiempo real con el telescopio\nDebes seleccionar un archivo de muestra que se encuentre en la misma carpeta donde se exportaran los archivos FITS desde el CCD", fg="gray60")
	rt_label.pack(side=tk.BOTTOM)
	
	as_label = tk.Label(assession, text="Selecciona varias imagenes tomadas anteriormente para comenzar un analisis fotometrico de estas\nTambien puedes apilar estas imagenes", fg="gray60")
	as_label.pack(side=tk.BOTTOM)
	
	rt_title.bind('<Button-1>', rt_cmd)
	as_title.bind('<Button-1>', as_cmd)

	rt_label.bind('<Button-1>', rt_cmd)
	as_label.bind('<Button-1>', as_cmd)

	SetSessionType(-1, rtsession, assession)

	button_frame = ttk.Frame(top)
	button_frame.pack(side=tk.BOTTOM, fill=tk.X)

	ttk.Button(button_frame, text = "Continuar", style="Highlight.TButton", command=Continue, width=40).pack(side=tk.RIGHT, pady=16, padx=8)
	ttk.Button(button_frame, text = "Cancelar", command=CloseLevel, width=32).pack(side=tk.RIGHT, pady=16, padx=8)
	

def PreloadComponents():
	print ("Preloading components..")
	ImageView.BuildLayout(Window)
	Tracker.BuildLayout(Window)

if __name__ == "__main__":
	Window = tk.Tk()
	
	Window.configure(bg="black")
	Window.tk.call('lappend', 'auto_path', 'STCore/theme/awthemes-10.3.0')
	Window.tk.call('package', 'require', 'awdark')

	import Styles

	Settings.WorkingPath = dirname(abspath(__file__))
	DataManager.WorkingPath = dirname(abspath(__file__))
	icons.Initialize()
	DataManager.Awake()
	Settings.LoadSettings()
	Tools.Awake(Window)
	
	#print DataManager.WorkingPath
	DataManager.LoadRecent()
	DataManager.TkWindowRef = Window


	StartFrame = None
	Window.wm_title(string = "StarTrak 1.1.0")
	Window.geometry("1280x640")
	try:
		Window.iconbitmap(DataManager.WorkingPath+"/icon.ico")
	except:
		pass
	
	PreloadComponents()

	Window.after(20, Awake, Window)
	
	# Pre-initialize UI components
	
	if len(sys.argv) > 1:
		_helperLoadData(str(sys.argv[1]), Window)
	
	#print(style.theme_names())
	
	
	Window.mainloop()
def GetWindow():
	return Window 
