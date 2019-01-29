
class FileItem(object):
	def __init__(self):
		self.path = ""
		self.active = 1
		self.data = None
	
	def PrintData(self):
		print "File: "+self.path+", Active: "+str(self.active)+" Containing: "+str(self.data.size)