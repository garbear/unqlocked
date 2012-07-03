from unqlocked import log, createTruthMatrix, gcd, WINDOW_ID, Time

import solver

import xbmc
import threading
import datetime
#import time
from copy import deepcopy

class StateMachine(threading.Thread):
	'''Representation of a state machine, where the state is defined by
	a reference to an internal (fake) clock or an external (real) clock,
	and the only transition between states occurs as a transition between
	two different times.'''
	def __init__(self, delay):
		super(StateMachine, self).__init__()
		self._stop = False
		self.waitCondition = threading.Condition()
		
		now = datetime.datetime.now()
		seconds = now.hour * 60 * 60 + now.minute * 60 + now.second
		
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
			time = Time(1, 45)
			self.step(time)
			# Calculate when the next step should be
			self.delay = 100.0
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
	def __init__(self, window, layout):
		super(QlockThread, self).__init__(self.calcDelay(layout))
		self.window = window
		# Use a lowercase matrix for comparison
		self.layout = deepcopy(layout)
		# TODO: inline
		for row in range(self.layout.height):
			for col in range(self.layout.width):
				self.layout.matrix[row][col] = self.layout.matrix[row][col].lower()
		# Instantiate the solver
		log('Creating the solver')
		self.solver = solver.Solver(layout.times, layout.strings)
		log('Solver created')
	
	def step(self, time):
		# Initialize an empty matrix
		truthMatrix = createTruthMatrix(self.layout.height, self.layout.width)
		# Ask the solver for the time
		log('Solving for the current time (%s)' % str(time))
		solution = self.solver.resolveTime(time)
		log('Solution: ' + str(solution))
		# Highlight the solution
		success = self.highlight(self.layout.matrix, truthMatrix, solution)
		log('Highlight results: ' + str(success))
		# Draw the result
		self.window.drawMatrix(truthMatrix)
	
	def highlight(self, charMatrix, truthMatrix, tokens):
		'''Highlight tokens in truthMatrix as they are found in charMatrix.
		This function returns True if all tokens are highlighted sucessfully,
		and False otherwise.'''
		for row in range(self.layout.height):
			if not len(tokens):
				break
			consumed = self.highlightRow(charMatrix[row], row, truthMatrix, tokens)
			tokens = tokens[consumed:]
		return len(tokens) == 0
	
	def highlightRow(self, charRow, row, truthMatrix, tokens):
		'''Highlight tokens in a row of chars (and each char is allowed to be
		composed of more than one char, such as in o'clock). row is used to
		keep track of the row in truthMatrix to highlight values on. The return
		value is the number of tokens consumed.'''
		tokensCopy = tokens # Shallow copy (deep is done via slice later)
		for i in range(len(charRow)):
			if len(tokens) == 0:
				break
			token = tokens[0]
			if ''.join(charRow[i:]).startswith(token):
				# Found a match
				while len(token):
					truthMatrix[row][i] = True
					# Don't just pop 1 char, because charRow[i] might be longer
					# than a single char (such as the o' in o'clock)
					token = token[len(charRow[i]):]
					i = i + 1
				# Elements have been highlighted, move on to the next token
				tokens = tokens[1:]
		return len(tokensCopy) - len(tokens)
	
	def cleanup(self):
		'''Clear window properties'''
		truthMatrix = createTruthMatrix(self.layout.height, self.layout.width)
		self.window.drawMatrix(truthMatrix)
		pass
	
	def calcDelay(self, layout):
		'''The delay is calculated from the GCD of every time entry.'''
		return reduce(gcd, [time.toSeconds() for time in layout.times.keys()])



class SpriteThread(StateMachine):
	def __init__(self, window, config):
		super(SpriteThread, self).__init__(self.calcDelay(config))
		self.window = window
		self.config = config
	
	def step(self, time):
		self.window.drawSprites(0)
	
	def cleanup(self):
		# clear window properties
		pass
	
	def calcDelay(self, config):
		return 5.0
