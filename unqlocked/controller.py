import gui, monitor, statemachine, solver, window
from unqlocked import log, Time, WINDOW_ID

import os
import shutil # for copyfile()
import elementtree.ElementTree as ElementTree
import xbmc, xbmcgui

class Master:
	def __init__(self, config):
		# Test to see if the window is already open
		if xbmc.getCondVisibility('Window.IsVisible(%s)' % WINDOW_ID):
			log('Bailing out (window already exists?)')
			sys.exit()
		
		# Generate and pretty-print the GUI XML
		windowGUI = gui.Window(config.layout, config.theme)
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
		# TODO: Allow layout to specify background images
		images = ['unqlocked-1px-white.png']
		for image in images:
			imgPath = os.path.join(config.themeDir, 'images', image)
			newPath = os.path.join(mediaDir, image)
			if not os.path.exists(newPath):
				shutil.copyfile(imgPath, newPath)
				log('Wrote ' + newPath)
		
		# Now create the GUI window
		self.window = window.UnqlockedWindow('unqlocked.xml', config.profile, 'Default')
		self.window.setLayout(config.layout)
		self.window.drawBackground()
		
		# Create the threads
		self.qlockThread = statemachine.QlockThread(self.window, config.layout)
		#self.spriteThread = statemachine.SpriteThread(self.window, config) # not implemented yet
	
	def spin(self):
		self.qlockThread.start()
		#self.spriteThread.start()
		self.window.doModal()
		self.qlockThread.stop()
		#self.spriteThread.stop()
