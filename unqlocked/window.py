import monitor
import xbmcgui

ACTION_PARENT_DIR    = 9
ACTION_PREVIOUS_MENU = 10
ACTION_NAV_BACK      = 92

class UnqlockedWindow(xbmcgui.WindowXMLDialog):
	def onInit(self):
		self.monitor = monitor.ExitMonitor(self.exit)
	
	def onAction(self, action):
		actionID = action.getId()
		if (actionID in (ACTION_PREVIOUS_MENU, ACTION_NAV_BACK, ACTION_PARENT_DIR)):
			self.close()
	
	def exit(self):
		self.close()
