import Tkinter as tk
import ttk
import STCore.DataManager
import STCore.Settings
import tkFileDialog
import tkMessageBox
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
	filemenu.add_command(label="Salir", command=lambda:QuitAppCommand(root))
	menubar.add_cascade(label="Archivo", menu=filemenu)

	editmenu = tk.Menu(menubar, tearoff=0)
	editmenu.add_command(label="Pagina anterior", command=hello)
	editmenu.add_command(label="Pagina siguiente", command=hello)
	#editmenu.add_command(label="", command=hello)
	menubar.add_cascade(label="Ver", menu=editmenu)

	toolmenu = tk.Menu(menubar, tearoff=0)
	#toolmenu.add_command(label="Configurar magnitud base", command=hello)
	#toolmenu.add_command(label="Opciones de rastreo", command=hello)
	toolmenu.add_command(label="Opciones", command=lambda: OpenSettingsCommand(root))
	menubar.add_cascade(label="Herramientas", menu=toolmenu)

	helpmenu = tk.Menu(menubar, tearoff=0)
	helpmenu.add_command(label="Guia de usuario", command=hello)
	helpmenu.add_command(label="Acerca de", command=hello)
	menubar.add_cascade(label="Ayuda", menu=helpmenu)

	root.config(menu=menubar)

def NewFileCommand():
	if tkMessageBox.askyesno("Confirmar Nuevo Archivo", "Desea descartar los cambios actuales?"):
		STCore.DataManager.CurrentFilePath = ""
		STCore.DataManager.Reset()
def OpenFileCommand():
	path = tkFileDialog.askopenfilename(filetypes=[("StarTrak Save", "*.trak")])
	if len(path) == 0:
		return
	STCore.DataManager.LoadData(str(path))

def SaveFileCommand():
	path = tkFileDialog.asksaveasfilename(confirmoverwrite = True, filetypes=[("StarTrak Save", "*.trak")], defaultextension = "*.trak")
	if len(path) == 0:
		return
	STCore.DataManager.SaveData(str(path))
	
def QuitAppCommand(root):
	if tkMessageBox.askyesno("Confirmar Salida", "Desea descartar los cambios actuales?"):
		root.quit()

def OpenSettingsCommand(root):
	STCore.Settings.Awake(root)
def hello():
	print "Coming soon.."