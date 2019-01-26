
import STCore.ImageSelector
import Tkinter as tk
import tkFileDialog
import ttk

def Awake(root):
	global StartFrame
	StartFrame = tk.Frame(root, width = 1100, height = 400)
	StartFrame.pack(expand = 1, fill = tk.BOTH)
	tk.Label(StartFrame, text = "Bienvenido a StarTrak").pack()
	tk.Label(StartFrame, text = "Por favor seleccione las imagenes que quiera analizar").pack(anchor = tk.CENTER)
	ttk.Button(StartFrame, text = "Seleccionar Imagenes", command = LoadFiles).pack(anchor = tk.CENTER)
	

def LoadFiles():
	paths = tkFileDialog.askopenfilenames(parent = Window, filetypes=[("FIT Image", "*.fits;*.fit")])
	paths = Window.tk.splitlist(paths)
	Destoy()
	STCore.ImageSelector.Awake(Window, paths)

def Destoy():
	StartFrame.destroy()

if __name__ == "__main__":
	Window = tk.Tk()
	StartFrame = None
	Window.wm_title(string = "StarTrak v1.0.0")
	Window.geometry("1080x480")
	Awake(Window)
	#ImageView.Awake(Window)
	Window.mainloop()
def GetWindow():
	return Window 