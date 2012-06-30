import gui, monitor, solver, window
from unqlocked import log, WINDOW_ID
import os
import elementtree.ElementTree as ElementTree
import xbmc, xbmcgui

class Layout:
	def __init__(self, config):
		dir = config.layoutDir
		file = config.addon.getSetting('layout') + '.xml'
		path = os.path.join(dir, file)
		root = ElementTree.parse(path).getroot()

class Theme:
	'''A theme has several elements that can be accessed through this class:
	* self.background - The background color
	* self.active     - The color of enabled tiles
	* self.inactive   - The color of disabled tiles
	'''
	def __init__(self, config):
		dir = config.themeDir
		file = config.addon.getSetting('theme') + '.xml'
		path = os.path.join(dir, file)
		root = ElementTree.parse(path).getroot()
		self.background = root.find('background').text
		self.active = root.find('active').text
		self.inactive = root.find('inactive').text





class Master:
	def __init__(self, config):
		# Test to see if the window is already open
		if xbmc.getCondVisibility("Window.IsVisible(%s)" % WINDOW_ID):
			log("Bailing out (window already exists?)")
			sys.exit()
		layout = Layout(config)
		theme = Theme(config)
		#self.window = gui.Window(config, layout, theme)
		windowXML = gui.Window(layout, theme).toPrettyXML()
		skinDir = os.path.join(config.dataDir, 'resources', 'skins', 'Default', '720p')
		if not os.path.isdir(skinDir):
			os.makedirs(skinDir)
		ElementTree.ElementTree(windowXML).write(os.path.join(skinDir, 'unqlocked.xml'))
		log('Wrote ' + os.path.join(skinDir, 'unqlocked.xml'))
		self.window = window.UnqlockedWindow('unqlocked.xml', config.dataDir, 'Default')
	
	def spin(self):
		self.window.doModal()
		pass
		# While (!stopCondition):
		#  Get the current time
		#  Pass the current time to the matrix solver
		#  Pass the matrix solution to the matrix gui
		#  Pass current time to the sprite gui
		#  Have the window gui update the screen
		#self.window.show() # After forking a thread for background updates