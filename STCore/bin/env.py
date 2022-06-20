from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from tkinter import Tk
	from STCore.bin.data_management import *
	from STCore.bin.app.ui import STView
#--------------------
scope 			: str				= None
working_path 	: str				= None
tk				: Tk				= None
current_view 	: STView			= None
views 			: dict[str, STView]	= None
recent_manager	: RecentsManager	= None
session_manager	: SessionManager	= None
settings_manager: SettingsManager	= None
print(TYPE_CHECKING, scope)