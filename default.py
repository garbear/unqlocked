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

from unqlocked import log, WINDOW_ID
import unqlocked.controller

import os
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

class Time(object):
	def __init__(self, hours, minutes = 0, seconds = 0):
		if isinstance(hours, int):
			self.hours = hours
			self.minutes = minutes
			self.seconds = seconds
		elif isinstance(hours, str):
			parts = hours.split(':')
			self.hours   = int(parts[0]) if len(parts) >= 1 else 0
			self.minutes = int(parts[1]) if len(parts) >= 2 else 0
			self.seconds = int(parts[2]) if len(parts) >= 3 else 0
	
	def __hash__(self):
		return hash((self.hours, self.minutes, self.seconds))
	
	def __eq__(self, other):
		return (self.hours, self.minutes, self.seconds) == (other.hours, other.minutes, other.seconds)
	
	def __str__(self):
		if self.seconds:
			return '%d:%02d:%02d' % (self.hours, self.minutes, self.seconds)
		else:
			return '%d:%02d' % (self.hours, self.minutes)

class Layout:
	def __init__(self, file):
		root = ElementTree.parse(file).getroot()
		background = root.find('background')
		self.height = int(background.attrib['height'])
		self.width = int(background.attrib['width'])
		
		self.matrix = []
		entities = [char.strip() for char in background.text.split(',')]
		for i in range(self.height):
			self.matrix.append(entities[i * self.width : (i + 1) * self.width])
		
		self.times = {}
		for time in root.find('times').findall('time'):
			self.times[Time(time.attrib['id'])] = time.text
		
		self.strings = {}
		for string in root.find('strings').findall('string'):
			self.strings[int(string.attrib['id'])] = string.text

class Theme:
	'''A theme has several elements that can be accessed through this class:
	* self.background - The background color
	* self.active     - The color of enabled tiles
	* self.inactive   - The color of disabled tiles
	'''
	def __init__(self, file):
		root = ElementTree.parse(file).getroot()
		self.background = root.find('background').text
		self.active = root.find('active').text
		self.inactive = root.find('inactive').text


config = Config()

if (__name__ == "__main__"):
	controller = unqlocked.controller.Master(config)
	controller.spin()
