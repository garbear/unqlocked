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

import xbmc
import xbmcaddon
import sys

__script_id__ = "script.unqlocked"
__addon__     = xbmcaddon.Addon(id=__script_id__)
__addonname__ = __addon__.getAddonInfo('name')
__cwd__       = __addon__.getAddonInfo('path')
__author__    = __addon__.getAddonInfo('author')
__version__   = __addon__.getAddonInfo('version')
__language__  = __addon__.getLocalizedString
__layoutDir__ = xbmc.translatePath(os.path.join(__cwd__, 'layouts'))

from unqlocked import log, WINDOW_ID

if (__name__ == "__main__"):
	# First test to see if the window is already open
	if xbmc.getCondVisibility("Window.IsVisible(%s)" % WINDOW_ID):
		log("bailing out (window already exists?)")
		sys.exit()
	#import unqlocked.qlock as qlock
	#qlock = qlock.Qlock()
	#del qlock
	from unqlocked.qlockgui import QlockGUI
	gui = QlockGUI('script-unqlocked.xml', __cwd__, 'Default')
	gui.doModal()


log("got here!")
# Use only one of the following two lines
#sys.modules.clear()
sys.exit()


#from unqlocked import *
#from unqlocked import log, WINDOW_ID
#from unqlocked.qlockgui import QlockGUI
#import unqlocked.qlock




qlock = qlock.Qlock()
qlock.main()



import os
import xbmcaddon

import datetime
import time

#import xbmc # for windowxml
import xbmcgui # for windowxml

### from script.qlock
if xbmc.getLanguage() in (os.listdir(__layoutDir__)):
	layout = xbmc.getLanguage()
else:
	layout = "English"
__layoutFile__ = xbmc.translatePath(os.path.join(__cwd__, 'resources', 'layout', layout, "default.xml"))


def log(msg):
	xbmc.log(str(msg), level=xbmc.LOGDEBUG)


from qlockgui import QlockGui

try:
	# parse sys.argv for params
	try:
		params = dict(arg.split('=') for arg in sys.argv[1].split('&'))
	except:
		params = dict(sys.argv[1].split('='))
except:
	# no params passed
	params = {}


if params.get("backend", False):
	if xbmc.getInfoLabel("Window(%s).Property(Running)" % WINDOW_ID) != "true":
		xbmcgui.Window(3000).setProperty("Running", "true")
		xbmc.executebuiltin('XBMC.RunScript(%s,param1=%s&param2=%s)' % (os.path.join(__cwd__ , "tvtunes_backend.py"), param1 , param2))


class UnQlocked:
	def __init__( self ):
		i = 0
		return
	
	def main( self ):
		gui = UnQlockedGUI('script-unqlocked.xml', __cwd__, 'Default')
		gui.doModal()
		# clean up

if ( __name__ == "__main__" ):
	unqlocked = UnQlocked()
	unqlocked.main()
