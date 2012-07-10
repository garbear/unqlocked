# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with XBMC; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html

from unqlocked import log, createTruthMatrix, WINDOW_ID
import config
import gui
import monitor

import os
import xbmcgui

ACTION_PARENT_DIR    = 9
ACTION_PREVIOUS_MENU = 10
ACTION_NAV_BACK      = 92

WINDOW_HOME = xbmcgui.Window(10000)

PROPERTY_ACTIVE = 'Unqlocked.%i.Highlight'
PROPERTY_INACTIVE = 'Unqlocked.%i.Background'


class UnqlockedWindow(xbmcgui.WindowXMLDialog):
	def setConfig(self, config):
		self.config = config
	
	def setLayoutCallback(self, callback):
		self.layoutCallback = callback
	
	def setDemoCallback(self, callback):
		self.demoCallback = callback
	
	def onInit(self):
		self.monitor = monitor.ExitMonitor(self.exit, self.config.ssMode)
		#ctrl = self.getControl(4848)
	
	def drawBackground(self):
		for row in range(self.config.layout.height):
			for col in range(self.config.layout.width):
				index = row * self.config.layout.width + col
				WINDOW_HOME.setProperty(PROPERTY_INACTIVE % index, self.config.layout.matrix[row][col])
		# Start with a state of uniform False
		self.state = createTruthMatrix(self.config.layout.height, self.config.layout.width)
	
	def onAction(self, action):
		actionID = action.getId()
		if (actionID in (ACTION_PREVIOUS_MENU, ACTION_NAV_BACK, ACTION_PARENT_DIR)):
			self.exit()
		if self.config.ssMode:
			return
		
		buttonCode = action.getButtonCode()
		if (buttonCode & 0xFF == ord('L')): # L was pressed
			self.layoutCallback()
		if (buttonCode & 0xFF == ord('D')): # D was pressed
			self.demoCallback()
		if (buttonCode & 0xFF == ord('T')): # T was pressed
			#self.changeTheme() # Disabled until XBMC supports control panel color changes
			pass
	
	def exit(self):
		self.close()
	
	def drawMatrix(self, truthMatrix):
		for row in range(self.config.layout.height):
			for col in range(self.config.layout.width):
				index = row * self.config.layout.width + col
				if truthMatrix[row][col] and not self.state[row][col]:
					WINDOW_HOME.setProperty(PROPERTY_ACTIVE % index, self.config.layout.matrix[row][col])
				if not truthMatrix[row][col] and self.state[row][col]:
					WINDOW_HOME.clearProperty(PROPERTY_ACTIVE % index)
		self.state = truthMatrix
	
	def drawSprites(self, count):
		pass
	
	def changeTheme(self):
		self.config.loadNextTheme()
		background = self.getControl(gui.CONTROL_BACKGROUND)
		background.setColorDiffuse('0x' + self.config.theme.background)
		
		# Always complain about XBMC's missing features
		log('Unable to change text color: Not implemented in XBMC!')
		
		image = self.getControl(gui.CONTROL_IMAGE)
		if self.config.theme.image:
			image.setImage(os.path.join(self.config.themeDir, self.config.theme.image))
			image.setWidth(self.config.theme.imageWidth)
			image.setHeight(self.config.theme.imageHeight)
			image.setVisible(True)
		else:
			image.setVisible(False)
