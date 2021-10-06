

CURRENT_VER = 1
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
		self.background = 1
		self.bsample = 3
		self.version = 0

	def PrintData(self, header=True):
		if header:
			name_lenght = max(len(self.name) - 6, 0)
			print("Nombre" + " "*name_lenght,"", "Ubicacion", "Brillo", "Fondo", "Radio", "Area", "Señal/Fondo", "Tamaño de muestra", sep="\t")
		print(self.name,"",self.location, self.value, int(self.background), self.radius, self.radius**2, "%.3f" % self.snr,"", self.bsample, sep="\t")
		