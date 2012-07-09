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

from unqlocked import log, Time, WINDOW_ID
import gui, statemachine, window

import elementtree.ElementTree as ElementTree
import os
import shutil # for copyfile()
import xbmc


class Master:
	def __init__(self, config):
		# Test to see if the window is already open
		if xbmc.getCondVisibility('Window.IsVisible(%s)' % WINDOW_ID):
			log('Bailing out (window already exists?)')
			sys.exit()
		
		self.ssMode = config.ssMode
		
		# Generate and pretty-print the GUI XML
		windowGUI = gui.Window(config.layout, config.theme, config.ssMode)
		windowXML = windowGUI.toXMLPrettyPlease()
		
		# Create a mimic directory that we can write to
		skinDir = os.path.join(config.profile, 'resources', 'skins', 'Default', '720p')
		if not os.path.isdir(skinDir):
			os.makedirs(skinDir)
		ElementTree.ElementTree(windowXML).write(os.path.join(skinDir, 'unqlocked.xml'))
		log('Wrote ' + os.path.join(skinDir, 'unqlocked.xml'))
		
		# Copy our images over to the new folder
		mediaDir = os.path.join(config.profile, 'resources', 'skins', 'Default', 'media')
		if not os.path.isdir(mediaDir):
			os.makedirs(mediaDir)
		# Allow layout to specify background images
		images = ['unqlocked-1px-white.png']
		if config.theme.image:
			images.append(config.theme.image)
		for image in images:
			imgPath = os.path.join(config.themeDir, image)
			newPath = os.path.join(mediaDir, image)
			if not os.path.exists(newPath):
				shutil.copyfile(imgPath, newPath)
				log('Wrote ' + newPath)
		
		# Now create the GUI window
		self.window = window.UnqlockedWindow('unqlocked.xml', config.profile, 'Default')
		self.window.setConfig(config)
		self.window.drawBackground()
		
		# Create the threads
		self.qlockThread = statemachine.QlockThread(self.window, config.layout)
		#self.spriteThread = statemachine.SpriteThread(self.window, config) # not implemented yet
	
	def spin(self):
		self.qlockThread.start()
		#self.spriteThread.start()
		
		# Give the solvers time to do their work, so that when the window fades
		# in, the solution will already have been highlighted.
		# I noticed problems as high as 10ms, so use 25ms.
		if not self.ssMode:
			xbmc.sleep(25)
		
		self.window.doModal()
		self.qlockThread.stop()
		#self.spriteThread.stop()
