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

from unqlocked import log, Time

import elementtree.ElementTree as ElementTree
import os
import sys
import xbmc
import xbmcaddon


class Config:
	def __init__(self):
		self.scriptId   = 'script.unqlocked'
		self.addon      = xbmcaddon.Addon(self.scriptId)
		self.addonName  = self.addon.getAddonInfo('name')
		self.cwd        = self.addon.getAddonInfo('path')
		self.author     = self.addon.getAddonInfo('author')
		self.version    = self.addon.getAddonInfo('version')
		self.profile    = xbmc.translatePath(self.addon.getAddonInfo('profile'))
		self.ssMode     = xbmc.getCondVisibility('System.ScreenSaverActive')
		#self.language   = self.addon.getLocalizedString
		self.layoutDir  = os.path.join(self.cwd, 'layouts')
		self.layoutName = self.getLayoutFile(self.layoutDir)
		self.layout     = Layout(os.path.join(self.layoutDir, self.layoutName))
		self.themeDir   = os.path.join(self.cwd, 'themes')
		self.themeName  = self.getThemeFile(self.themeDir)
		self.theme      = Theme(os.path.join(self.themeDir, self.themeName))
	
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
		return layout + '.xml'
	
	def getThemeFile(self, themeDir):
		theme = self.addon.getSetting('theme')
		if theme == 'Default':
			# Choose the best theme for the current skin
			map = {
				'skin.alaska.revisited': 'Vanilla Sugar',
				'skin.confluence':       'Black Ice Tea',
				'skin.xeebo':            'Gritty Guacamole'}
			skin = xbmc.getSkinDir()
			if skin in map:
				theme = map[skin]
			else:
				theme = map['skin.confluence']
			self.addon.setSetting('theme', theme)
		# .xml was masked in the settings
		return theme + '.xml'
	
	def loadNextTheme(self):
		themes = [theme for theme in os.listdir(self.themeDir) if theme[-4:] == '.xml']
		count = len(themes)
		for i in range(count):
			if themes[i] == self.themeName:
				self.themeName = themes[(i + 1) % count]
				self.theme = Theme(os.path.join(self.themeDir, self.themeName))
				break
	
	def loadNextLayout(self):
		layouts = [layout for layout in os.listdir(self.layoutDir) if layout[-4:] == '.xml']
		count = len(layouts)
		for i in range(count):
			if layouts[i] == self.layoutName:
				self.layoutName = layouts[(i + 1) % count]
				self.layout = Layout(os.path.join(self.layoutDir, self.layoutName))
				break


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
	* self.background  - The background color
	* self.active      - The color of enabled tiles
	* self.inactive    - The color of disabled tiles
	* self.image       - The filename of a background image, or None of omitted
	* self.imageWidth  - Image width, or 1280 if image is None
	* self.imageHeight - Image height, or 720 if image is None
	'''
	def __init__(self, file):
		log('Using theme: ' + os.path.basename(file))
		try:
			root = ElementTree.parse(file).getroot()
		except:
			log('Error parsing theme file!')
			raise # Let the user see the error
		try:
			self.active = root.find('active').text
			self.inactive = root.find('inactive').text
			imgNode = root.find('image')
			if imgNode != None:
				self.image = imgNode.text
				# Width and height default to fullscreen if unspecified
				self.imageWidth = int(imgNode.attrib['width']) if 'width' in imgNode.attrib else 1280
				self.imageHeight = int(imgNode.attrib['height']) if 'height' in imgNode.attrib else 720
				# If an image was found, background is optional
				if root.find('background') != None:
					self.background = root.find('background').text
				else:
					self.background = '00000000' # fully transparent
			else:
				# If an image wasn't found, background is mandatory
				self.background = root.find('background').text
				self.image = None
				self.imageWidth = 1280
				self.imageHeight = 720
			# In SS mode, the background is black so ignore the alpha channel
			if xbmc.getCondVisibility('System.ScreenSaverActive'):# and len(self.background) == 8:
				isHex = lambda x: (ord('0') <= ord(x) and ord(x) <= ord('9')) or \
				                  (ord('A') <= ord(x) and ord(x) <= ord('F')) or \
				                  (ord('a') <= ord(x) and ord(x) <= ord('f'))
				# Proceed if all chars are hex
				if [isHex(c) for c in self.background].count(False) == 0:
					self.background = 'ff' + self.background[2:]
					log('NewBackground: ' + self.background)
		except:
			log('Error parsing theme file!')
			sys.exit()
