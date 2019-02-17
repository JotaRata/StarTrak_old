# coding=utf-8
import Tkinter as tk
import ttk
import ConfigParser
from os.path import isfile
from os import remove
import STCore.DataManager
#region Variables
SettingsFrame = None
Window = None
VisModes = ("Linear", "Raiz cuadrada", "Logartitmico")
VisColors = ("Escala de grises", "Temperatura", "Arcoiris", "Negativo")
ThrNumber = ("1", "2", "3", "4")
WorkingPath = ""
#ednregion
#region Settings variables
_RECENT_FILES_ = None
_PROCESS_NUMBER_ = None
_SHOW_GRID_ = None
_VISUAL_MODE_ = None
_VISUAL_COLOR_ = None
_TRACK_PREDICTION_ = None
_SHOW_TRACKEDPOS_ = None
#endregion

def LoadSettings():
	global _RECENT_FILES_, _PROCESS_NUMBER_, _SHOW_GRID_, _VISUAL_MODE_, _VISUAL_COLOR_, _TRACK_PREDICTION_, _SHOW_TRACKEDPOS_
	config = ConfigParser.ConfigParser()
	if (isfile(WorkingPath+"/settings.ini")):
		config.read(WorkingPath+"/settings.ini")
	else:
		print "Setting file not found, creating new file.."
		SaveSettingsDefault()
		LoadSettings()
		return
	_RECENT_FILES_ = tk.IntVar(value = int(config.get("GENERAL","_SHOW_RECENT_FILES_", 1)))
	_PROCESS_NUMBER_ = tk.StringVar(value = ThrNumber[int(config.get("GENERAL","_THREADS_NUMBER_", 3))])
	_SHOW_GRID_ =   tk.IntVar(value = int(config.get("VISUALIZATION","_SHOW_GRID_", 0)))
	_VISUAL_MODE_ = tk.StringVar(value = VisModes[int(config.get("VISUALIZATION","_SCALE_MODE_", 0))])
	_VISUAL_COLOR_ = tk.StringVar(value = VisColors[int(config.get("VISUALIZATION","_COLOR_MODE_", 0))])
	_TRACK_PREDICTION_ = tk.IntVar(value = int(config.get("TRACKING","_USE_PREDICTION_", 1)))
	_SHOW_TRACKEDPOS_ = tk.IntVar(value = int(config.get("TRACKING","_SHOW_TRACKS_", 1)))

def SaveSettingsDefault():
	config = ConfigParser.ConfigParser()
	config.add_section("GENERAL")
	config.set("GENERAL", "_SHOW_RECENT_FILES_", 1)
	config.set("GENERAL", "_THREADS_NUMBER_", 3)

	config.add_section("VISUALIZATION")
	config.set("VISUALIZATION", "_SHOW_GRID_", 0)
	config.set("VISUALIZATION", "_SCALE_MODE_", 0)
	config.set("VISUALIZATION", "_COLOR_MODE_", 0)

	config.add_section("TRACKING")
	config.set("TRACKING", "_USE_PREDICTION_", 1)
	config.set("TRACKING", "_SHOW_TRACKS_", 1)
	with open(WorkingPath+'/Settings.ini', 'w') as configfile:
		 config.write(configfile)

def SaveSettings():
	config = ConfigParser.ConfigParser()
	config.add_section("GENERAL")
	config.add_section("VISUALIZATION")
	config.add_section("TRACKING")
	config.set("TRACKING", "_USE_PREDICTION_", _TRACK_PREDICTION_.get())
	config.set("TRACKING", "_SHOW_TRACKS_", _SHOW_TRACKEDPOS_.get())

	config.set("VISUALIZATION", "_SHOW_GRID_", _SHOW_GRID_.get())
	config.set("VISUALIZATION", "_SCALE_MODE_",VisModes.index(str(_VISUAL_MODE_.get())))
	config.set("VISUALIZATION", "_COLOR_MODE_",VisColors.index(str(_VISUAL_COLOR_.get())))

	config.set("GENERAL", "_SHOW_RECENT_FILES_", _RECENT_FILES_.get())
	config.set("GENERAL", "_THREADS_NUMBER_",ThrNumber.index(_PROCESS_NUMBER_.get()))
	with open(WorkingPath+'/Settings.ini', 'w') as configfile:
		 config.write(configfile)
	if STCore.DataManager.CurrentWindow == 2:
		STCore.ImageView.UpdateImage()
	if STCore.DataManager.CurrentWindow == 3:
		STCore.Tracker.UpdateImage()
	Window.destroy()

def Awake(root):
	global Window,SettingsFrame
	global _RECENT_FILES_, _PROCESS_NUMBER_, _SHOW_GRID_, _VISUAL_MODE_, _VISUAL_COLOR_, _TRACK_PREDICTION_, _SHOW_TRACKEDPOS_
	Window = tk.Toplevel(root)
	Window.wm_title(string = "Configuración")
	Window.resizable(False, False)
	SettingsFrame = tk.Frame(Window)
	SettingsFrame.pack(fill = tk.BOTH, expand = 1, side = tk.LEFT)
	
	genSettings = tk.LabelFrame(SettingsFrame, text = "Configuración general:")
	genSettings.pack(fill = tk.X, expand = 1)
	tk.Checkbutton(genSettings, variable = _RECENT_FILES_).grid(row = 1, column = 1, columnspan = 1, sticky = tk.E)
	tk.Label(genSettings, text = "Mostrar archivos recientes").grid(row = 1, column = 0, columnspan = 1, sticky = tk.W)
	#ttk.OptionMenu(genSettings, _PROCESS_NUMBER_,_PROCESS_NUMBER_.get(), *ThrNumber).grid(row = 2, column = 1, columnspan = 1, sticky = tk.E)
	#tk.Label(genSettings, text = "Número máximo de sub-procesos").grid(row = 2, column = 0, columnspan = 1, sticky = tk.W)

	visSettings = tk.LabelFrame(SettingsFrame, text = "Configuración de Visualización:")
	visSettings.pack(fill = tk.X, expand = 1)
	tk.Checkbutton(visSettings, variable = _SHOW_GRID_).grid(row = 2, column = 1, columnspan = 1, sticky = tk.E)
	tk.Label(visSettings, text = "Mostrar cuadrícula").grid(row = 2, column = 0, columnspan = 1, sticky = tk.W)
	ttk.OptionMenu(visSettings, _VISUAL_MODE_,_VISUAL_MODE_.get(), *VisModes).grid(row = 3, column = 1, columnspan = 1, sticky = tk.E)
	ttk.OptionMenu(visSettings, _VISUAL_COLOR_,_VISUAL_COLOR_.get(), *VisColors).grid(row = 4, column = 1, columnspan = 1, sticky = tk.E)
	tk.Label(visSettings, text = "Modo de visualización").grid(row = 3, column =0, columnspan = 1, sticky = tk.W)
	tk.Label(visSettings, text = "Mapa de color").grid(row =4, column =0, columnspan = 1, sticky = tk.W)

	trackSettings = tk.LabelFrame(SettingsFrame, text = "Configuración de Rastreo:")
	trackSettings.pack(fill = tk.X, expand = 1)
	tk.Checkbutton(trackSettings, variable = _TRACK_PREDICTION_).grid(row = 0, column = 1, columnspan = 1, sticky = tk.E)
	tk.Label(trackSettings, text = "Utilizar predicción de movimiento").grid(row = 0, column = 0, columnspan = 1, sticky = tk.W)
	tk.Checkbutton(trackSettings, variable = _SHOW_TRACKEDPOS_).grid(row = 1, column = 1, columnspan = 1, sticky = tk.E)
	tk.Label(trackSettings, text = "Mostrar trayectoria de rastreo").grid(row = 1, column = 0, columnspan = 1, sticky = tk.W)

	BottomPanel = tk.Frame(Window)
	BottomPanel.pack(side = tk.RIGHT, fill = tk.Y)
	ttk.Button(BottomPanel, text = "Cancelar", command = Window.destroy).grid(row = 1, column = 0)
	ttk.Button(BottomPanel, text = "Aceptar", command = SaveSettings).grid(row = 0, column = 0)