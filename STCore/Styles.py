
from tkinter import ttk
import matplotlib.pyplot as plt

plt.style.use("dark_background")

style =ttk.Style()
style.theme_use("awdark")
style.configure("Vertical.TScrollbar", gripcount=3,
			background="#367783", lightcolor="gray35",
			troughcolor="gray18", bordercolor="gray10", arrowcolor="azure2", relief ="flat",
			width="20", borderwidth = 0)
style.map("Vertical.TScrollbar",
	background=[ ('!active','#367783'),('pressed', '#49A0AE'), ('active', '#49A0AE')]
	)

style.configure("Horizontal.TScale", gripcount=3,
			background="#49A0AE", lightcolor="gray35",
			troughcolor="gray8", bordercolor="gray10", arrowcolor="azure2", relief ="flat",
			width="20", borderwidth = 0)
style.map("Horizontal.TScale",
	background=[ ('!active','#49A0AE'),('pressed', '#49A0AE'), ('active', '#49A0AE')]
	)
style.configure("TFrame", background = "gray15", relief="flat")
style.configure("TLabel", background = "gray15", foreground ="gray80")
style.configure("TLabelFrame", background = "gray15", highlightcolor="gray15")

style.configure("TButton", relief = "flat")
style.map("TButton",
	foreground=[('!active', 'gray90'),('pressed', 'gray95'), ('active', 'gray90')],
	background=[ ('!active','grey20'),('pressed', 'gray26'), ('active', 'gray24')]
	)	
style.configure("Highlight.TButton", relief = "flat")
style.map("Highlight.TButton",
	foreground=[('!active', 'gray90'),('pressed', 'gray95'), ('active', 'gray90')],
	background=[ ('!active','aquamarine4'),('pressed', 'aquamarine2'), ('active', 'aquamarine4')]
	)	