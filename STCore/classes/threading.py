
from abc import ABC, abstractmethod
from queue import Queue
from threading import Thread
from dataclasses import dataclass

# ----------------- Rendering ------------------------
class MPLRequest(ABC):
	@abstractmethod
	def process(self):
		raise NotImplementedError()

class RenderThread(Thread):
	def __init__(self, max_calls = 1, *args, **kwargs):
		Thread.__init__(self, target=self.__process__, name="Render thread", daemon=True, *args, **kwargs)
		
		self.render_queue = Queue(max_calls)
		
	def __process__(self):
		while True:
			try:
				entry = self.render_queue.get()
				entry.process()
			except:
				continue
	def enqueue(self, entry : MPLRequest):
		if not isinstance(entry, MPLRequest):
			raise TypeError('parameter entry needs to derive from MPLRequest')
		try:
			self.render_queue.put(entry)
		except:
			pass
@dataclass
class ChangeLevelsRequest(MPLRequest):
	''' Change Level Request
	This class takes the current data range and levels percentage to delegate a function which updates the mpl canvas in another thread
	'''
	levels 		: tuple
	data_range	: float
	callback 	: callable

	def process(self):
		minv = self.levels[0] * self.data_range
		maxv = self.levels[1] * self.data_range
		self.callback(minv, maxv)

# -----------------------------------------------------------------------

render_thread = RenderThread()