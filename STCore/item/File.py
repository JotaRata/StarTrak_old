
class FileItem(object):
	def __init__(self):
		self.path = ""
		self.active = None
		self.data = None
	
	def PrintData(self):
		print "File: "+self.path+", Active: "+str(self.active)+" Containing: "+str(self.data.size)