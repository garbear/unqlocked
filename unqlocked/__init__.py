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

# Import these submodules, functions and variables as part of the package
#__all__ = ["qlockgui", "WINDOW_ID", "log"]

# Shared functions and variables
import xbmc

WINDOW_ID = 3000

def log(msg):
	xbmc.log('UNQLOCKED: ' + msg, level=xbmc.LOGDEBUG)

def createTruthMatrix(height, width):
	return [[False for col in range(width)] for row in range(height)]

def gcd(a, b):
	return a if not b else gcd(b, a % b)


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
		self.useSeconds = (self.seconds != -1)
		self.seconds = 0 # Don't really store -1 for seconds
		self.duration = None # By default, a time is just an instant
	
	def __hash__(self):
		#return hash((self.hours, self.minutes, self.seconds))
		return self.toSeconds()
	
	def __eq__(self, other):
		return (self.hours, self.minutes, self.seconds) == (other.hours, other.minutes, other.seconds)
	
	def __str__(self):
		if self.useSeconds:
			return '%d:%02d:%02d' % (self.hours, self.minutes, self.seconds)
		else:
			return '%d:%02d' % (self.hours, self.minutes)
	
	def copy(self):
		temp = Time(self.hours, self.minutes, self.seconds)
		temp.useSeconds = self.useSeconds
		temp.duration = self.duration
		return temp
	
	def toSeconds(self):
		if self.useSeconds:
			return self.hours * 60 * 60 + self.minutes * 60 + self.seconds
		else:
			return self.hours * 60 * 60 + self.minutes * 60
	
	def end(self):
		return self.toSeconds() + (self.duration.toSeconds() if self.duration else 0)
	
	@staticmethod
	def fromSeconds(seconds):
		return Time(seconds / (60 * 60), (seconds / 60) % 60, seconds % 60)
