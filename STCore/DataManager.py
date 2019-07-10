import __main__ as Main
import pickle
from os.path import isfile
WorkingPath = ""
def Awake():
	global CurrentFilePath, FileItemList, StarItemList, TrackItemList, CurrentWindow
	global TkWindowRef, ResultSetting, Levels, RecentFiles, ResultData, RuntimeEnabled, ResultConstant, RuntimeDirectory
	CurrentFilePath = ""
	FileItemList = []
	StarItemList = []
	TrackItemList = []
	CurrentWindow = 0
	TkWindowRef = None
	ResultSetting = None
	Levels = -1
	RecentFiles = []
	ResultData = None
	ResultConstant = None
	RuntimeEnabled = False
	RuntimeDirectory = ""
def Reset():
	global CurrentFilePath, FileItemList, StarItemList, TrackItemList, CurrentWindow, ResultSetting, Levels, ResultData, RuntimeEnabled, ResultConstant, RuntimeDirectory
	Main.Reset()
	CurrentFilePath = ""
	FileItemList = []
	StarItemList = []
	TrackItemList = []
	CurrentWindow = 0
	ResultSetting = None
	Levels = -1
	ResultData = None
	ResultConstant = None
	RuntimeEnabled = False
	RuntimeDirectory = None

def PrintData():
	print CurrentFilePath
	print FileItemList
	print StarItemList
	print TrackItemList
	print CurrentWindow
def SaveRecent():
	with open(WorkingPath+"/StarTrak.bin", "wb") as f:
		pickle.dump(RecentFiles, f, pickle.HIGHEST_PROTOCOL)
def LoadRecent():
	global RecentFiles
	if (isfile(WorkingPath+"/StarTrak.bin")):
		with open(WorkingPath+"/StarTrak.bin", "rb") as f:
			try:
				RecentFiles = pickle.load(f)
			except:
				pass
	else:
		SaveRecent()
def SaveData(filepath):
	global CurrentFilePath
	CurrentFilePath = filepath
	with open(filepath, "wb") as out:
		pickle.dump(FileItemList, out, pickle.HIGHEST_PROTOCOL)
		pickle.dump(StarItemList, out, pickle.HIGHEST_PROTOCOL)
		pickle.dump(TrackItemList, out, pickle.HIGHEST_PROTOCOL)
		pickle.dump(CurrentWindow, out, pickle.HIGHEST_PROTOCOL)
		pickle.dump(ResultSetting, out, pickle.HIGHEST_PROTOCOL)
		pickle.dump(Levels, out, pickle.HIGHEST_PROTOCOL)
		pickle.dump(ResultData, out, pickle.HIGHEST_PROTOCOL)
		pickle.dump(ResultConstant, out, pickle.HIGHEST_PROTOCOL)
		pickle.dump(RuntimeEnabled, out, pickle.HIGHEST_PROTOCOL)
		pickle.dump(RuntimeDirectory, out, pickle.HIGHEST_PROTOCOL)
	Main.WindowName()

def LoadData(filepath):
	global CurrentFilePath, FileItemList, StarItemList, TrackItemList, CurrentWindow, ResultSetting, Levels, ResultData, ResultConstant, RuntimeEnabled, RuntimeDirectory
	Reset()
	CurrentFilePath = filepath
	with open(filepath, "rb") as inp:
		try:
			FileItemList = pickle.load(inp)
			StarItemList = pickle.load(inp)
			TrackItemList = pickle.load(inp)
			CurrentWindow = pickle.load(inp)
			ResultSetting = pickle.load(inp)
			Levels = pickle.load(inp)
			ResultData = pickle.load(inp)
			ResultConstant = pickle.load(inp)
			RuntimeEnabled = pickle.load(inp)
			RuntimeDirectory = pickle.load(inp)
		except:
			pass
	Main.WindowName()
	Main.LoadData(CurrentWindow)
