
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
		print ("-"*30 + "Datos de la estrella"+ "-"*30)
		print ("Nombre: ", self.name, "\t\t\t Tipo: ", self.type)
		print ("Ubicacion: ", self.location, "\t\t\t Brillo: ", self.value)
		print ("Radio: ", self.bounds,"\t\t\t Variabilidad: ", self.threshold*100,"%")
		print ("Bkg-Sigma: ", self.bsigma)
		print ("----------------------------------------------------------")