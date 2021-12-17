import tkinter
import STCore as st
from STCore.classes import ui

APP_VERSION = "1.2.0"
if __name__ == '__main__':
	tk = tkinter.Tk()
	tk.state('zoomed')
	tk.minsize(1140, 550)
	tk.config(**st.styles.FRAME)
	tk.wm_title("StarTrak {0}".format(APP_VERSION))

	st.styles.load_styles()
	st.icons.load_icons()

	main = ui.MainScreenUI(tk)

	main.config_callback(toplevel=None)
	main.build(tk)
	tk.mainloop()
