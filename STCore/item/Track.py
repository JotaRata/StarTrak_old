
from STCore import Debug
from STCore.item.Star import StarItem


class TrackItem(object):
	def __init__(self):
		self.star : StarItem = None
		self.lastPos = (0,0)
		self.lastSeen = -1
		self.lastValue = 0
		self.currPos = (0,0)
		self.currValue = 0
		self.trackedPos = []
		self.lostPoints = []
		self.active = -1
	def PrintData(self):
		Debug.Log(__name__, "Track info for: "+self.star.name)
		Debug.Log(__name__, "Tracked frames: " + str(len(self.trackedPos)) + "\t Lost frames: " + str(len(self.lostPoints)))
