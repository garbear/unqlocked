from unqlocked import log, WINDOW_ID

import xbmc, xbmcgui

class QlockGUI(xbmcgui.WindowXMLDialog):
	def onInit(self):
		log("Window Initalized!")


class WindowGUI:
	def __init__(self, x, y, settings):
		self.window = QlockGUI('script-unqlocked.xml', settings.config.cwd, 'Default')
	
	def show(self):
		self.window.doModal()


class SpritesGUI:
	def __init__(self, settings):
		pass


class MatrixGUI:
	def __init__(self, solution, settings):
		pass
