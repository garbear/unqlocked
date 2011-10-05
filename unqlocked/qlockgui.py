import xbmcgui

# import log, WINDOW_ID
from unqlocked import log, WINDOW_ID

class QlockGUI(xbmcgui.WindowXMLDialog):
	def onInit(self):
		log("Window Initalized!!!")
