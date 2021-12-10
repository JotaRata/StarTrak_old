import __main__ as Main
from configparser import ConfigParser
from dataclasses import dataclass
import pickle
from os.path import isfile
from tkinter import BooleanVar, IntVar, StringVar
from STCore import Debug
from STCore.bin import env
from STCore.classes.items import Setting

class SessionManager:
	current_path : str 		= ""
	session_name : str		= ""
	file_refs 	 : list 	= []
	file_items 	 : list 	= []
	star_items 	 : list 	= []
	track_items  : list 	= []
	graph_setting = None
	graph_cache =  None
	viewer_levels:  tuple	= None
	graph_constant: float	= 0
	runtime		  : float 	= False
	runtime_dir : str = ""
	runtime_dir_state = []
	window = 0

	def __print__(self):
		print (self.file_items)
		print (self.star_items)
		print (self.track_items)
		print (self.current_window)
	
	def save_data(self, filepath):
		self.current_path = filepath

		with open(filepath, "wb") as out:
			pickle.dump(self.session_name, out, pickle.DEFAULT_PROTOCOL)
			pickle.dump(self.file_refs, out, pickle.HIGHEST_PROTOCOL)
			pickle.dump(self.star_items, out, pickle.HIGHEST_PROTOCOL)
			pickle.dump(self.track_items, out, pickle.HIGHEST_PROTOCOL)
			pickle.dump(self.window, out, pickle.HIGHEST_PROTOCOL)
			pickle.dump(self.graph_setting, out, pickle.HIGHEST_PROTOCOL)
			pickle.dump(self.viewer_levels, out, pickle.HIGHEST_PROTOCOL)
			pickle.dump(self.graph_cache, out, pickle.HIGHEST_PROTOCOL)
			pickle.dump(self.graph_constant, out, pickle.HIGHEST_PROTOCOL)
			pickle.dump(self.runtime, out, pickle.HIGHEST_PROTOCOL)
			pickle.dump(self.runtime_dir, out, pickle.HIGHEST_PROTOCOL)
			pickle.dump(self.runtime_dir_state, out, pickle.HIGHEST_PROTOCOL)
		Main.WindowName()

	def load_data(self, filepath):
		self.reset()
		self.current_path = filepath
		with open(filepath, "rb") as inp:
			try:
				self.session_name = pickle.load(inp)
				self.file_refs = pickle.load(inp)
				self.star_items = pickle.load(inp)
				self.track_items = pickle.load(inp)
				self.window = pickle.load(inp)
				self.graph_setting = pickle.load(inp)
				self.viewer_levels = pickle.load(inp)
				self.graph_cache = pickle.load(inp)
				self.graph_constant = pickle.load(inp)
				self.runtime = pickle.load(inp)
				self.runtime_dir = pickle.load(inp)
				self.runtime_dir_state = pickle.load(inp)
			except:
				print ("El archivo seleccionado parece ser de una version incompatible..")
				pass
		if filepath not in self.recent_files:
			self.recent_files.append((self.session_name, str(filepath)))
		self.save_recent()

		Main.WindowName()
		Main.LoadData(self.window)
#----------------------------------
class RecentsManager:
	recent_files = []

	def reset(self):
		Main.Reset()

	def save_recent(self):
		with open(env.working_path+"/StarTrak.bin", "wb") as f:
			pickle.dump(self.recent_files, f, pickle.HIGHEST_PROTOCOL)

	def load_recent(self):
		if (isfile(env.working_path + "/StarTrak.bin")):
			with open(env.working_path + "/StarTrak.bin", "rb") as f:
				try:
					self.recent_files = pickle.load(f)
				except:
					pass
		else:
			self.save_recent()
#----------------------------------
class SettingsManager:
	def __init__(self):
		self.loaded = False
		self.keys = [
			Setting(BooleanVar(),	"GENERAL",	 	"SHOW_RECENT", 	True),
			Setting(IntVar(), 		"GENERAL", 		"THREADNUM", 	1),
			Setting(BooleanVar(),	"VISUAL", 		"SHOW_GRID", 	False),
			Setting(IntVar(), 		"VISUAL", 		"SCALE_MODE", 	0),
			Setting(IntVar(), 		"VISUAL", 		"COLOR_MODE", 	0),
			Setting(BooleanVar(), 	"TRACKING", 	"TRACK_PRED", 	True),
			Setting(BooleanVar(),	"TRACKING", 	"SHOW_TRAILS", 	True),
		]
	
	def load_settings(self):
		config = ConfigParser()
		if (isfile(env.working_path + "/settings.ini")):
			config.read(env.working_path + "/settings.ini")
		else:
			Debug.Warn(__name__, "Settings file not found, creating new file..")
			self.save_default()
			self.load_settings()
			return

		for key in self.keys:
			try:
				key.set(config.get(key.group, key.name))
			except:
				Debug.Warn(__name__, "La clave {0} no se ha encontrado en la configuracion".format(key.name))
				continue
		self.loaded = True

	def save(self):
		config = ConfigParser()

		config.add_section("GENERAL")
		config.add_section("VISUAL")
		config.add_section("TRACKING")

		for key in self.keys:
			config.set(key.group, key.name, key.get())

		with open(env.working_path + '/settings.ini', 'w') as configfile:
			config.write(configfile)
			
	def save_default(self):
		config = ConfigParser()

		config.add_section("GENERAL")
		config.add_section("VISUAL")
		config.add_section("TRACKING")

		for key in self.keys:
			config.set(key.group, key.name, key.default)

		with open(env.working_path + '/settings.ini', 'w') as configfile:
			config.write(configfile)


		#CloseWindow()