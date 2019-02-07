import __main__ as Main
import pickle
def Awake():
	global CurrentFilePath, FileItemList, StarItemList, TrackItemList, CurrentWindow, TkWindowRef
	CurrentFilePath = ""
	FileItemList = []
	StarItemList = []
	TrackItemList = []
	CurrentWindow = 0
	TkWindowRef = None

def Reset():
	global CurrentFilePath, FileItemList, StarItemList, TrackItemList, CurrentWindow
	Main.Reset()
	CurrentFilePath = ""
	FileItemList = []
	StarItemList = []
	TrackItemList = []
	CurrentWindow = 0

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
	Main.WindowName()

def LoadData(filepath):
	global CurrentFilePath, FileItemList, StarItemList, TrackItemList, CurrentWindow
	Reset()
	CurrentFilePath = filepath
	with open(filepath, "rb") as inp:
		FileItemList = pickle.load(inp)
		StarItemList = pickle.load(inp)
		TrackItemList = pickle.load(inp)
		CurrentWindow = pickle.load(inp)
	Main.WindowName()
	Main.LoadData(1)
