from unqlocked import log, Time

import xbmc
import xbmcaddon

import elementtree.ElementTree as ElementTree
import os, sys


class Config:
	def __init__(self):
		self.scriptId  = 'script.unqlocked'
		self.addon     = xbmcaddon.Addon(self.scriptId)
		self.addonName = self.addon.getAddonInfo('name')
		self.cwd       = self.addon.getAddonInfo('path')
		self.author    = self.addon.getAddonInfo('author')
		self.version   = self.addon.getAddonInfo('version')
		self.profile   = xbmc.translatePath(self.addon.getAddonInfo('profile'))
		#self.language  = self.addon.getLocalizedString
		self.layoutDir = os.path.join(self.cwd, 'layouts')
		self.layout    = Layout(self.getLayoutFile(self.layoutDir))
		self.themeDir  = os.path.join(self.cwd, 'themes')
		self.theme     = Theme(self.getThemeFile(self.themeDir))
	
	def getLayoutFile(self, layoutDir):
		layout = self.addon.getSetting('layout')
		if layout == 'Default':
			# Choose the best layout for the language
			map = {
				'dutch':   'Dutch 10x11',
				'english': 'English 10x11',
				'french':  'French 10x11',
				'german':  'German 10x11',
				'italian': 'Italian 10x11',
				'spanish': 'Spanish 10x11'}
			language = xbmc.getLanguage()
			if language in map:
				layout = map[language]
			else:
				layout = map['english']
			self.addon.setSetting('layout', layout)
		# .xml was masked in the settings
		return os.path.join(layoutDir, layout + '.xml')
	
	def getThemeFile(self, themeDir):
		theme = self.addon.getSetting('theme')
		if theme == 'Default':
			# Choose the best theme for the current skin
			map = {
				'skin.confluence': 'Black Ice Tea'}
			skin = xbmc.getSkinDir()
			if skin in map:
				theme = map[skin]
			else:
				theme = map['skin.confluence']
			self.addon.setSetting('theme', theme)
		# .xml was masked in the settings
		return os.path.join(themeDir, theme + '.xml')


class Layout:
	'''Load an XML layout file into several parameters:
	* self.matrix - The 2-dimensional array of background characters
	* self.height - equal to len(self.matrix)
	* self.width - equal to len(self.matrix[0])
	* self.times - dictionary of time strings
	* self.use24 - flag for a 24-hour clock
	* self.strings - dictionary for translating numbers into strings
	'''
	def __init__(self, file):
		log('Using layout: ' + os.path.basename(file))
		try:
			root = ElementTree.parse(file).getroot()
		except:
			log('Error parsing layout file!')
			raise # Let the user see the error
		try:
			background = root.find('background')
			self.height = int(background.attrib['height'])
			self.width = int(background.attrib['width'])
		except:
			log('Error: <background> tag missing/incorrect!')
			sys.exit()
		
		self.matrix = []
		entities = [char.strip().upper() for char in background.text.split(',')]
		if (self.height * self.width > len(entities)):
			log('Error: Too many characters in background (expecting %d, found %d)' % \
				(self.height * self.width, len(entities)))
			sys.exit()
		elif (self.height * self.width < len(entities)):
			log('Error: Too few characters in background (expecting %d, found %d)' % \
				(self.height * self.width, len(entities)))
			sys.exit()
		for i in range(self.height):
			self.matrix.append(entities[i * self.width : (i + 1) * self.width])
		
		timesNode = root.find('times')
		if timesNode == None:
			log('Error: <times> node not found!')
			sys.exit()
		if 'use24' in timesNode.attrib and timesNode.attrib['use24'] == 'true':
			self.use24 = True
		else:
			self.use24 = False
		
		self.times = {}
		for time in timesNode.findall('time'):
			if 'id' not in time.attrib:
				log('Warning: found <time> tag with no "id" attribute')
				continue
			key = Time(time.attrib['id'])
			# If set, store the duration with the key
			if 'duration' in time.attrib:
				key.duration = Time(time.attrib['duration'])
			self.times[key] = time.text.lower()
		if len(self.times) == 0:
			log('Error: no <time> tags found!')
			sys.exit()
		
		self.strings = {}
		stringsNode = root.find('strings')
		if stringsNode == None:
			log('Error: <strings> node not found!')
			sys.exit()
		for string in stringsNode.findall('string'):
			if 'id' not in string.attrib:
				log('Warning: found <string> tag with no "id" attribute')
				continue
			self.strings[int(string.attrib['id'])] = string.text.lower()


class Theme:
	'''A theme has several elements that can be accessed through this class:
	* self.background - The background color
	* self.active     - The color of enabled tiles
	* self.inactive   - The color of disabled tiles
	'''
	def __init__(self, file):
		log('Using theme: ' + os.path.basename(file))
		try:
			root = ElementTree.parse(file).getroot()
		except:
			log('Error parsing theme file!')
			raise # Let the user see the error
		try:
			self.background = root.find('background').text
			self.active = root.find('active').text
			self.inactive = root.find('inactive').text
		except:
			log('Error parsing theme file!')
			sys.exit()
