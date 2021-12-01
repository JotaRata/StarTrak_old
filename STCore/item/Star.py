import numpy

#comentario pal primer commit: las guatitas son más malas que la chucha

CURRENT_VER = 2

# Parameters (Name, Units)
NAME=	("Nombre Estrella", "")
LOC=	("Ubicacion Estrella", "(pix, pix)")
SUM=	("Flujo Estrella", "adu * pix²")

RADIUS=	("Radio Estrella", "pix")
AREA=	("Area Estrella", "pix²")
SBR=	("Señal/Fondo", "")
BOUNDS=	("Limites", "pix")
GUIDE=	("Guia", "")
VALUE=	("Referencia", "adu")
FLUX=	("Intensidad Estrella", "adu")

FBACK=	("Fondo", "adu * pix²")
MBACK=	("Media Fondo", "adu")
DBACK=	("Variacion Fondo", "adu")
VBACK= 	("Valor Muestras", "adu")
SUMVBACK=  ("Flujo Muestras Fondo (L, B, R, U)", "adu * pix²")
BACKREFS= ("Referencias Fondo (L, B, R, U)", "adu")
FLUXBACK=  ("Intensidad Fondo", "adu")
BSIZE=	("Ancho Muestra", "pix")
ABACK=  ("Area De Cada Muestra", "pix²")

NETFLUX= ("Intensidad Neta", "adu")
APPMAG= ('Magnitud Aparente (Celular)', "")

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
		self.background : tuple = None		# [0]: values, [1]: status, [2]: mean, [3]: std, [4]: sum_values, [5]: background_references
		self.bsample = 3
		self.barea = 0
		self.version = 2

	def PrintData(self, attributes : tuple, header=True, sep="{:^15} ", stdout= None):
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
		elif attr ==MBACK[0]:
			return int(self.background[2])
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
			return int(self.background[2] * (2*self.radius)**2)
		elif attr ==DBACK[0]:
			return "%.3f" % self.background[3]
		elif attr ==VBACK[0]:
			return tuple(self.background[0])
		elif attr ==SUMVBACK[0]:
			return tuple(self.background[4])
		elif attr ==ABACK[0]:
			return int(self.barea)
		elif attr ==FLUXBACK[0]:
			return int(sum(self.background[4])/(self.barea*4))
		elif attr ==BACKREFS[0]:
			return tuple(self.background[5])
		elif attr ==NETFLUX[0]:
			return int(int(self.flux / ((2*self.radius)**2)) - int(sum(self.background[4])/(self.barea*4)))
		elif attr ==APPMAG[0]:
			return 14-2.5*numpy.log10(int(int(self.flux / ((2*self.radius)**2)) - int(sum(self.background[4])/(self.barea*4))))
		else:
			raise ValueError("El parametro \"%s\" no existe" % attr)