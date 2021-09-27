
class StarItem(object):
	def __init__(self):
		self.name = "Star"
		self.type = 0
		self.location = (0,0)
		self.value = 0
		self.bounds = 0
		self.threshold = 100
		self.radius = 0
		self.std = 0
		self.bsigma = 2

	def PrintData(self):

		print("Nombre\tGuia\tUbicacion\tBrillo\tTamaño\tVariabilidad\tSeñal a ruido")
		print(self.name, "*" if self.type == 1 else "",self.location, self.value, self.radius, self.threshold,"", "%.3f" % self.std, sep="\t")
		