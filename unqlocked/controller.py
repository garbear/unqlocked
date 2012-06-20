import os
import gui
import solver
import elementtree.ElementTree as ElementTree
from unqlocked import log, WINDOW_ID
import xbmc, xbmcgui

class Layout:
	def __init__(self, config):
		dir = config.layoutDir
		file = config.addon.getSetting('layout') + '.xml'
		path = os.path.join(dir, file)
		root = ElementTree.parse(path).getroot()

class Theme:
	def __init__(self, config):
		dir = config.themeDir
		file = config.addon.getSetting('theme') + '.xml'
		path = os.path.join(dir, file)
		root = ElementTree.parse(path).getroot()
		# self.background
		self.background = root.find('background').text
		# self.active
		self.active = root.find('active').text
		# self.inactive
		self.inactive = root.find('inactive').text



# http://stackoverflow.com/questions/749796/pretty-printing-xml-in-python
def indent(elem, level=0):
	i = "\n" + level*"  "
	if len(elem):
		if not elem.text or not elem.text.strip():
			elem.text = i + "  "
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
		for elem in elem:
			indent(elem, level + 1)
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
	else:
		if level and (not elem.tail or not elem.tail.strip()):
			elem.tail = i


class Master:
	def __init__(self, config):
		# Test to see if the window is already open
		if xbmc.getCondVisibility("Window.IsVisible(%s)" % WINDOW_ID):
			log("Bailing out (window already exists?)")
			sys.exit()
		layout = Layout(config)
		theme = Theme(config)
		#self.window = gui.Window(config, layout, theme)
		window = gui.Window(layout, theme)
		windowXML = window.toXML()
		indent(windowXML)
		ElementTree.ElementTree(windowXML).write(os.path.join(config.cwd, 'test.xml'))
	
	def spin(self):
		# While (!stopCondition):
		#  Get the current time
		#  Pass the current time to the matrix solver
		#  Pass the matrix solution to the matrix gui
		#  Pass current time to the sprite gui
		#  Have the window gui update the screen
		#self.window.show() # After forking a thread for background updates
		pass