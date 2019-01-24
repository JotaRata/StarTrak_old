
class FileItem():
	path = ""
	active = None
	data = None
	
	def PrintData(self):
		print "File: "+self.path+", Active: "+str(self.active.get())+" Containing: "+str(self.data.size)