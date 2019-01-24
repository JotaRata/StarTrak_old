
class TrackItem():
	lastPos = (0,0)
	lastSeen = -1
	lastValue = 0
	currPos = (0,0)
	currValue = 0
	trackedPos = []

	def PrintData(self):
		print "Last seen at file: ", self.lastSeen," in ", self.lastPos," with value ",self.lastValue, "tracked for", len(self.trackedPos), "frames"
		print "Lost Points: ", len(filter(lambda x: x.size == 0, self.trackedPos))