import gui, monitor, statemachine, solver, window
from unqlocked import log, WINDOW_ID

import os
import elementtree.ElementTree as ElementTree
import xbmc, xbmcgui

class Time(object):
	def __init__(self, hours, minutes = 0, seconds = -1):
		if isinstance(hours, int):
			self.hours = hours
			self.minutes = minutes
			self.seconds = seconds
		elif isinstance(hours, str):
			parts = hours.split(':')
			self.hours   = int(parts[0]) if len(parts) >= 1 else 0
			self.minutes = int(parts[1]) if len(parts) >= 2 else 0
			self.seconds = int(parts[2]) if len(parts) >= 3 else -1
		self.secondsUsed = (self.seconds != -1)
		# self.duration
		# Optionally, add a duration post-instantation
		# A duration is simply another Time object
	
	def __hash__(self):
		#return hash((self.hours, self.minutes, self.seconds))
		return self.toSeconds()
	
	def __eq__(self, other):
		return (self.hours, self.minutes, self.seconds) == (other.hours, other.minutes, other.seconds)
	
	def __str__(self):
		if self.secondsUsed:
			return '%d:%02d:%02d' % (self.hours, self.minutes, self.seconds)
		else:
			return '%d:%02d' % (self.hours, self.minutes)
	
	def toSeconds(self):
		if self.secondsUsed:
			return self.hours * 60 * 60 + self.minutes * 60 + self.seconds
		else:
			return self.hours * 60 * 60 + self.minutes * 60

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
		skinDir = os.path.join(config.dataDir, 'resources', 'skins', 'Default', '720p')
		if not os.path.isdir(skinDir):
			os.makedirs(skinDir)
		ElementTree.ElementTree(windowXML).write(os.path.join(skinDir, 'unqlocked.xml'))
		log('Wrote ' + os.path.join(skinDir, 'unqlocked.xml'))
		
		# Now create the GUI window
		self.window = window.UnqlockedWindow('unqlocked.xml', config.dataDir, 'Default')
		self.window.setLayout(config.layout)
		self.window.drawBackground()
		
		# Create the threads
		self.qlockThread = statemachine.QlockThread(self.window, config.layout)
		#self.spriteThread = statemachine.SpriteThread(self.window, config)
	
	def spin(self):
		self.qlockThread.start()
		#self.spriteThread.start()
		self.window.doModal()
		self.qlockThread.stop()
		#self.spriteThread.stop()
