# coding=utf-8
import tkinter as tk
from tkinter import ttk
import configparser
from os.path import isfile
from os import remove
#region Variables
SettingsFrame = None
Window = None
VisModes = ("Linear", "Raiz cuadrada", "Logaritmico")
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

def Awake(root):
	global Window,SettingsFrame
	global _RECENT_FILES_, _PROCESS_NUMBER_, _SHOW_GRID_, _VISUAL_MODE_, _VISUAL_COLOR_, _TRACK_PREDICTION_, _SHOW_TRACKEDPOS_
	if Window is not None:
		return
	Window = tk.Toplevel(root)
	Window.wm_title(string = "Configuración")
	Window.protocol("WM_DELETE_WINDOW", CloseWindow)
	Window.attributes('-topmost', 'true')
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
	ttk.Button(BottomPanel, text = "Cancelar", command = CloseWindow).grid(row = 1, column = 0)
	ttk.Button(BottomPanel, text = "Aceptar", command = SaveSettings).grid(row = 0, column = 0)

def CloseWindow():
	global Window
	Window.destroy()
	Window = None
