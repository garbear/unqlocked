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

from unqlocked import log, WINDOW_ID, Time
import unqlocked.controller

import os, sys
import xbmc
import xbmcaddon
import elementtree.ElementTree as ElementTree

class Config:
	def __init__(self):
		self.scriptId  = "script.unqlocked"
		self.addon     = xbmcaddon.Addon(self.scriptId)
		self.addonName = self.addon.getAddonInfo('name')
		self.cwd       = self.addon.getAddonInfo('path')
		self.author    = self.addon.getAddonInfo('author')
		self.version   = self.addon.getAddonInfo('version')
		self.language  = self.addon.getLocalizedString
		self.dataDir   = "special://profile/addon_data/%s/" % self.scriptId
		# Workaround: open() doesn't translate path correctly on some versions
		self.dataDir   = xbmc.translatePath(self.dataDir)
		self.layoutDir = xbmc.translatePath(os.path.join(self.cwd, 'layouts'))
		self.layout    = Layout(os.path.join(self.layoutDir, self.addon.getSetting('layout') + '.xml'))
		self.themeDir  = xbmc.translatePath(os.path.join(self.cwd, 'themes'))
		self.theme     = Theme(os.path.join(self.themeDir, self.addon.getSetting('theme') + '.xml'))

class Layout:
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
			key = unqlocked.controller.Time(time.attrib['id'])
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

config = Config()

if (__name__ == "__main__"):
	controller = unqlocked.controller.Master(config)
	controller.spin()
