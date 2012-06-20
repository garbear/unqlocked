from unqlocked import log, WINDOW_ID

import xbmc, xbmcgui



class MatrixGUI:
	def __init__(self, solution, settings):
		pass

class SpritesGUI:
	def __init__(self, settings):
		pass


class Window:
	class UnqlockedWindow(xbmcgui.WindowXMLDialog):
		class ExitMonitor(xbmc.Monitor):
			def __init__(self, exit_callback):
				self.exit_callback = exit_callback
			
			def onScreensaverDeactivated(self):
				log('Invoking exit_callback')
				self.exit_callback()
		
		# Class UnqlockedWindow
		def onInit(self):
			log('Window Initalized!')
			self.monitor = self.ExitMonitor(self.exit)
		
		def onAction(self, actionid):
			# This is just for non-screensaver run mode, ex. Addon-Program
			log('Action received: exiting')
			self.close()
		
		def exit(self):
			log('Exit requested')
			self.close()
	
	# Class WindowGUI
	def __init__(self, layout, settings):
		self.window = UnqlockedWindow('script-unqlocked.xml', settings.config.cwd, 'Default')
	
	def show(self):
		self.window.doModal()

