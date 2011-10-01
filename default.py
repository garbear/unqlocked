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
import xbmcaddon, xbmc
import datetime
import time

#import xbmc # for windowxml
import xbmcgui # for windowxml

#__title__ = "Pandora"
#__script_id__ = "script.xbmc.pandora"
#__settings__ = xbmcaddon.Addon(id=__script_id__)
#__version__ = "1.2.5-git"

#__scriptname__ = "Qlock"
#__author__     = "Amet"
#__settings__   = xbmcaddon.Addon(id='script.qlock')
#__language__   = __settings__.getLocalizedString
#__cwd__        = __settings__.getAddonInfo('path')
#__layoutDir__ = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'layout' ) )

__title__      = "UnQlocked" # Pandora
__scriptname__ = "UnQlocked" # Qlock
__script_id__  = "script.unqlocked" #Pandora
__author__     = "Garrett a.k.a. Garbear" # Qlock
__settings__   = xbmcaddon.Addon(id=__script_id__)
__language__   = __settings__.getLocalizedString # Qlock
__version__    = '1.0' # Pandora
__cwd__        = __settings__.getAddonInfo('path')
__layoutDir__  = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'layout' ) ) # Qlock

if xbmc.getLanguage() in (os.listdir(__layoutDir__)):
	layout = xbmc.getLanguage()
else:
	layout = "English"   

__layoutFile__ = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'layout', layout, "default.xml" ) )         
__selfRun__    = 'XBMC.AlarmClock(%s,%s,%i,True)' % (__scriptname__, 'XBMC.RunScript(script.qlock,-update)', 4 )

class UnQlocked:
	def __init__( self ):
		i = 0
		return
	
	def main( self ):
		gui = UnQlockedGUI('script-unqlocked.xml', __cwd__, 'Default')
		gui.doModal()

class UnQlockedGUI(xbmcgui.WindowXMLDialog):
	def onInit(self):
		print "UNQLOCKED: Window Initalized!!!"

if ( __name__ == "__main__" ):
	unqlocked = UnQlocked()
	unqlocked.main()
