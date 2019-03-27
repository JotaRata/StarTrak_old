import STCore.ImageView
import STCore.Tracker
import STCore.Results
import STCore.DataManager
import tkFileDialog
from os.path import dirname, abspath, basename, isfile
import pyfits as fits
from os.path import  getmtime
from STCore.item.File import FileItem
import os, time
import Tkinter as tk
#region Variables
directoryPath = ""
startFile = ""
filesList = []
dirState = None
#endregion
def Awake(root):
	global dirState
	if LoadFile(root):
		STCore.DataManager.RuntimeEnabled = True
		STCore.ImageView.Awake(root, filesList)
		dirState = dict ([(f, None) for f in os.listdir (directoryPath)])

def LoadFile(root):
	global startFile, directoryPath
	startFile = str(tkFileDialog.askopenfilename(parent = root, filetypes=[("FIT Image", "*.fits;*.fit"), ("Todos los archivos",  "*.*")]))
	directoryPath = dirname(startFile)
	filesList.append(CreateFileItem(startFile))
	return len(startFile) > 0

def CreateFileItem(path):
	item = FileItem()
	item.path = str(path)
	item.data, header = fits.getdata(item.path, header = True)
	item.date = getmtime(item.path)
	return item

def UpdateFileList(path):
	filesList.append(CreateFileItem(path))
	STCore.Tracker.CurrentFile += 1
	STCore.Tracker.UpdateTrack(filesList, STCore.ImageView.Stars, STCore.Tracker.CurrentFile, False)
	stIndex = 0
	temp = 0
	while stIndex < len(STCore.Tracker.TrackedStars):
		value = STCore.Results.GetValue(filesList, STCore.Tracker.TrackedStars[stIndex], STCore.Results.Constant, STCore.Results.BackgroundFlux, STCore.Tracker.CurrentFile)
		X = GetXTick(STCore.Tracker.CurrentFile)
		point = [X, value]
		STCore.Results.AddPoint(point, stIndex)
		stIndex += 1
	STCore.Results.UpdateScale()

def GetXTick(index):
	epoch = time.time()
	if STCore.ResultsConfigurator.SettingsObject.sortingMode == 0:
		return filesList[index].date - epoch
	else:
		return index
def StartRuntime(root):
	STCore.Tracker.CurrentFile = 0
	STCore.Tracker.UpdateTrack(filesList, STCore.ImageView.Stars, STCore.Tracker.CurrentFile, False)
	STCore.ResultsConfigurator.Awake(root, filesList, STCore.Tracker.TrackedStars)
	WatchDir(root)

def WatchDir(root):
	global directoryPath, dirState
	if STCore.DataManager.RuntimeEnabled == True:
		after = dict ([(f, None) for f in os.listdir (directoryPath)])
		added = [f for f in after if not f in dirState]
		removed = [f for f in dirState if not f in after]
		if added:
		   for a in added: 
			   UpdateFileList(os.path.join(directoryPath, str(a)))
			   time.sleep(0.01)
		if removed: print "Removed: ", ", ".join (removed)
		dirState = after
		root.after(1000, lambda: WatchDir(root))
