
class StarItem(object):
	def __init__(self):
		self.name = "Star"
		self.type = 0
		self.location = (0,0)
		self.value = 0
		self.bounds = 0
		self.threshold = 100
		self.radius = 0

	def PrintData(self):
		print "Nombre: ", self.name
		print "Tipo: ", self.type
		print "Ubicacion: ", self.location
		print "Brillo: ", self.value
		print "Radio: ", self.bounds

