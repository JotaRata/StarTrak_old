from astropy.io.fits import Header
_FILE_VERSION = 1
class FileItem(object):
	def __init__(self):
		self.path = ""
		self.active = 1
		self.data = None
		self.date = None  # No confundir con data
		self.header : Header = None
		self.version = 1
	def PrintData(self):
		print ("File: "+self.path+", Active: "+str(self.active)+" Containing: "+str(self.data.size))
	def Exists(self):
		from os.path import  isfile
		return isfile(self.path)