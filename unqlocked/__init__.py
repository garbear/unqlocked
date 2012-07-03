# Import these submodules, functions and variables as part of the package
#__all__ = ["qlockgui", "WINDOW_ID", "log"]

# Shared functions and variables
import xbmc

WINDOW_ID = 3000

def log(msg):
	xbmc.log("UNQLOCKED: " + str(msg), level=xbmc.LOGDEBUG)

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
