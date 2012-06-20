import gui
import solver
from unqlocked import log, WINDOW_ID

import xbmc, xbmcgui


class Master:
	def __init__(self, config):
		# Test to see if the window is already open
		if xbmc.getCondVisibility("Window.IsVisible(%s)" % WINDOW_ID):
			log("Bailing out (window already exists?)")
			sys.exit()
		self.window = gui.Window(config)
		self.solver = solver.Solver(config)
	
	def spin(self):
		# While (!stopCondition):
		#  Get the current time
		#  Pass the current time to the matrix solver
		#  Pass the matrix solution to the matrix gui
		#  Pass current time to the sprite gui
		#  Have the window gui update the screen
		self.window.show() # After forking a thread for background updates
	pass