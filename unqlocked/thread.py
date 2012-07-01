from unqlocked import log, WINDOW_ID

import xbmc
import threading

class StateMachine(threading.Thread):
	def __init__(self, delay):
		super(StateMachine, self).__init__()
		self._stop = False
		self.waitCondition = threading.Condition()
		self.delay = delay
		# When we first start the thread, the window might not be active yet.
		# Keep track of whether we sight the window; if it subsequently falls
		# off the map, we know we should exit
		self.windowSighted = False
	
	def run(self):
		log('StateMachine starting')
		self.waitCondition.acquire()
		while not self.shouldStop():
			# Allow the subclass to update the GUI
			log('StateMachine stepping')
			self.step()
			# Calculate when the next step should be
			self.waitCondition.wait(self.delay)
		#except:
		#	log('Exception thrown in StateMachine thread')
		#	self.stop()
		self.waitCondition.release()
		self.cleanup()
		log('StateMachine exiting')
	
	def shouldStop(self):
		'''Two conditions result in stopping: a call to stop(), or the window
		not being visible after once being visible.'''
		visible = xbmc.getCondVisibility('Window.IsVisible(%s)' % WINDOW_ID)
		if self.windowSighted and not visible:
			return True
		elif visible:
			self.windowSighted = True
		return self._stop
	
	def stop(self):
		self.waitCondition.acquire()
		self._stop = True
		self.waitCondition.notifyAll()
		self.waitCondition.release()


class QlockThread(StateMachine):
	def __init__(self, window, config):
		super(QlockThread, self).__init__(self.calcDelay(config))
		self.window = window
		self.config = config
		self.test = False
	
	def step(self):
		# Initialize an empty matrix
		truthMatrix = [[False for col in range(self.config.layout.width)] for row in range(self.config.layout.height)]
		self.test = not self.test
		log('Toggling first letter: ' + str(self.test))
		truthMatrix[0][0] = self.test
		self.window.drawMatrix(truthMatrix)
	
	def cleanup(self):
		# clear window properties
		pass
	
	def calcDelay(self, config):
		return 1.0

class SpriteThread(StateMachine):
	def __init__(self, window, config):
		super(SpriteThread, self).__init__(self.calcDelay(config))
		self.window = window
		self.config = config
	
	def step(self):
		pass
	
	def cleanup(self):
		# clear window properties
		pass
	
	def calcDelay(self, config):
		return 5.0
