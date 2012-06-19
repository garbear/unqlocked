import gui
import solver
from unqlocked import log, WINDOW_ID

import xbmc, xbmcgui

if False:
	class Screensaver(xbmcgui.WindowXMLDialog):
		class ExitMonitor(xbmc.Monitor):
			def __init__(self, exit_callback):
				self.exit_callback = exit_callback
			
			def onScreensaverDeactivated(self):
				print '3 ExitMonitor: sending exit_callback'
				self.exit_callback()
		
		def onInit(self):
			print '2 Screensaver: onInit'
			self.monitor = self.ExitMonitor(self.exit)
		
		def onAction(self, actionid):
			# This is just for non-screensaver run mode, ex. Addon-Program
			print '3 Action received: exiting'
			self.close()
		
		def exit(self):
			print '4 Screensaver: Exit requested'
			self.close()



class Settings:
	def __init__(self, config):
		self.config = config

class Master:
	def __init__(self, config):
		# Test to see if the window is already open
		if xbmc.getCondVisibility("Window.IsVisible(%s)" % WINDOW_ID):
			log("Bailing out (window already exists?)")
			sys.exit()
		
		# Load settings
		settings = Settings(config)
		# Pass the settings to the matrix solver
		matrixSolution = solver.MatrixSolver(settings)
		# Pass the matrix solution and settings to the matrix gui
		matrixGUI = gui.MatrixGUI(matrixSolution, settings)
		# Pass the settings to the sprite gui
		spriteGUI = gui.SpritesGUI(settings)
		# Pass the matrix gui, sprite gui and settings to the window gui
		# The window gui generates the XML window
		self.window = gui.WindowGUI(matrixGUI, spriteGUI, settings)
	
	def spin(self):
		# While (!stopCondition):
		#  Get the current time
		#  Pass the current time to the matrix solver
		#  Pass the matrix solution to the matrix gui
		#  Pass current time to the sprite gui
		#  Have the window gui update the screen
		self.window.show()
	pass