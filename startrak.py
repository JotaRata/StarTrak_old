from os import name
import tkinter
import STCore as st
from STCore import debug
from STCore.classes import ui

NAME = "stcore"
APP_VERSION = "1.2.0"
if __name__ == '__main__':
	try:
		tk = tkinter.Tk()
		tk.state('zoomed')
		tk.minsize(1140, 550)
		tk.config(**st.styles.FRAME)
		tk.wm_title("StarTrak {0}".format(APP_VERSION))
		tk.report_callback_exception = st.tk_exception
		tk.columnconfigure((0, ), weight=1)
		tk.rowconfigure((0, 1), weight=1)

		st.debug.initialize()
		st.styles.load_resources()
		# st.icons.load_icons()
		st.lang.register_languages()
		st.lang.set_current_language("es")

		view = ui.ViewerUI(tk)
		view.grid(row=0, column=0, sticky='new')
		view.config_callback(toplevel=None)
		view.build(tk)

		main = ui.SelectorUI(tk, width = 30)
		main.grid(row=0, column=1, rowspan=2, sticky='news')
		main.config_callback(toplevel=None)
		main.build(tk)

		tk.mainloop()
	except:
		debug.error(NAME, st.lang.get('runtime_error'))
