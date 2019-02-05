
class TrackItem(object):
	def __init__(self):
		self.star = None
		self.lastPos = (0,0)
		self.lastSeen = -1
		self.lastValue = 0
		self.currPos = (0,0)
		self.currValue = 0
		self.trackedPos = []
		self.lostPoints = []
	def PrintData(self):
		print ""
		print self.star.name, " Track Info: "
		print "Last seen at file: ", self.lastSeen," in ", self.lastPos," with value ",self.lastValue, "tracked for", len(self.trackedPos), "frames"
		print "Lost Points: ", len(self.lostPoints)