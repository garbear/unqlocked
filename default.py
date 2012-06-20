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

import os, sys
import xbmc
import xbmcaddon
from elementtree.ElementTree import ElementTree

from unqlocked import log, WINDOW_ID

import unqlocked.controller

class Config:
	def __init__(self):
		self.scriptId  = "script.unqlocked"
		self.addon     = xbmcaddon.Addon(self.scriptId)
		self.addonName = self.addon.getAddonInfo('name')
		self.cwd       = self.addon.getAddonInfo('path')
		self.author    = self.addon.getAddonInfo('author')
		self.version   = self.addon.getAddonInfo('version')
		self.language  = self.addon.getLocalizedString
		self.layoutDir = xbmc.translatePath(os.path.join(self.cwd, 'layouts'))
		self.themeDir  = xbmc.translatePath(os.path.join(self.cwd, 'themes'))
		self.dataDir   = os.path.join("special://profile/addon_data/%s/" % self.scriptId)
		# Workaround: open() doesn't translate path correctly on some versions
		self.dataDir = xbmc.translatePath(self.dataDir)

config = Config()

if (__name__ == "__main__"):
	controller = unqlocked.controller.Master(config)
	controller.spin()


# Controller internally keeps track of update interval (timeouts)
# Every timeout, asks the solver to generate the next state
# Sends the state to the view so that the GUI can be updated
# Controller watches for exit events and/or keyboard events

