import STCore.ImageView
import STCore.Tracker
import STCore.Results
import STCore.DataManager
from tkinter import filedialog
from os.path import dirname, abspath, basename, isfile
from astropy.io import fits
#import pyfits as fits
from os.path import  getmtime
from time import sleep, strftime, localtime, strptime,gmtime, mktime
from STCore.item.File import FileItem
from STCore.utils.backgroundEstimator import GetBackgroundMean
import os, time
import tkinter as tk
import __main__
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
		__main__.Destroy()
		STCore.ImageView.Awake(root, filesList)
		dirState = dict ([(f, None) for f in os.listdir (directoryPath)])
		STCore.DataManager.RuntimeDirectory = directoryPath

def LoadFile(root):
	global startFile, directoryPath, filesList
	startFile = str(filedialog.askopenfilename(parent = root, filetypes=[("FIT Image", "*.fits;*.fit"), ("Todos los archivos",  "*.*")]))
	if len(startFile) == 0:
		print ("Cancelled Analysis")
		return False
	directoryPath = dirname(startFile)
	filesList.append(CreateFileItem(startFile))
	return len(startFile) > 0

def CreateFileItem(path):
	item = FileItem()
	item.path = str(path)
	item.data, hdr = fits.getdata(item.path, header = True)
	# Request DATE-OBS keyword to extract date information (previously used NOTE keyword which was not always available)
	try:
		item.date = strptime(hdr["DATE-OBS"], "%Y-%m-%dT%H:%M:%S.%f")
	except:
		print ("File has no DATE-OBS keyword in Header   -   using system time instead..")
		item.date = gmtime(getmtime(item.path))
		pass
	
	return item

def UpdateFileList(root, path):
	item = CreateFileItem(path)
	filesList.append(item)
	STCore.Tracker.CurrentFile += 1
	STCore.Tracker.UpdateTrack(root, filesList, STCore.ImageView.Stars, STCore.Tracker.CurrentFile, False)
	stIndex = 0
	temp = 0
	data = item.data
	if STCore.DataManager.CurrentWindow == 3:
		return
	while stIndex < len(STCore.Tracker.TrackedStars):
		value = STCore.Results.GetValue(data, STCore.Tracker.TrackedStars[stIndex], STCore.Results.Constant,  STCore.Tracker.CurrentFile, GetBackgroundMean(data))
		X = GetXTick(STCore.Tracker.CurrentFile)
		point = [X, -value +  STCore.Results.Constant]
		STCore.Results.AddPoint(point, stIndex)
		stIndex += 1
	STCore.Results.UpdateScale(True)
	STCore.DataManager.FileItemList = filesList
	
def GetXTick(index):
	epoch = mktime(filesList[0].date)
	if STCore.ResultsConfigurator.SettingsObject.sortingMode == 0:
		return mktime(filesList[index].date) - epoch
	else:
		return index
def StartRuntime(root):
	global filesList
	filesList = list(filter(lambda item: item.Exists(), filesList))
	STCore.Tracker.UpdateTrack(root, filesList, STCore.ImageView.Stars, STCore.Tracker.CurrentFile, False)
	STCore.ResultsConfigurator.Awake(root, filesList, STCore.Tracker.TrackedStars)
	WatchDir(root)

def StopRuntime():
	 STCore.DataManager.RuntimeEnabled = False
	
def WatchDir(root):
	global directoryPath, dirState
	if STCore.DataManager.CurrentWindow == 2:
		return
	if STCore.DataManager.RuntimeEnabled == True:
		after = dict ([(f, None) for f in os.listdir (directoryPath)])
		added = [f for f in after if not f in dirState]
		removed = [f for f in dirState if not f in after]
		if added:
			for a in added:
				try:
					UpdateFileList(root, os.path.join(directoryPath, str(a)))
					time.sleep(0.001)
				except Exception as e:
						print ("No se pudo abrir el archivo: ", str(a))
						print (e)
						pass
		if removed: print ("Removed: ", ", ".join (removed))
		dirState = after
		STCore.DataManager.RuntimeDirState = dirState
		root.after(100, lambda: WatchDir(root))
