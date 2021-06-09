import tkinter as tk
from tkinter import ttk
import STCore.DataManager
import STCore.Settings
from tkinter import filedialog
from tkinter import messagebox
import webbrowser
#region Variables
ToolbarFrame = None
#endregion

def Awake(root):
	menubar = tk.Menu(root)

	filemenu = tk.Menu(menubar, tearoff=0)
	filemenu.add_command(label="Nuevo", command=NewFileCommand)
	filemenu.add_command(label="Abrir", command=OpenFileCommand)
	filemenu.add_command(label="Guardar", command=SaveFileCommand)
	filemenu.add_separator()
	filemenu.add_command(label="Opciones", command=lambda: OpenSettingsCommand(root))
	filemenu.add_command(label="Salir", command=lambda:QuitAppCommand(root))
	menubar.add_cascade(label="Archivo", menu=filemenu)


	#editmenu = tk.Menu(menubar, tearoff=0)
	#editmenu.add_command(label="Pagina anterior", command=hello)
	#editmenu.add_command(label="Pagina siguiente", command=hello)
	#editmenu.add_command(label="", command=hello)
	#menubar.add_cascade(label="Ver", menu=editmenu)

	#toolmenu = tk.Menu(menubar, tearoff=0)
	#toolmenu.add_command(label="Configurar magnitud base", command=hello)
	#toolmenu.add_command(label="Opciones de rastreo", command=hello)
	#menubar.add_cascade(label="Herramientas", menu=toolmenu)

	helpmenu = tk.Menu(menubar, tearoff=0)
	helpmenu.add_command(label="Guia de usuario", command=Help)
	helpmenu.add_command(label="Acerca de", command=About)
	menubar.add_cascade(label="Ayuda", menu=helpmenu)

	root.config(menu=menubar)

def NewFileCommand():
	if messagebox.askyesno("Confirmar Nuevo Archivo", "Desea descartar los cambios actuales?"):
		STCore.DataManager.CurrentFilePath = ""
		STCore.DataManager.Reset()
def OpenFileCommand():
	path = filedialog.askopenfilename(filetypes=[("StarTrak Save", "*.trak")])
	if len(path) == 0:
		return
	if path not in STCore.DataManager.RecentFiles:
		STCore.DataManager.RecentFiles.append(str(path))
	STCore.DataManager.SaveRecent()
	STCore.DataManager.LoadData(str(path))

def SaveFileCommand():
	path = filedialog.asksaveasfilename(confirmoverwrite = True, filetypes=[("StarTrak Save", "*.trak")], defaultextension = "*.trak")
	if len(path) == 0:
		return
	STCore.DataManager.SaveData(str(path))
	
def QuitAppCommand(root):
	if messagebox.askyesno("Confirmar Salida", "Desea descartar los cambios actuales?"):
		root.destroy()

def OpenSettingsCommand(root):
	STCore.Settings.Awake(root)
def hello():
	print ("Coming soon..")
def Help():
	webbrowser.open("file://"+STCore.DataManager.WorkingPath+"/help/help.html")
def About():
	top = tk.Toplevel()
	top.wm_title(string = "Acerca de")
	top.geometry("320x320")
	tk.Label(top, text = "StarTrak version 1.0.0").pack()
	tk.Label(top, text = "Creado por Kevin Espindola y Jose Barria").pack()
	tk.Label(top, text = "Estudiantes de Lic. en fisica M/ Astornomia").pack()
	tk.Label(top, text = "Universidad de Valparaiso - 2019").pack()