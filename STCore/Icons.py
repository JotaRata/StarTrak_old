import tkinter as tk

from astropy.units.equivalencies import with_H0
from PIL import Image, ImageTk

import Debug

loaded_images = {}
iconList = ["delete", "prev", "next", "add", "play", "stop", "restart", "multi",
		   "run", "open","plot","check","image", "export", "settings",
		   "conf1","conf2","conf3"] # Lista Constante con los nombres de los iconos sin extension
def GetIcon(key):
	try:
		return loaded_images[key]
	except:
		Debug.Warn (__name__, "El icono: "+key+" no existe.")
		pass

def Initialize():
	global loaded_images
	ThumbSize = 20,20
	
	for s in iconList:
		try:
			icon = Image.open("STCore/res/"+s+".png")
			icon.thumbnail(ThumbSize)
			loaded_images.update({s : ImageTk.PhotoImage(icon)})
		except:
			Debug.Warn (__name__, "El icono: "+s+" no se encontro.")
			pass
	Debug.Log (__name__, str(len(iconList))+ " Iconos cargados")
