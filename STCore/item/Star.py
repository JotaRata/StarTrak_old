
class StarItem(object):
	def __init__(self):
		self.name = "Star"
		self.type = 0
		self.location = (0,0)
		self.value = 0
		self.bounds = 0
		self.threshold = 100
		self.radius = 0
		self.snr = 0
		self.background = 0
		self.bsigma = 2

	def PrintData(self):

		print("Nombre\tGuia\tUbicacion\tBrillo\tFondo\tTamaño\tArea\tVariabilidad\tSeñal a ruido")
		print(self.name, "*" if self.type == 1 else "",self.location, self.value, "%.3f"%self.background, self.radius, self.radius**2, self.threshold,"", "%.3f" % self.snr, sep="\t")
		