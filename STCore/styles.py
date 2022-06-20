# coding=utf-8
import tkinter as tk

from STCore import debug
# A class that stores kwagrs to be used with tkinter tk module
# ---------------------------

# Colors
base_primary = 		"#37474F"
base_dark = 		"#232931"
base_light = 		"#393E46"
base_highlight =	"#007769"

hover_primary = "#525c61"
hover_dark =	"#3a4448"
hover_highlight="#307a71"

press_primary = "#29353b"
press_dark =	"#0c181d"
press_highlight="#00594f"

# img = Image.open("STCore/button.gif")
def load_styles():
	global button_base, button_hover, button_press
	global hbutton_base, hbutton_hover, hbutton_press
	global handle_base, handle_hover, handle_press
	try:
		button_base = tk.PhotoImage(file="STCore/res/button_base.png")
		button_hover = tk.PhotoImage(file="STCore/res/button_hover.png")
		button_press = tk.PhotoImage(file="STCore/res/button_press.png")
		hbutton_base = tk.PhotoImage(file="STCore/res/hbutton_base.png")
		hbutton_hover = tk.PhotoImage(file="STCore/res/hbutton_hover.png")
		hbutton_press = tk.PhotoImage(file="STCore/res/hbutton_press.png")

		handle_base = tk.PhotoImage(file="STCore/res/handle/handle_base.png")
		handle_hover = tk.PhotoImage(file="STCore/res/handle/handle_hover.png")
		handle_press = tk.PhotoImage(file="STCore/res/handle/handle_press.png")
	except Exception as e:
		debug.warn(__name__, "Algunos resursos no pudieron ser cargados: " + e.__str__())

# Styles
FRAME =		{"bg" : base_dark, "relief" : "flat"}
SFRAME = 	{"bg" : base_primary, "relief" : "raised"}
HFRAME = 	{"bg" : base_light, "relief" : "flat"}

LABEL =		{"bg" : base_dark, "fg" : "gray70", "relief" : "flat"}
SLABEL = 	{"bg" : base_primary, "fg" : "gray80", "relief" : "flat"}
HLABEL = 	{"bg" : base_light, "fg" : "white", "relief" : "flat"}


BUTTON = 	{"bg" : base_primary, "fg" : "white", "relief" : "flat"	,	"border":0 } 
DBUTTON =	{"bg" : base_dark, "fg" : "gray70", "relief" : "flat"	,	"border":0 }
HBUTTON =	{"bg" : base_highlight, "fg" : "white", "relief" : "flat" 	,"border":0} 
# SLIGHT =	{"bg" : "#48a697", "fg" : "black", "relief" : "flat"}
# SDARK = 	{"bg" : "#004a3f", "fg" : "gray80", "relief":"flat"}