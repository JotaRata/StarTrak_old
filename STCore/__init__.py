# Dice a Python que esta carpeta contiene modulos
import STCore.styles as styles
import STCore.debug as debug
import STCore.icons as icons
import STCore.lang as lang
import STCore.bin.env as env
import STCore.bin.data_management
import STCore.classes.drawables
import STCore.classes.ui
import STCore.classes.items


def tk_exception(*args):
	debug.error(
		"Tk", lang.get("tk_error"), stop=False)
