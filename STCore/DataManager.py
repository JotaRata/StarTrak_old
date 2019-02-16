import __main__ as Main
import pickle
def Awake():
	global CurrentFilePath, FileItemList, StarItemList, TrackItemList, CurrentWindow, TkWindowRef, ResultSetting, Brightness
	CurrentFilePath = ""
	FileItemList = []
	StarItemList = []
	TrackItemList = []
	CurrentWindow = 0
	TkWindowRef = None
	ResultSetting = None
	Brightness = -1

def Reset():
	global CurrentFilePath, FileItemList, StarItemList, TrackItemList, CurrentWindow, ResultSetting, Brightness
	Main.Reset()
	CurrentFilePath = ""
	FileItemList = []
	StarItemList = []
	TrackItemList = []
	CurrentWindow = 0
	ResultSetting = None
	Brightness = -1

def PrintData():
	print CurrentFilePath
	print FileItemList
	print StarItemList
	print TrackItemList
	print CurrentWindow

def SaveData(filepath):
	CurrentFilePath = filepath
	with open(filepath, "wb") as out:
		pickle.dump(FileItemList, out, pickle.HIGHEST_PROTOCOL)
		pickle.dump(StarItemList, out, pickle.HIGHEST_PROTOCOL)
		pickle.dump(TrackItemList, out, pickle.HIGHEST_PROTOCOL)
		pickle.dump(CurrentWindow, out, pickle.HIGHEST_PROTOCOL)
		pickle.dump(ResultSetting, out, pickle.HIGHEST_PROTOCOL)
		pickle.dump(Brightness, out, pickle.HIGHEST_PROTOCOL)
	Main.WindowName()

def LoadData(filepath):
	global CurrentFilePath, FileItemList, StarItemList, TrackItemList, CurrentWindow, ResultSetting, Brightness
	Reset()
	CurrentFilePath = filepath
	with open(filepath, "rb") as inp:
		try:
			FileItemList = pickle.load(inp)
			StarItemList = pickle.load(inp)
			TrackItemList = pickle.load(inp)
			CurrentWindow = pickle.load(inp)
			ResultSetting = pickle.load(inp)
			Brightness = pickle.load(inp)
		except:
			pass
	Main.WindowName()
	Main.LoadData(CurrentWindow)
