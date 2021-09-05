import tkinter as tk
from tkinter import ttk
from STCore.item.ResultSettings import ResultSetting
import STCore.Tracker, STCore.Results, STCore.DataManager
import numpy
#region variables
ConfiguratorFrame = None
SettingsObject = None
PlotWindow = None

_SORTINGMODE_ = None
_DELTRACKS_ = None
_DELERROR_ = None
_REFSTAR_ = None
_REFVALUE_ = None
_XTICKS_ = None
_TIMELENGHT_ = None
#endregion
def Clear():
	global SettingsObject, _SORTINGMODE_, _DELTRACKS_, _DELERROR_, _REFSTAR_, _REFVALUE_, _XTICKS_, _TIMELENGHT_
	_SORTINGMODE_ = None
	_DELTRACKS_ = None
	_DELERROR_ = None
	_REFSTAR_ = None
	_REFVALUE_ = None
	_XTICKS_ = None
	_TIMELENGHT_ = None
def Load():
	Clear()
	global SettingsObject, _SORTINGMODE_, _DELTRACKS_, _DELERROR_, _REFSTAR_, _REFVALUE_, _XTICKS_, _TIMELENGHT_
	if SettingsObject is None:
		SettingsObject = ResultSetting()
	try:
		_SORTINGMODE_ = tk.IntVar(value = SettingsObject.sortingMode)
		_DELTRACKS_ = tk.IntVar(value = SettingsObject.delLostTracks)
		_DELERROR_ = tk.IntVar(value = SettingsObject.delError)
		_REFSTAR_ = tk.IntVar(value = SettingsObject.refStar)
		_REFVALUE_ = tk.StringVar(value = SettingsObject.refValue)
		_XTICKS_ = tk.IntVar(value = SettingsObject.tickNumber)
		_TIMELENGHT_ = tk.IntVar(value = SettingsObject.timeLenght/60)
	except:
		print ("Inavelid or Outdated Result Setting Object, creating a new one from scratch..")
		SettingsObject = None
		Load()
		pass
def CheckWindowClear():
	value = PlotWindow == None or not tk.Toplevel.winfo_exists(PlotWindow)
	print ("Result Window Cleared: ", value)
	return value

def Apply(root, ItemList, TrackedStars):
	global SettingsObject, _SORTINGMODE_, _DELTRACKS_, _DELERROR_, _REFSTAR_, _REFVALUE_, _XTICKS_, PlotWindow, _TIMELENGHT_
	SettingsObject.sortingMode = _SORTINGMODE_.get()
	SettingsObject.tickNumber = _XTICKS_.get()
	STCore.DataManager.ResultSetting = SettingsObject
	SettingsObject.delLostTracks = _DELTRACKS_.get()
	SettingsObject.delError = _DELERROR_.get()
	SettingsObject.refStar = _REFSTAR_.get()
	SettingsObject.refValue = float(_REFVALUE_.get())
	SettingsObject.timeLenght = (60*int(_TIMELENGHT_.get()))
	if STCore.DataManager.CurrentWindow == 3:
		if STCore.DataManager.RuntimeEnabled == False:
			STCore.Tracker.Destroy()
			STCore.Results.Awake(root, ItemList, TrackedStars)
		else:
			STCore.Results.Reset()
			if CheckWindowClear() == True:
				PlotWindow = tk.Toplevel(root)
				STCore.Results.Awake(PlotWindow, ItemList, TrackedStars)
			else:
				PlotWindow.destroy()
				PlotWindow = tk.Toplevel(root)
				STCore.Results.Awake(PlotWindow, ItemList, TrackedStars)
			PlotWindow.protocol("WM_DELETE_WINDOW", lambda: (STCore.Tracker.OnRuntimeWindowClosed(root), PlotWindow.destroy()))
		return;
	if STCore.DataManager.CurrentWindow == 4:
		STCore.Results.Constant = STCore.Results.GetConstant(ItemList[0].data, 0, 
												  max(SettingsObject.refStar, 0), TrackedStars, SettingsObject.refValue)
		STCore.Results.UpdateConstant(ItemList)
		return;
def Awake(root, ItemList, mini = False, toplevel = True):
	global SettingsObject, _SORTINGMODE_, _DELTRACKS_, _DELERROR_, _REFSTAR_, _REFVALUE_
	if toplevel:
		ConfiguratorFrame = tk.Toplevel(root)
		ConfiguratorFrame.wm_title(string = "Configurar analisis")
		ConfiguratorFrame.resizable(False, False)
		ConfiguratorFrame.protocol("WM_DELETE_WINDOW", lambda: (STCore.Tracker.OnRuntimeWindowClosed(root), ConfiguratorFrame.destroy()))
		ConfiguratorFrame.attributes('-topmost', 'true')
	else:
		ConfiguratorFrame = root
	Load()
	MainPanel = ttk.Frame(ConfiguratorFrame)
	MainPanel.pack(side=tk.LEFT, fill = tk.Y, anchor = tk.N)
	TrackedStars = STCore.Tracker.TrackedStars
	ttk.Label(MainPanel, text = "Ordenar datos por: ").grid(row = 0, column = 0, columnspan = 2, sticky = tk.W)
	ttk.Radiobutton(MainPanel, variable = _SORTINGMODE_, value = 0).grid(row = 1, column = 0, sticky= tk.W)
	ttk.Label(MainPanel, text = "Por fecha").grid(row = 1, column = 1, sticky= tk.W)
	ttk.Radiobutton(MainPanel, variable = _SORTINGMODE_, value = 1).grid(row = 2, column = 0, sticky= tk.W)
	ttk.Label(MainPanel, text = "Por nombre").grid(row = 2, column = 1, sticky= tk.W)
	ttk.Label(MainPanel, text =" ").grid(row = 3, column = 0)

	if not mini:
		ttk.Checkbutton(MainPanel, variable = _DELTRACKS_).grid(row = 4, column = 0, sticky= tk.W)
		ttk.Label(MainPanel, text ="Eliminar datos de rastreo perdidos").grid(row = 4, column = 1, sticky= tk.W)
		ttk.Checkbutton(MainPanel, variable = _DELERROR_).grid(row = 5, column = 0, sticky= tk.W)
		ttk.Label(MainPanel, text ="Eliminar datos distantes").grid(row = 5, column = 1, sticky= tk.W)

	ttk.Label(MainPanel, text ="Numero de etiquetas").grid(row = 6, column = 1, sticky= tk.W)
	ttk.Spinbox(MainPanel, from_ = 1, to = 15, width = 3, textvariable = _XTICKS_).grid(row = 6, column = 0, sticky= tk.W)
	ttk.Label(MainPanel, text ="Minutos de observacion").grid(row = 7, column = 1, sticky= tk.W)
	ttk.Spinbox(MainPanel, from_ = 1, to = 365*24*60, width = 3, textvariable = _TIMELENGHT_).grid(row = 7, column = 0, sticky= tk.W)
	ttk.Label(MainPanel, text ="Estrella de referencia").grid(row = 9, column = 0, columnspan = 2, sticky= tk.W, pady = 20)
	RefFrame = ttk.Frame(MainPanel)
	RefFrame.grid(row = 10, column = 0, columnspan = 3, rowspan = 6, sticky = tk.NSEW)
	_REFSTAR_.trace("w",lambda a,b,c: UpdateReferences(RefFrame, TrackedStars))
	UpdateReferences(RefFrame, TrackedStars)

	Sidebar = ttk.Frame(ConfiguratorFrame)
	Sidebar.pack(side = tk.RIGHT, fill = tk.Y, anchor = tk.N)
	#ttk.Button(Sidebar, text = "Cancelar", command =  lambda: (STCore.Tracker.OnRuntimeWindowClosed(root), ConfiguratorFrame.destroy())).grid(row = 1, column = 0)
	ttk.Button(Sidebar, text = "Aplicar", command = lambda:Apply(root, ItemList, TrackedStars)).grid(row = 0, column = 0)
def UpdateReferences(RefFrame, TrackedStars):
	for child in RefFrame.winfo_children():
		child.destroy()
	i = 0
	for t in TrackedStars:
		frame = ttk.Frame(RefFrame, relief = tk.RAISED)
		frame.grid(row = i, column = 0, columnspan = 2, sticky = tk.W)
		ttk.Radiobutton(frame, variable = _REFSTAR_, value = i).grid(row = 0, column = 0)
		ttk.Label(frame, text = t.star.name).grid(row = 0, column = 1)
		if _REFSTAR_.get() == i:
			tk.Entry(frame, width = 10, textvariable = _REFVALUE_).grid(row = 0, column = 2)
		i += 1