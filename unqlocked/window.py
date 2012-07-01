from unqlocked import log, WINDOW_ID
import monitor
import xbmcgui

ACTION_PARENT_DIR    = 9
ACTION_PREVIOUS_MENU = 10
ACTION_NAV_BACK      = 92

WINDOW_HOME = xbmcgui.Window(10000)

PROPERTY_ACTIVE = 'Unqlocked.%i.Highlight'
PROPERTY_INACTIVE = 'Unqlocked.%i.Background'

class UnqlockedWindow(xbmcgui.WindowXMLDialog):
	def setLayout(self, layout):
		self.layout = layout
	
	def onInit(self):
		self.monitor = monitor.ExitMonitor(self.exit)
	
	def drawBackground(self):
		for row in range(self.layout.height):
			for col in range(self.layout.width):
				index = row * self.layout.width + col
				WINDOW_HOME.setProperty(PROPERTY_INACTIVE % index, self.layout.matrix[row][col])
	
	def onAction(self, action):
		actionID = action.getId()
		if (actionID in (ACTION_PREVIOUS_MENU, ACTION_NAV_BACK, ACTION_PARENT_DIR)):
			self.close()
	
	def exit(self):
		self.close()
	
	def drawMatrix(self, truthMatrix):
		for i in range(self.layout.height * self.layout.width):
			WINDOW_HOME.clearProperty(PROPERTY_ACTIVE % i)
		for row in range(self.layout.height):
			for col in range(self.layout.width):
				if truthMatrix[row][col]:
					index = row * self.layout.width + col
					WINDOW_HOME.setProperty(PROPERTY_ACTIVE % index, self.layout.matrix[row][col])
