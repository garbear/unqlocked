from unqlocked import log, WINDOW_ID

import xbmc
import threading

class StateMachine(threading.Thread):
	def __init__(self, duration):
		super(StateMachine, self).__init__()
		self._stop = False
		self.waitCondition = threading.Condition()
		self.duration = duration
	
	def run(self):
		self.waitCondition.acquire()
		while not self.shouldStop():
			# Allow the subclass to update the GUI
			self.step()
			# Calculate when the next step should be
			self.waitCondition.wait(self.duration)
		#except:
		#	log('Exception thrown in StateMachine thread')
		#	self.stop()
		self.waitCondition.release()
		self.cleanup()
	
	def shouldStop(self):
		return self._stop or not xbmc.getCondVisibility('Window.IsVisible(%s)' % WINDOW_ID)
	
	def stop(self):
		self._stop = True
		self.waitCondition.acquire()
		self.waitCondition.notifyAll()
		self.waitCondition.release()


class QlockThread(StateMachine):
	def __init__(self, window, config):
		super(QlockThread, self).__init__(1.0)
		self.window = window
		self.config = config
	
	def step(self):
		#self.window
		pass
	
	def cleanup(self):
		# clear window properties
		pass

class SpriteThread(StateMachine):
	def __init__(self, window, config):
		super(SpriteThread, self).__init__(5.0)
		self.window = window
		self.config = config
	
	def step(self):
		pass
	
	def cleanup(self):
		# clear window properties
		pass
