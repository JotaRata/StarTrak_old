from tkinter import Tk
from STCore.Settings import WorkingPath
from STCore.bin.app.ui import STView
from bin.data_management import *
from bin.app.ui import STView
#--------------------
scope 			: str
working_path 	: str
tk				: Tk
current_view 	: STView
views 	: dict[str, STView]
recent_manager	: RecentsManager
session_manager	: SessionManager