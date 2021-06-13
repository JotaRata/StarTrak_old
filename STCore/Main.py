# coding=utf-8
import sys
if sys.version_info < (3, 0):
	print ("Star Trak debe iniciar con Python3")
	quit()


print ("\n Cargando StarTrak..")

import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk

from os.path import dirname, abspath, basename, isfile
import gc
try:
	sys.path.append(dirname(dirname(abspath(__file__))))
except NameError:  # We are the main py2exe script, not a module
	sys.path.append(dirname(dirname(abspath(sys.argv[0]))))
import STCore.ImageSelector
import STCore.Tools
import STCore.DataManager
import STCore.Settings
import STCore.RuntimeAnalysis
import STCore.utils.Icons as icons

print ("=" * 60)
	

def Awake(root):
	global StartFrame
	icons.Initialize()
	STCore.DataManager.CurrentWindow = 0
	WindowName()
	gc.collect()
	StartFrame = ttk.Frame(root, width = 1100, height = 400)
	STCore.Tracker.DataChanged = False
	StartFrame.pack(expand = 1, fill = tk.BOTH)
	ttk.Label(StartFrame, text = "Bienvenido a StarTrak",font="-weight bold").pack()
	ttk.Label(StartFrame, text = "Por favor seleccione la accion que quiera realizar").pack(anchor = tk.CENTER)
	RunButton = ttk.Button(StartFrame, text = "     Comenzar análisis     ",image = icons.Icons["run"], compound = "left", command = lambda: (STCore.RuntimeAnalysis.Awake(root)), width = 100)
	RunButton.pack(anchor = tk.CENTER)
	MultiButton = ttk.Button(StartFrame, text = "     Seleccionar varias Imagenes     ",image = icons.Icons["multi"], compound = "left", command = lambda:LoadFiles(root), width = 100)
	MultiButton.pack(anchor = tk.CENTER)
	#tk.Label(StartFrame, text = "\n O tambien puede ").pack(anchor = tk.CENTER)
	OpenButton = ttk.Button(StartFrame, text = "     Abrir archivo     ",image = icons.Icons["open"], compound = "left", command = STCore.Tools.OpenFileCommand, width = 100)
	OpenButton.pack(anchor = tk.CENTER)

	if STCore.Settings._RECENT_FILES_.get() == 1:
		recentlabel = tk.LabelFrame(StartFrame, text = "Archivos recientes:", bg="gray18", fg="gray90", relief="flat")
		recentlabel.pack(anchor = tk.CENTER, pady=64)
		for p in reversed(STCore.DataManager.RecentFiles):
			l = ttk.Label(recentlabel, text = p,foreground="blue", cursor="hand2")
			l.bind("<Button-1>", _helperOpenFile(p, root))
			l.pack(anchor = tk.CENTER)
def _helperOpenFile(path, root):
	return lambda e: _helperLoadData(path, root)
def _helperLoadData(path, root):
	if isfile(path):
		STCore.DataManager.LoadData(path)
	else:
		messagebox.showerror("Error", "Este archivo ya no existe")
		STCore.DataManager.RecentFiles.remove(path)
		STCore.DataManager.SaveRecent()
		Destroy()
		Awake(root)

def LoadFiles(root):
	paths = filedialog.askopenfilenames(parent = root, filetypes=[("FIT Image", "*.fits;*.fit"), ("Todos los archivos",  "*.*")])
	Destroy()
	STCore.ImageSelector.Awake(root, paths)

def Destroy():
	StartFrame.destroy()

def WindowName():
	if len(STCore.DataManager.CurrentFilePath) > 0:
		Window.wm_title(string = "StarTrak v1.1.0 - "+ basename(STCore.DataManager.CurrentFilePath))
	else:
		Window.wm_title(string = "StarTrak v1.1.0")
def LoadData(window):
	win = Window
	STCore.ImageSelector.ItemList = STCore.DataManager.FileItemList
	STCore.ImageView.Stars = STCore.DataManager.StarItemList
	STCore.Tracker.TrackedStars = STCore.DataManager.TrackItemList
	STCore.Tracker.DataChanged = False
	STCore.ResultsConfigurator.SettingsObject = STCore.DataManager.ResultSetting
	STCore.ImageView.Levels = STCore.DataManager.Levels
	STCore.Results.MagData = STCore.DataManager.ResultData
	STCore.DataManager.RuntimeEnabled =  STCore.DataManager.RuntimeEnabled
	STCore.Results.Constant = 0
	STCore.Results.BackgroundFlux = 0
	if  STCore.DataManager.RuntimeEnabled == True:
		STCore.RuntimeAnalysis.directoryPath = STCore.DataManager.RuntimeDirectory
		STCore.RuntimeAnalysis.filesList = STCore.DataManager.FileItemList
		STCore.RuntimeAnalysis.startFile = ""
		STCore.RuntimeAnalysis.dirState = STCore.DataManager.RuntimeDirState

		print ("---------------------------")
		print ("DirState: ", len(STCore.DataManager.RuntimeDirState))
	else:
		STCore.RuntimeAnalysis.directoryPath = ""
		STCore.RuntimeAnalysis.dirState = []
		STCore.RuntimeAnalysis.filesList = []
		STCore.RuntimeAnalysis.startFile = ""
	if window == 0:
		# No hacer nada #
		return
	if window == 1:
		Destroy()
		STCore.ImageSelector.Awake(win)
		return

	if (window == 2) and STCore.DataManager.RuntimeEnabled == True:
		Destroy()
		STCore.ImageView.Awake(win, STCore.DataManager.FileItemList)
		return

	if window == 2:
		Destroy()
		STCore.ImageSelector.Awake(win)
		STCore.ImageSelector.Apply(win)
		return

	if (window == 4 or window == 3) and STCore.DataManager.RuntimeEnabled == True:
		Destroy()
		STCore.Tracker.CurrentFile = 0
		STCore.Tracker.Awake(win, STCore.ImageView.Stars, STCore.DataManager.FileItemList)
		STCore.RuntimeAnalysis.StartRuntime(win)
		return
	if window == 3 or window == 5:
		Destroy()
		STCore.ImageSelector.Awake(win)
		STCore.ImageSelector.Destroy()
		STCore.Tracker.Awake(win, STCore.ImageView.Stars, STCore.ImageSelector.FilteredList)
		return
	if window == 4:
		Destroy()
		STCore.ImageSelector.Awake(win)
		STCore.ImageSelector.Destroy()
		STCore.Results.Awake(win, STCore.ImageSelector.FilteredList, STCore.Tracker.TrackedStars)
		return

def Reset():
	win = Window
	STCore.ResultsConfigurator.SettingsObject = None
	STCore.ImageSelector.ItemList = []
	STCore.ImageView.ClearStars()
	STCore.Tracker.TrackedStars = []
	STCore.Tracker.CurrentFile = 0
	STCore.ImageView.Levels = -1
	STCore.Results.MagData = None
	STCore.DataManager.RuntimeEnabled = False
	STCore.Results.Constant = 0
	STCore.Results.BackgroundFlux = 0
	STCore.RuntimeAnalysis.directoryPath = ""
	STCore.RuntimeAnalysis.dirState = []
	STCore.RuntimeAnalysis.filesList = []
	STCore.RuntimeAnalysis.startFile = ""
	STCore.Tracker.DataChanged = False
	print ("Window Reset")
	if STCore.DataManager.CurrentWindow == 0:
		# No hacer nada #
		return
	if STCore.DataManager.CurrentWindow == 1:
		STCore.ImageSelector.Destroy()
		STCore.ImageSelector.ClearList(win)
		Awake(win)
		return
	if STCore.DataManager.CurrentWindow == 2:
		STCore.ImageView.Destroy()
		STCore.ImageView.ClearStars()
		Awake(win)
		return
	if STCore.DataManager.CurrentWindow == 3:
		STCore.Tracker.Destroy()
		Awake(win)
		return
	if STCore.DataManager.CurrentWindow == 4:
		STCore.Results.Destroy()
		Awake(win)
		return
	if STCore.DataManager.CurrentWindow == 5:
		STCore.Composite.Destroy()
		Awake(win)
		return
	

if __name__ == "__main__":
	Window = tk.Tk()
	style =ttk.Style(Window)
	Window.configure(bg="black")
	Window.tk.call('lappend', 'auto_path', 'STCore/theme/awthemes-10.3.0')
	Window.tk.call('package', 'require', 'awdark')

	STCore.DataManager.Awake()
	STCore.Settings.WorkingPath = dirname(abspath(__file__))
	STCore.DataManager.WorkingPath = dirname(abspath(__file__))
	#print STCore.DataManager.WorkingPath
	STCore.DataManager.LoadRecent()
	STCore.DataManager.TkWindowRef = Window
	StartFrame = None
	Window.wm_title(string = "StarTrak v1.1.0")
	Window.geometry("1280x640")
	Window.iconbitmap(STCore.DataManager.WorkingPath+"/icon.ico")
	STCore.Settings.LoadSettings()
	Awake(Window)
	STCore.Tools.Awake(Window)
	if len(sys.argv) > 1:
		_helperLoadData(str(sys.argv[1]), Window)
	
	#print(style.theme_names())
	
	style.theme_use("awdark")
	style.configure("Vertical.TScrollbar", gripcount=3,
                background="#367783", lightcolor="gray35",
                troughcolor="gray18", bordercolor="gray10", arrowcolor="azure2", relief ="flat",
				width="20", borderwidth = 0)
	style.map("Vertical.TScrollbar",
		background=[ ('!active','#367783'),('pressed', '#49A0AE'), ('active', '#49A0AE')]
		)

	style.configure("Horizontal.TScale", gripcount=3,
                background="#49A0AE", lightcolor="gray35",
                troughcolor="gray8", bordercolor="gray10", arrowcolor="azure2", relief ="flat",
				width="20", borderwidth = 0)
	style.map("Horizontal.TScale",
		background=[ ('!active','#49A0AE'),('pressed', '#49A0AE'), ('active', '#49A0AE')]
		)
	style.configure("TFrame", background = "gray15", relief="flat")
	style.configure("TLabel", background = "gray15", foreground ="gray80")
	style.configure("TLabelFrame", background = "gray15", highlightcolor="gray15")

	style.configure("TButton", relief = "flat")
	style.map("TButton",
		foreground=[('!active', 'gray90'),('pressed', 'gray95'), ('active', 'gray90')],
		background=[ ('!active','grey20'),('pressed', 'gray26'), ('active', 'gray24')]
		)	
	Window.mainloop()
def GetWindow():
	return Window 
