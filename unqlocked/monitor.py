import xbmc

class ExitMonitor(xbmc.Monitor):
	def __init__(self, exit_callback):
		self.exit_callback = exit_callback
	
	def onScreensaverDeactivated(self):
		self.exit_callback()
