import Tkinter as tk
import tkFileDialog
import ttk
import sys
from os.path import dirname, abspath, basename
sys.path.append(dirname(dirname(abspath(__file__))))

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
	ttk.Button(StartFrame, text = "Seleccionar Imagenes", command = lambda:LoadFiles(root)).pack(anchor = tk.CENTER)

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
	STCore.ImageView.Brightness = STCore.DataManager.Brightness
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
	if window == 3:
		Destroy()
		STCore.ImageSelector.Awake(win)
		STCore.ImageSelector.Destroy()
		STCore.Tracker.Awake(win, STCore.ImageView.Stars, STCore.ImageSelector.FilteredList, STCore.ImageView.Brightness)
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
	STCore.ImageView.Brightness = -1
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
	print "Window Reset"

if __name__ == "__main__":
	Window = tk.Tk()
	STCore.DataManager.Awake()
	STCore.DataManager.TkWindowRef = Window
	StartFrame = None
	Window.wm_title(string = "StarTrak v1.0.0")
	Window.geometry("1080x480")
	STCore.Settings.WorkingPath = dirname(dirname(abspath(__file__)))
	STCore.Settings.LoadSettings()
	Awake(Window)
	STCore.Tools.Awake(Window)
	Window.mainloop()
def GetWindow():
	return Window 
