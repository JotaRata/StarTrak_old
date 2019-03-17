import Tkinter as tk
import tkFileDialog
import tkMessageBox
import ttk
import sys
from os.path import dirname, abspath, basename, isfile
try:
	sys.path.append(dirname(dirname(abspath(__file__))))
except NameError:  # We are the main py2exe script, not a module
	sys.path.append(dirname(dirname(abspath(sys.argv[0]))))
import STCore.ImageSelector
import STCore.Tools
import STCore.DataManager
import STCore.Settings
def Awake(root):
	global StartFrame
	STCore.DataManager.CurrentWindow = 0
	WindowName()
	StartFrame = tk.Frame(root, width = 1100, height = 400)
	STCore.Tracker.DataChanged = False
	StartFrame.pack(expand = 1, fill = tk.BOTH)
	tk.Label(StartFrame, text = "Bienvenido a StarTrak",font="-weight bold").pack()
	tk.Label(StartFrame, text = "Por favor seleccione las imagenes que quiera analizar").pack(anchor = tk.CENTER)
	ttk.Button(StartFrame, text = "   Seleccionar Imagenes   ", command = lambda:LoadFiles(root)).pack(anchor = tk.CENTER)
	tk.Label(StartFrame, text = "\n O tambien puede ").pack(anchor = tk.CENTER)
	ttk.Button(StartFrame, text = "   Abrir archivo   ", command = STCore.Tools.OpenFileCommand).pack(anchor = tk.CENTER)
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
		Window.wm_title(string = "StarTrak v1.0.0 - "+ basename(STCore.DataManager.CurrentFilePath))
	else:
		Window.wm_title(string = "StarTrak v1.0.0")
def LoadData(window):
	win = Window
	STCore.ImageSelector.ItemList = STCore.DataManager.FileItemList
	STCore.ImageView.Stars = STCore.DataManager.StarItemList
	STCore.Tracker.TrackedStars = STCore.DataManager.TrackItemList
	STCore.Tracker.DataChanged = False
	STCore.ResultsConfigurator.SettingsObject = STCore.DataManager.ResultSetting
	STCore.ImageView.Levels = STCore.DataManager.Levels
	STCore.Results.MagData = STCore.DataManager.ResultData
	if window == 0:
		# No hacer nada #
		return
	if window == 1:
		Destroy()
		STCore.ImageSelector.Awake(win)
		return
	if window == 2:
		Destroy()
		STCore.ImageSelector.Awake(win)
		STCore.ImageSelector.Apply(win)
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
	STCore.ImageView.Levels = -1
	STCore.Results.MagData = None
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
	print "Window Reset"

if __name__ == "__main__":
	Window = tk.Tk()
	STCore.DataManager.Awake()
	STCore.Settings.WorkingPath = dirname(abspath(__file__))
	STCore.DataManager.WorkingPath = dirname(abspath(__file__))
	STCore.DataManager.LoadRecent()
	STCore.DataManager.TkWindowRef = Window
	StartFrame = None
	Window.wm_title(string = "StarTrak v1.0.0")
	Window.geometry("1080x480")
	Window.iconbitmap("icon.ico")
	STCore.Settings.LoadSettings()
	Awake(Window)
	STCore.Tools.Awake(Window)
	if len(sys.argv) > 1:
		_helperLoadData(str(sys.argv[1]), Window)
	Window.mainloop()
def GetWindow():
	return Window 
