from os import getcwd
from os.path import join
from sys import version_info as ver
from sys import modules, platform
from traceback import format_exc
from tkinter import messagebox
from datetime import datetime

DEBUG_PATH = join(getcwd(), "Startrak.log")
INCLUDE_IMPORTS = True

class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKCYAN = '\033[96m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

def initialize():
	with open(DEBUG_PATH, "w") as f:
		f.write(f"System date: {datetime.now()}\nOS: {platform}\nStartrak version: 1.2.0\nPython version: {ver.major}.{ver.minor}.{ver.micro}\n")
		if INCLUDE_IMPORTS:
			installed = [m for m in modules.keys() if not m.startswith('_')]
			installed.sort(key=str.lower)
			
			filter_indices = [j for i in range(len(installed)) for j in range(i+1, len(installed)) if installed[j].startswith(installed[i]+".")]
			installed_filtered = [installed[i] for i in range(len(installed)) if i not in filter_indices]
			f.write(f"Imported modules ({len(installed_filtered)}):\n{installed_filtered}\n\n")
		f.write("="*20+ " Startrak Log " + "="*20+"\n")
	return
def log(provider, message):
	print(bcolors.HEADER + "["+provider+"]", bcolors.OKBLUE + message + bcolors.ENDC)
	flush("["+provider+"]\tL: " + message)


def warn(provider, message):
	print(bcolors.HEADER + "["+provider+"]",bcolors.WARNING + message + bcolors.ENDC)
	flush("["+provider+"]\tW: " + message)


def error(provider, message, stop=True):
	end = ""
	if stop:
		end = "\n\nEnd of log"
	print(bcolors.HEADER + "["+provider+"]", bcolors.FAIL + message + bcolors.ENDC)
	messagebox.showerror("Error", message)

	flush("["+provider+"]\tE: " + message + "\n" + "-"*20+"\n"+format_exc()+end)
	if stop:
		print("Log saved at", DEBUG_PATH)
		quit()


def flush(message):
	with open(DEBUG_PATH, "a") as f:
		f.write(message+"\n")
