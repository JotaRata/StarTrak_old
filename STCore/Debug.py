from os import getcwd
from os.path import join
from sys import version_info as ver
from traceback import format_exc
from tkinter import messagebox

DEBUG_PATH = join(getcwd(), "Startrak.log")


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
		f.write("Startrak log\nversion: 1.2.0\npython {0}.{1}.{2}\n".format(ver.major, ver.micro, ver.minor))
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
