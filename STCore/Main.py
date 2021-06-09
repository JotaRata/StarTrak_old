# coding=utf-8
import Tkinter as tk
import tkFileDialog
import tkMessageBox
import ttk
import sys
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
def Awake(root):
	global StartFrame
	icons.Initialize()
	STCore.DataManager.CurrentWindow = 0
	WindowName()
	gc.collect()
	StartFrame = tk.Frame(root, width = 1100, height = 400)
	STCore.Tracker.DataChanged = False
	StartFrame.pack(expand = 1, fill = tk.BOTH)
	tk.Label(StartFrame, text = "Bienvenido a StarTrak",font="-weight bold").pack()
	tk.Label(StartFrame, text = "Por favor seleccione la accion que quiera realizar").pack(anchor = tk.CENTER)
	RunButton = tk.Button(StartFrame, text = "     Comenzar análisis     ",image = icons.Icons["run"], compound = "left",anchor="w", command = lambda: (STCore.RuntimeAnalysis.Awake(root)), width = 200)
	RunButton.pack(anchor = tk.CENTER)
	MultiButton = tk.Button(StartFrame, text = "     Seleccionar varias Imagenes     ",image = icons.Icons["multi"], compound = "left",anchor="w", command = lambda:LoadFiles(root), width = 200)
	MultiButton.pack(anchor = tk.CENTER)
	#tk.Label(StartFrame, text = "\n O tambien puede ").pack(anchor = tk.CENTER)
	OpenButton = tk.Button(StartFrame, text = "     Abrir archivo     ",image = icons.Icons["open"], compound = "left",anchor="w", command = STCore.Tools.OpenFileCommand, width = 200)
	OpenButton.pack(anchor = tk.CENTER)

	if STCore.Settings._RECENT_FILES_.get() == 1:
		recentlabel = tk.LabelFrame(StartFrame, text = "Archivos recientes:")
		recentlabel.pack(anchor = tk.CENTER)
		for p in reversed(STCore.DataManager.RecentFiles):
			l = tk.Label(recentlabel, text = p, fg = "blue", cursor="hand2")
			l.bind("<Button-1>", _helperOpenFile(p, root))
			l.pack(anchor = tk.CENTER)
def _helperOpenFile(path, root):
	return lambda e: _helperLoadData(path, root)
def _helperLoadData(path, root):
	if isfile(path):
		STCore.DataManager.LoadData(path)
	else:
		tkMessageBox.showerror("Error", "Este archivo ya no existe")
		STCore.DataManager.RecentFiles.remove(path)
		STCore.DataManager.SaveRecent()
		Destroy()
		Awake(root)
def LoadFiles(root):
	paths = tkFileDialog.askopenfilenames(parent = root, filetypes=[("FIT Image", "*.fits;*.fit"), ("Todos los archivos",  "*.*")])
	paths = root.tk.splitlist(paths)
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

		print "---------------------------"
		print "DirState: ", len(STCore.DataManager.RuntimeDirState)
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
	print "Window Reset"
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
	Window.mainloop()
def GetWindow():
	return Window 
