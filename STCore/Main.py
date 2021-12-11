# coding=utf-8

_name_ = "STCore"
import sys
import gc
from tkinter.constants import END
import warnings
from os.path import abspath, basename, dirname, isfile

warnings.filterwarnings("ignore")	

try:
	import Debug
except:
	raise ImportError("No se pudo importar algunos modulos")
if sys.version_info < (3, 0):
	Debug.Error(_name_, "StarTrak debe ser ejecutado usando  Python3")

try:
	Debug.Log(_name_, "Iniciando Tk..")
	import tkinter as tk
	from tkinter import Toplevel, filedialog, font, messagebox, ttk
	from tkinter.filedialog import FileDialog
except:
	Debug.Error(_name_, "No se pudo cargar los modulos tkinter\nAsegurese que estos modulos esten activados en su instalacion de python.")

try:
	Debug.Log(_name_, "Iniciando MPL..")
	import matplotlib.pyplot as plt
except:
	Debug.Error(_name_, "Matplotlib no se pudo cargar o no esta instalado\nAsegurate de instalar la ultima version de MatplotLib usando:\npip3 install matplotlib")
try:
	Debug.Log(_name_, "Iniciando AstroPy..")
	import astropy.io
except:
	Debug.Error(_name_, "AstroPy no se pudo cargar o no esta instalado\nAsegurate de instalar la ultima version de AstroPy usando:\npip3 install astropy")

try:
	Debug.Log (_name_, "Iniciando PIL..")
	from PIL import Image, ImageTk
except:
	Debug.Error(_name_, "No se pudo cargar Python Image Library\nAsegurate de instalarlo usando:\npip3 install pillow")
try:
	sys.path.append(dirname(dirname(abspath(__file__))))
except NameError:  # We are the main py2exe script, not a module
	sys.path.append(dirname(dirname(abspath(sys.argv[0]))))
try:
	Debug.Log (_name_, "Cargando modulos de Startrak..")
	# from STCore import Composite
	# from STCore import DataManager
	# from STCore import ImageSelector
	# from STCore import ImageView
	# from STCore import Results
	# from STCore import ResultsConfigurator
	#from STCore import RuntimeAnalysis
	# from STCore import Settings
	#from STCore import Tools
	# from STCore import Tracker
	# from STCore import Styles
	from STCore import Icons
	from STCore.bin import env
	from STCore.bin.app.ui import MainScreenUI, STView, SelectorUI
	from STCore.bin.data_management import RecentsManager, SettingsManager, SessionManager
	from STCore.bin.app.ui import SessionDialog
	from STCore import styles


except:
	Debug.Error(_name_, "Algunos archivos de StarTrak no existen o no pudieron ser cargados\nAsegurate de descargar la ultima version e intenta de nuevo\n")
print ("=" * 60)

# Define scope
# ----------------------------------
master : tk.Tk = None

# Define functions
#---------------------------------
def change_view(view_name : str):
	view = env.views[view_name]
	
	# if view.active:
	# 	return view
	if env.current_view is not None:
		env.current_view.close()
		#env.current_view.active = False

	view.build(master)
	#view.active = True
	env.current_view = view
	return view

def load_files():
	paths = filedialog.askopenfilenames(parent = master, filetypes=[("FIT Image", "*.fits;*.fit"), ("Todos los archivos",  "*.*")])
	view = change_view("selector")
	view.config_callback()

def create_session():
	level = SessionDialog(master)
	return level
def load_session(path):
	if not isfile(path):
		messagebox.showerror("Error", "Este archivo no existe")
		Debug.Error(_name_, "El archivo {0} no existe".format(path))
		# DataManager.RecentFiles.remove(path)
		# DataManager.SaveRecent()
		return

	session = SessionManager()
	session.load_data(path)

	# Tracker.DataChanged = False
	if  session.runtime:
		RuntimeAnalysis.directoryPath = session.runtime_dir
		RuntimeAnalysis.filesList = session.file_refs
		RuntimeAnalysis.startFile = ""
		RuntimeAnalysis.dirState = session.runtime_dir_state
		print ("---------------------------")
		print ("DirState: ", len(session.RuntimeDirState))
	else:
		RuntimeAnalysis.directoryPath = ""
		RuntimeAnalysis.dirState = []
		RuntimeAnalysis.filesList = []
		RuntimeAnalysis.startFile = ""

	if session.window == 1:
		change_view("selector")
		# Destroy()
		# ImageSelector.Awake(win)
	if (session.window == 2) and session.runtime == True:
		change_view("viewer")
		# Destroy()
		# ImageView.Awake(win)
	if session.window == 2:
		change_view("selector")
		# Destroy()
		# ImageSelector.Awake(win)
		# ImageSelector.Apply(win)
	if (session.window == 4 or session.window == 3) and session.runtime == True:
		# Destroy()
		# Tracker.CurrentFile = 0
		# Tracker.Awake(win, ImageView.Stars, DataManager.FileItemList)
		change_view("tracker")
		RuntimeAnalysis.StartRuntime(master)
	if session.window == 3 or session.window == 5:
		change_view("tracker")
		# Destroy()
		# ImageSelector.Awake(win)
		# ImageSelector.Destroy()
		# Tracker.Awake(win, ImageView.Stars, ImageSelector.FilteredList)
	if session.window == 4:
		change_view("graph")
		# Destroy()
		# ImageSelector.Awake(win)
		# ImageSelector.Destroy()
		# Results.Awake(win, ImageSelector.FilteredList, Tracker.TrackedStars)

	env.session_manager = session
	return session

def reset():
	if env.session_manager is None: return
	env.session_manager = None
	change_view("main")
	

def preload_view(root):
	Debug.Log (_name_, "Preloading Views..")
	env.views = { "main" : MainScreenUI(root), 
				"selector" : SelectorUI(root)}

def TkinterExceptionHandler(*args):
	Debug.Error("Tk", "Se ha detectado un error de ejecuccion, revisa el registro para mas detalles.", stop=False)

# -----------------------------------
try:
	if __name__ == "__main__":
		# Iniciar atributos de entorno
		env.scope = __name__
		env.working_path = dirname(abspath(__file__))

		master = tk.Tk()
		master.configure(bg="black")
		master.tk.call('lappend', 'auto_path', 'STCore/theme/awthemes-10.3.0')
		master.tk.call('package', 'require', 'awdark')
		master.report_callback_exception = TkinterExceptionHandler
		
		styles.load_styles()
		preload_view(master)
		env.recent_manager = RecentsManager()
		env.settings_manager = SettingsManager()
		env.tk = master

		Icons.load_icons()
		env.settings_manager.load_settings()
		env.recent_manager.load_recent()

		env.views["main"].config_callback(toplevel = create_session, load_data = load_session)
		main_view = change_view("main")

		# Settings.WorkingPath = dirname(abspath(__file__))
		# DataManager.WorkingPath = dirname(abspath(__file__))
		#Tools.Awake(master)
		
		#print DataManager.WorkingPath

		master.wm_title(string = "StarTrak 1.2.0")
		master.geometry("1280x640")
		try:
			master.iconbitmap(env.working_path+"/icon.ico")
		except:
			pass
		
		#master.after(20, Awake, master)
		
		# Pre-initialize UI Drawabless
		
		if len(sys.argv) > 1:
			load_session(str(sys.argv[1]), master)
		
		#print(style.theme_names())
		
		
		master.mainloop()
except:
	Debug.Error(_name_, "Ha ocurrido un error que ha hecho que Startrak deje de funcionar, revisa el registro para mas detalles")
def GetWindow():
	return master 
