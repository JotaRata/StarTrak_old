# coding=utf-8
import tkinter as tk
# A class that stores kwagrs to be used with tkinter tk module
# ---------------------------

# Colors
base_primary = 		"#37474F"
base_dark = 		"#102027"
base_light = 		"#62727b"
base_highlight =	"#007769"

hover_primary = "#525c61"
hover_dark =	"#3a4448"
hover_highlight="307a71"

press_primary = "#29353b"
press_dark =	"#0c181d"
press_highlight="#00594f"
# Images
button_base = None
button_hover = None
button_press = None

hbutton_base = None
hbutton_hover = None
hbutton_press = None
# img = Image.open("STCore/button.gif")
def load_styles():
	global button_base, button_hover, button_press
	global hbutton_base, hbutton_hover, hbutton_press
	button_base = tk.PhotoImage(file="STCore/res/button_base.png")
	button_hover = tk.PhotoImage(file="STCore/res/button_hover.png")
	button_press = tk.PhotoImage(file="STCore/res/button_press.png")
	hbutton_base = tk.PhotoImage(file="STCore/res/hbutton_base.png")
	hbutton_hover = tk.PhotoImage(file="STCore/res/hbutton_hover.png")
	hbutton_press = tk.PhotoImage(file="STCore/res/hbutton_press.png")

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