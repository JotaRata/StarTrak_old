
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
		print "-------------- Datos de la estrella ---------------------"
		print "Nombre: ", self.name, "\t\t\t Tipo: ", self.type
		print "Ubicacion: ", self.location, "\t\t\t Brillo: ", self.value
		print "Radio: ", self.bounds,"\t\t\t Tolerancia: ", self.threshold
		print "----------------------------------------------------------"