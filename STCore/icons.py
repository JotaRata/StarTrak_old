import tkinter as tk

from astropy.units.equivalencies import with_H0
from PIL import Image, ImageTk
from STCore import debug

loaded_images = {}
iconList = ["delete", "prev", "next", "add", "play", "stop", "restart", "multi",
		   "run", "open","plot","check","image", "export", "settings",
		   "conf1","conf2","conf3"] # Lista Constante con los nombres de los iconos sin extension
def get_icon(key):
	try:
		return loaded_images[key]
	except:
		debug.warn (__name__, "El icono: "+key+" no existe.")
		pass

def load_icons():
	global loaded_images
	ThumbSize = 20,20
	
	for s in iconList:
		try:
			icon = Image.open("STCore/res/"+s+".png")
			icon.thumbnail(ThumbSize)
			loaded_images.update({s : ImageTk.PhotoImage(icon)})
		except:
			debug.warn (__name__, "El icono: "+s+" no se encontro.")
			pass
	debug.log (__name__, str(len(iconList))+ " Iconos cargados")
