# Dice a Python que esta carpeta contiene modulos
import STCore.styles as styles
import STCore.debug as debug
import STCore.icons as icons
import STCore.lang as lang
import STCore.bin.env as env
import STCore.bin.data_management as data
import STCore.classes.drawables as drawables
import STCore.classes.items as items
import STCore.classes.ui


def tk_exception(*args):
	debug.error(
		"Tk", lang.get("tk_error"), stop=False)
