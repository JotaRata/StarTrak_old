from PIL import Image, ImageTk
import Tkinter as tk


Icons = {}
iconList = ["delete", "prev", "next", "add", "play", "stop", "restart", "multi",
		   "run", "open","plot","check","image", "export", "settings",
		   "conf1","conf2","conf3"] # Lista Constante con los nombres de los iconos sin extension

def Initialize():
	global Icons
	ThumbSize = 20,20
	
	for s in iconList:
		try:
			icon = Image.open("STCore/icons/"+s+".png")
			icon.thumbnail(ThumbSize)
			Icons.update({s : ImageTk.PhotoImage(icon)})
		except:
			print "El icono: "+s+" no existe."
			pass
	print len(iconList), " Icons loaded"