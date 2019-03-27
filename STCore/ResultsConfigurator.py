import Tkinter as tk
import ttk
from STCore.item.ResultSettings import ResultSetting
import STCore.Tracker, STCore.Results, STCore.DataManager
import numpy
#region variables
ConfiguratorFrame = None
SettingsObject = None

_SORTINGMODE_ = None
_DELTRACKS_ = None
_DELERROR_ = None
_REFSTAR_ = None
_REFVALUE_ = None
_XTICKS_ = None
#endregion
def Clear():
	global SettingsObject, _SORTINGMODE_, _DELTRACKS_, _DELERROR_, _REFSTAR_, _REFVALUE_, _XTICKS_
	_SORTINGMODE_ = None
	_DELTRACKS_ = None
	_DELERROR_ = None
	_REFSTAR_ = None
	_REFVALUE_ = None
	_XTICKS_ = None
def Load():
	Clear()
	global SettingsObject, _SORTINGMODE_, _DELTRACKS_, _DELERROR_, _REFSTAR_, _REFVALUE_, _XTICKS_
	if SettingsObject is None:
		SettingsObject = ResultSetting()
	_SORTINGMODE_ = tk.IntVar(value = SettingsObject.sortingMode)
	_DELTRACKS_ = tk.IntVar(value = SettingsObject.delLostTracks)
	_DELERROR_ = tk.IntVar(value = SettingsObject.delError)
	_REFSTAR_ = tk.IntVar(value = SettingsObject.refStar)
	_REFVALUE_ = tk.StringVar(value = SettingsObject.refValue)
	_XTICKS_ = tk.IntVar(value = SettingsObject.tickNumber)

def Apply(root, ItemList, TrackedStars):
	global SettingsObject, _SORTINGMODE_, _DELTRACKS_, _DELERROR_, _REFSTAR_, _REFVALUE_, _XTICKS_
	SettingsObject.sortingMode = _SORTINGMODE_.get()
	SettingsObject.tickNumber = _XTICKS_.get()
	STCore.DataManager.ResultSetting = SettingsObject
	if STCore.DataManager.CurrentWindow == 3:
		if STCore.DataManager.RuntimeEnabled == False:
			STCore.Tracker.Destroy()
		SettingsObject.delLostTracks = _DELTRACKS_.get()
		SettingsObject.delError = _DELERROR_.get()
		SettingsObject.refStar = _REFSTAR_.get()
		SettingsObject.refValue = float(_REFVALUE_.get())
		if STCore.DataManager.RuntimeEnabled == False:
			STCore.Results.Awake(root, ItemList, TrackedStars)
		else:
			PlotWindow = tk.Toplevel(root)
			STCore.Results.Awake(PlotWindow, ItemList, TrackedStars)
	if STCore.DataManager.CurrentWindow == 4:
		ticks = STCore.ResultsConfigurator.SettingsObject.tickNumber
		XAxis, Xlabel = STCore.Results.GetXTicks(ItemList)
		for i in range(len(TrackedStars)):
			X = numpy.c_[XAxis,STCore.Results.MagData[i]]
			STCore.Results.Plots[i].set_offsets(X)
			STCore.Results.PlotAxis.set_xticks(XAxis[0::max(1, len(ItemList) / ticks)])
			STCore.Results.PlotAxis.set_xticklabels(Xlabel[0::max(1, len(ItemList) / ticks)])
			xmin=X[:,0].min(); xmax=X[:,0].max()
			STCore.Results.PlotAxis.set_xlim(xmin-0.1*(xmax-xmin),xmax+0.1*(xmax-xmin))
		STCore.Results.PlotCanvas.draw()

def Awake(root, ItemList, TrackedStars, mini = False):
	global SettingsObject, _SORTINGMODE_, _DELTRACKS_, _DELERROR_, _REFSTAR_, _REFVALUE_
	ConfiguratorFrame = tk.Toplevel(root)
	ConfiguratorFrame.wm_title(string = "Configurar analisis")
	ConfiguratorFrame.resizable(False, False)
	Load()

	MainPanel = tk.LabelFrame(ConfiguratorFrame)
	MainPanel.pack(side = tk.LEFT, fill = tk.Y, anchor = tk.N)

	tk.Label(MainPanel, text = "Ordenar datos por: ").grid(row = 0, column = 0, columnspan = 2, sticky = tk.W)
	ttk.Radiobutton(MainPanel, variable = _SORTINGMODE_, value = 0).grid(row = 1, column = 0, sticky= tk.W)
	tk.Label(MainPanel, text = "Por fecha").grid(row = 1, column = 1, sticky= tk.W)
	ttk.Radiobutton(MainPanel, variable = _SORTINGMODE_, value = 1).grid(row = 2, column = 0, sticky= tk.W)
	tk.Label(MainPanel, text = "Por nombre").grid(row = 2, column = 1, sticky= tk.W)
	tk.Label(MainPanel, text =" ").grid(row = 3, column = 0)

	if not mini:
		ttk.Checkbutton(MainPanel, variable = _DELTRACKS_).grid(row = 4, column = 0, sticky= tk.W)
		tk.Label(MainPanel, text ="Eliminar datos de rastreo perdidos").grid(row = 4, column = 1, sticky= tk.W)
		ttk.Checkbutton(MainPanel, variable = _DELERROR_).grid(row = 5, column = 0, sticky= tk.W)
		tk.Label(MainPanel, text ="Eliminar datos distantes").grid(row = 5, column = 1, sticky= tk.W)

	tk.Label(MainPanel, text ="Numero de etiquetas").grid(row = 6, column = 1, sticky= tk.W)
	tk.Spinbox(MainPanel, from_ = 1, to = len(ItemList), width = 3, textvariable = _XTICKS_).grid(row = 6, column = 0, sticky= tk.W)
	if not mini:
		tk.Label(MainPanel, text ="Estrella de referencia").grid(row = 7, column = 0, columnspan = 2, sticky= tk.W, pady = 20)
		RefFrame = tk.LabelFrame(MainPanel)
		RefFrame.grid(row = 8, column = 0, columnspan = 3, rowspan = 6, sticky = tk.NSEW)
		_REFSTAR_.trace("w",lambda a,b,c: UpdateReferences(RefFrame, TrackedStars))
		UpdateReferences(RefFrame, TrackedStars)

	Sidebar = tk.Frame(ConfiguratorFrame)
	Sidebar.pack(side = tk.RIGHT, fill = tk.Y, anchor = tk.N)
	ttk.Button(Sidebar, text = "Cancelar", command = ConfiguratorFrame.destroy).grid(row = 1, column = 0)
	ttk.Button(Sidebar, text = "Analizar", command = lambda:(ConfiguratorFrame.destroy(), Apply(root, ItemList, TrackedStars))).grid(row = 0, column = 0)
def UpdateReferences(RefFrame, TrackedStars):
	for child in RefFrame.winfo_children():
		child.destroy()
	i = 0
	for t in TrackedStars:
		frame = tk.Frame(RefFrame, relief = tk.RAISED)
		frame.grid(row = i, column = 0, columnspan = 2, sticky = tk.W)
		tk.Radiobutton(frame, variable = _REFSTAR_, value = i).grid(row = 0, column = 0)
		tk.Label(frame, text = t.star.name).grid(row = 0, column = 1)
		if _REFSTAR_.get() == i:
			tk.Entry(frame, width = 10, textvariable = _REFVALUE_).grid(row = 0, column = 2)
		i += 1