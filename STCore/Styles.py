# coding=utf-8
from os import listdir, scandir
from os.path import isdir, join, basename, splitext
import tkinter as tk
from STCore import debug
# A class that stores kwagrs to be used with tkinter tk module
# ---------------------------

# Colors
base_primary = 	'#263238'
base_dark = 	'#000a12'
base_light = 	'#4f5b62'
base_highlight ='#00897b'

hover_primary = '#364248'
hover_dark =	'#3a4448'
hover_highlight='#307a71'

press_primary = '#29353b'
press_dark =	'#0c181d'
press_highlight='#00594f'

__res = {}
def load_resources():
	res_dir = 'STCore/res'
	if not isdir(res_dir):
		debug.error(__name__, 'No se pueden cargar los recursos de StarTrak')
	
	sub_dir = [f.path for f in scandir(res_dir) if f.is_dir()]
	for directory in sub_dir:
		for file in listdir(directory):
			if '.png' in file:
				name = splitext(basename(file))[0]
				__res[name] = tk.PhotoImage(file= join(directory, file))

def get_resource(name : str) -> tk.PhotoImage:
	try:
		return __res[name]
	except:
		debug.warn(__name__, 'No se puede cargar \'{0}\' '.format(name))
		return None
def get_resources(*names : tuple[str]) -> tuple[tk.PhotoImage]:
	return (get_resource(res) for res in names)
# Styles
FRAME =		{'bg' : base_dark, 		'relief' : 'flat'}
SFRAME = 	{'bg' : base_primary, 	'relief' : 'raised'}
HFRAME = 	{'bg' : base_light, 	'relief' : 'flat'}

LABEL =		{'bg' : base_dark, 	  'fg' : 'gray70', 	'relief' : 'flat'}
SLABEL = 	{'bg' : base_primary, 'fg' : 'gray80', 	'relief' : 'flat'}
HLABEL = 	{'bg' : base_light,   'fg' : 'white', 	'relief' : 'flat'}


BUTTON = 	{'bg' : base_primary, 	 'fg' : 'white', 	'relief' : 'flat'	,	'border':0 , 'activebackground':press_primary} 
DBUTTON =	{'bg' : base_dark, 		 'fg' : 'gray70', 	'relief' : 'flat'	,	'border':0 ,  'activebackground':press_dark}
HBUTTON =	{'bg' : base_highlight,  'fg' : 'white', 	'relief' : 'flat' 	,	'border':0 , 'activebackground':press_highlight}  
# SLIGHT =	{'bg' : '#48a697', 	 'fg' : 'black', 	'relief' : 'flat'}
# SDARK = 	{'bg' : '#004a3f', 	 'fg' : 'gray80', 	'relief':'flat'}