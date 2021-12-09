import __main__ as Main
import pickle
from os.path import isfile

class SessionManager:
	working_path : str 		= ""
	current_path : str 		= ""
	session_name : str		= ""
	file_refs 	 : list 	= []
	file_items 	 : list 	= []
	star_items 	 : list 	= []
	track_items  : list 	= []
	current_win	 : int		= 0
	graph_setting = None
	graph_cache =  None
	viewer_levels:  tuple	= None
	graph_constant: float	= 0
	runtime		  : float 	= False
	runtime_dir : str = ""
	runtime_dir_state = []

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
			pickle.dump(self.current_win, out, pickle.HIGHEST_PROTOCOL)
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
				self.current_win = pickle.load(inp)
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
		Main.LoadData(self.current_win)

class RecentsManager:
	recent_files = []

	def reset(self):
		Main.Reset()

	def save_recent(self):
		with open(self.working_path+"/StarTrak.bin", "wb") as f:
			pickle.dump(self.recent_files, f, pickle.HIGHEST_PROTOCOL)

	def load_recent(self):
		if (isfile(self.working_path + "/StarTrak.bin")):
			with open(self.working_path + "/StarTrak.bin", "rb") as f:
				try:
					self.recent_files = pickle.load(f)
				except:
					pass
		else:
			self.save_recent()


def __init__():
	global recent_manager
	recent_manager = RecentsManager()
