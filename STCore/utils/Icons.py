from PIL import Image, ImageTk
import tkinter as tk

from astropy.units.equivalencies import with_H0


Icons = {}
iconList = ["delete", "prev", "next", "add", "play", "stop", "restart", "multi",
		   "run", "open","plot","check","image", "export", "settings",
		   "conf1","conf2","conf3"] # Lista Constante con los nombres de los iconos sin extension
def GetIcon(key):
	try:
		return Icons[key]
	except:
		print ("El icono: "+key+" no existe.")
		pass

def Initialize():
	global Icons
	ThumbSize = 20,20
	
	for s in iconList:
		try:
			icon = Image.open("STCore/icons/"+s+".png")
			icon.thumbnail(ThumbSize)
			Icons.update({s : ImageTk.PhotoImage(icon)})
		except:
			print ("El icono: "+s+" no se encontro.")
			pass
	print (len(iconList), " Iconos cargados")