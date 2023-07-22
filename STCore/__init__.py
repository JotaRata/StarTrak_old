from . import styles
from . import debug
from . import icons
from . import lang
from .bin import env
from .bin import data_management as data
from .classes import drawables
from .classes import items
from .classes import ui
from .classes import threading as thread
from .classes.threading import render_thread

NAME = "stcore"
APP_VERSION = "1.2.0"


def tk_exception(*args):
    debug.error(
        "Tk", lang.get("tk_error"), stop=False)
