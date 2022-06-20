import tkinter as tk
from tkinter import ttk

import DataManager
import Results
import Tracker
from item.ResultSettings import ResultSetting

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
_PLOTKIND_ = None
#endregion
def Clear():
	global SettingsObject, _SORTINGMODE_, _DELTRACKS_, _DELERROR_, _REFSTAR_, _REFVALUE_, _XTICKS_, _TIMELENGHT_, _PLOTKIND_
	_SORTINGMODE_ = None
	_DELTRACKS_ = None
	_DELERROR_ = None
	_REFSTAR_ = None
	_REFVALUE_ = None
	_XTICKS_ = None
	_TIMELENGHT_ = None
	_PLOTKIND_ = None
def Load():
	Clear()
	global SettingsObject, _SORTINGMODE_, _DELTRACKS_, _DELERROR_, _REFSTAR_, _REFVALUE_, _XTICKS_, _TIMELENGHT_, _PLOTKIND_
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
		_PLOTKIND_ = tk.IntVar(value = SettingsObject.plotkind)
	except:
		print ("Invalid or Outdated Result Setting Object, creating a new one from scratch..")
		SettingsObject = None
		Load()
		pass
def CheckWindowClear():
	value = PlotWindow == None or not tk.Toplevel.winfo_exists(PlotWindow)
	print ("Result Window Cleared: ", value)
	return value

def Apply(root, ItemList, TrackedStars):
	global SettingsObject, _SORTINGMODE_, _DELTRACKS_, _DELERROR_, _REFSTAR_, _REFVALUE_, _XTICKS_, PlotWindow, _TIMELENGHT_, _PLOTKIND_
	SettingsObject.sortingMode = _SORTINGMODE_.get()
	SettingsObject.tickNumber = _XTICKS_.get()
	DataManager.ResultSetting = SettingsObject
	SettingsObject.delLostTracks = _DELTRACKS_.get()
	SettingsObject.delError = _DELERROR_.get()
	SettingsObject.refStar = _REFSTAR_.get()
	SettingsObject.refValue = float(_REFVALUE_.get())
	SettingsObject.timeLenght = (60*int(_TIMELENGHT_.get()))
	SettingsObject.plotkind = _PLOTKIND_.get()

	if DataManager.CurrentWindow == 3:
		if DataManager.RuntimeEnabled == False:
			Tracker.Destroy()
			Results.Awake(root, ItemList, TrackedStars)
		else:
			Results.Reset()
			if CheckWindowClear() == True:
				PlotWindow = tk.Toplevel(root)
				Results.Awake(PlotWindow, ItemList, TrackedStars)
			else:
				PlotWindow.destroy()
				PlotWindow = tk.Toplevel(root)
				Results.Awake(PlotWindow, ItemList, TrackedStars)
			PlotWindow.protocol("WM_DELETE_WINDOW", lambda: (Tracker.OnRuntimeWindowClosed(root), PlotWindow.destroy()))
		return;
	if DataManager.CurrentWindow == 4:
		#Results.Constant = Results.GetConstant(ItemList[0].data, 0, 
		#										  max(SettingsObject.refStar, 0), TrackedStars, SettingsObject.refValue)
		Results.UpdateGraph(ItemList)
		return;
def Awake(root, ItemList, mini = False, toplevel = True):
	global SettingsObject, _SORTINGMODE_, _DELTRACKS_, _DELERROR_, _REFSTAR_, _REFVALUE_
	if toplevel:
		ConfiguratorFrame = tk.Toplevel(root)
		ConfiguratorFrame.wm_title(string = "Configurar analisis")
		ConfiguratorFrame.resizable(False, False)
		ConfiguratorFrame.protocol("WM_DELETE_WINDOW", lambda: (Tracker.OnRuntimeWindowClosed(root), ConfiguratorFrame.destroy()))
		ConfiguratorFrame.attributes('-topmost', 'true')
	else:
		ConfiguratorFrame = root
	Load()
	MainPanel = ttk.Frame(ConfiguratorFrame)
	MainPanel.pack(side=tk.LEFT, fill = tk.Y, anchor = tk.N)
	TrackedStars = Tracker.TrackedStars

	ttk.Label(MainPanel, text="Tipo de grafico:").grid(row=2, column=0, sticky=tk.W)	
	horizontalPanel = ttk.Frame(MainPanel)
	horizontalPanel.grid(row=2, column=1, sticky=tk.EW)	

	magPlot = tk.Button(horizontalPanel, command=  lambda: ChangePlotKind(0), text="Magnitud", fg="gray80", relief=tk.FLAT)
	snrPlot = tk.Button(horizontalPanel, command=  lambda: ChangePlotKind(1), text="Señal-ruido", fg="gray80", relief=tk.FLAT)

	def ChangePlotKind(kind):
		colorOn = "aquamarine4"
		colorOff = "gray20"

		if kind == 0:
			magPlot.config(bg=colorOn)
			snrPlot.config(bg=colorOff)
		else:
			magPlot.config(bg=colorOff)
			snrPlot.config(bg=colorOn)
		_PLOTKIND_.set(kind)
	
	ChangePlotKind(0)
	magPlot.pack(side=tk.LEFT, fill=tk.X, expand=1)
	snrPlot.pack(side=tk.RIGHT, fill=tk.X, expand=1)



	#ttk.Label(MainPanel, text = "Ordenar datos por: ").grid(row = 0, column = 0, columnspan = 2, sticky = tk.W)
	#ttk.Radiobutton(MainPanel, variable = _SORTINGMODE_, value = 0).grid(row = 1, column = 0, sticky= tk.W)
	#ttk.Label(MainPanel, text = "Por fecha").grid(row = 1, column = 1, sticky= tk.W)
	#ttk.Radiobutton(MainPanel, variable = _SORTINGMODE_, value = 1).grid(row = 2, column = 0, sticky= tk.W)
	#ttk.Label(MainPanel, text = "Por nombre").grid(row = 2, column = 1, sticky= tk.W)
	#ttk.Label(MainPanel, text =" ").grid(row = 3, column = 0)

	if not mini:
		ttk.Checkbutton(MainPanel, variable = _DELTRACKS_).grid(row = 4, column = 1, sticky= tk.E)
		ttk.Label(MainPanel, text ="Eliminar datos perdidos").grid(row = 4, column = 0, sticky= tk.W)

		ttk.Checkbutton(MainPanel, variable = _DELERROR_).grid(row = 5, column = 1, sticky= tk.E)
		ttk.Label(MainPanel, text ="Eliminar datos distantes").grid(row = 5, column = 0, sticky= tk.W)

	ttk.Label(MainPanel, text ="Numero de etiquetas").grid(row = 6, column = 0, sticky= tk.W)
	ttk.Spinbox(MainPanel, from_ = 1, to = 15, width = 3, textvariable = _XTICKS_).grid(row = 6, column = 1, sticky= tk.E)

	ttk.Label(MainPanel, text ="Minutos de observacion").grid(row = 7, column = 0, sticky= tk.W)
	ttk.Spinbox(MainPanel, from_ = 1, to = 365*24*60, width = 3, textvariable = _TIMELENGHT_).grid(row = 7, column = 1, sticky= tk.E)

	ttk.Label(MainPanel, text ="Estrella de referencia").grid(row = 9, column = 0, columnspan = 2, sticky= tk.W, pady = 20)
	RefFrame = ttk.Frame(MainPanel)
	RefFrame.grid(row = 10, column = 0, columnspan = 3, rowspan = 6, sticky = tk.NSEW)
	_REFSTAR_.trace("w",lambda a,b,c: UpdateReferences(RefFrame, TrackedStars))
	UpdateReferences(RefFrame, TrackedStars)

	ttk.Button(MainPanel, text = "Aplicar", command = lambda:Apply(root, ItemList, TrackedStars)).grid(row = 0, column = 0, columnspan=2)
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
			tk.Entry(frame, width = 10, textvariable = _REFVALUE_).grid(row = 0, column = 2,sticky=tk.E)
		i += 1
