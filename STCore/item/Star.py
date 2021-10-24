

CURRENT_VER = 1

# Parameters (Name, Units)
NAME=	("Nombre", "")
LOC=	("Ubicacion", "(pix, pix)")
SUM=	("Suma", "adu")
BACK=	("Fondo Promedio", "adu/pix^2")
RADIUS=	("Radio", "pix")
AREA=	("Area", "pix^2")
SBR=	("Señal/Fondo", "")
BSIZE=	("Muestra", "pix")
BOUNDS=	("Limites", "pix")
GUIDE=	("Guia", "")
VALUE=	("Referencia", "adu")
FLUX=	("Flujo", "adu/pix^2")
FBACK=	("Fondo", "adu")


class StarItem(object):
	def __init__(self):
		self.name = "Star"
		self.type = 0
		self.location = (0,0)
		self.value = 0
		self.flux = 0
		self.bounds = 0
		self.threshold = 100
		self.radius = 0
		self.snr = 0
		self.background = 1
		self.bsample = 3
		self.version = 0

	def PrintData(self, attributes : tuple, header=True, sep="{:<15} ", stdout= None):
		base : str= sep* len(attributes)
		if header:
			
			print(base.format(*[i[0] for i in attributes]), file=stdout)
			print(base.format(*[i[1] for i in attributes]), file=stdout)
		print(base.format(*[str(self.GetAttribute(i[0])) for i in attributes]), file=stdout)

	def GetAttribute(self, attribute : str):
		attr = attribute.title()
		if attr == 	NAME[0]:
			return self.name
		elif attr ==LOC[0]:
			return self.location
		elif attr ==SUM[0]:
			return int(self.flux)
		elif attr ==BACK[0]:
			return int(self.background)
		elif attr ==RADIUS[0]:
			return self.radius
		elif attr ==AREA[0]:
			return int((2*self.radius)**2)
		elif attr ==FLUX[0]:
			return int(self.flux / (2*self.radius)**2)
		elif attr ==SBR[0]:
			return "%0.3f"%self.snr
		elif attr ==GUIDE[0]:
			return self.type
		elif attr ==BSIZE[0]:
			return self.bsample
		elif attr ==BOUNDS[0]:
			return self.bounds
		elif attr ==VALUE[0]:
			return self.value
		elif attr ==FBACK[0]:
			return int(self.background * (2*self.radius)**2)
		else:
			raise ValueError("El parametro \"%s\" no existe" % attr)