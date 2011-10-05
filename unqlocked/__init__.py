# Import these submodules, functions and variables as part of the package
#__all__ = ["qlockgui", "WINDOW_ID", "log"]

# Shared functions and variables
import xbmc

WINDOW_ID = 3000

def log(msg):
	xbmc.log("UNQLOCKED: " + str(msg), level=xbmc.LOGDEBUG)
