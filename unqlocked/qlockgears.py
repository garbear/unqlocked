import threading

import xbmc
#Modules XBMC
import xbmc
import xbmcgui
import sys
import xbmcvfs

from traceback import print_exc

def log(msg):
	xbmc.log("UNQLOCKED: " + str(msg), level=xbmc.LOGDEBUG)

class QlockGears( threading.Thread ):
	def __init__( self ):
		threading.Thread.__init__( self )
		self._stop = False
		log( "### starting TvTunes Backend ###" )
	
	def run( self ):
		try:
			while not self._stop:
				if not xbmc.getCondVisibility("Window.IsVisible(3000)"): self.stop() # destroy threading
				time.sleep(1) # seconds
		except:
			print_exc()
			self.stop()
	
	def stop( self ):
		xbmcgui.Window(3000).clearProperty("Running")
		log( "### Stopping TvTunes Backend ###" )
		self._stop = True
