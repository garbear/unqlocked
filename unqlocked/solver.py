from unqlocked import log
import controller # for Time

class Token(object):
	'''Base class (to appease my OOP heritage), a token can be a string
	constant or a symbol (appearing as %1h% in the <time> text).'''
	pass

class Constant(Token):
	def __init__(self, name):
		self.name = name
	
	def __str__(self):
		return self.name

class Symbol(Token):
	'''A symbol has four properties:
	self.unit - the hour, minute or second of this symbol
	self.transform - lambda function that determines the actual number of this symbol
	self.stringTable - dictionary for the final conversion of number to string
	self.timeSource - when converted to a string, this is used as the current time
	
	To update this symbol to the current time, it is sufficient to change
	the timeSource reference and convert to a string again.'''
	def __init__(self, symbol, time, stringTable, timeSource):
		self.unit = symbol[-2] # unit comes before the last %
		log('Symbol: Unit: %s' % self.unit)
		metric = int(symbol[1:-2]) # number comes between the % and the unit
		log('Symbol: Metric: %d' %  metric)
		if self.unit == 'h':
			diff = metric - time.hours
			self.transform = lambda x: (x + diff) % 12 # TODO: or 24
		elif self.unit == 'm':
			diff = metric - time.minutes
			self.transform = lambda x: (x + diff) % 60
		elif self.unit == 's':
			diff = metric - time.seconds
			self.transform = lambda x: (x + diff) % 60
		log('Symbol: Diff: %d' % diff)
		self.stringTable = stringTable
		self.timeSource = timeSource
	
	def __str__(self):
		log('Converting symbol to string')
		if self.unit == 'h':
			log('timeSource.hours is %d' % self.timeSource.hours)
			id = self.transform(self.timeSource.hours)
		elif self.unit == 'm':
			log('timeSource.minutes is %d' % self.timeSource.minutes)
			id = self.transform(self.timeSource.minutes)
		elif self.unit == 's':
			log('timeSource.seconds is %d' % self.timeSource.seconds)
			id = self.transform(self.timeSource.seconds)
		log('Transformed id is %d' % id)
		return self.stringTable[id]

class RuleChain(object):
	def __init__(self, strings, timeSource):
		self.strings = strings
		self.timeSource = timeSource
		self.rules = []
	
	def add(self, timeObject, timeString):
		rule = [self.createToken(word, timeObject) for word in timeString.split(' ')]
		self.rules.append(rule)
	
	def createToken(self, token, time):
		'''Translate a string into a Constant or a Symbol. Returns a Token
		object.'''
		if self.isSymbol(token):
			return Symbol(token, time, self.strings, self.timeSource)
		else:
			return Constant(token)
	
	def isSymbol(self, test):
		'''A symbol looks like %1h%'''
		if len(test) >= 4 and test[0] == '%' and test[-1] == '%':
			# Unit is the last-but-one char
			unit = test[-2]
			# Bypass % and unit
			metric = int(test[1:-2])
			if unit == 'h':
				return 0 <= metric and metric <= 24 # include 24
			elif unit == 'm' or unit == 's':
				return -60 <= metric and metric <= 60 # include 60
		return False
	
	def lookup(self, time):
		return self.rules[0]

class Solver(object):
	def __init__(self, times, strings):
		self.strings = strings
		# Time reference used to stringify symbols
		self.time = controller.Time(0, 0, 0)
		
		self.rules = RuleChain(self.strings, self.time)
		for timeObject in sorted(times.keys(), key=lambda t: t.toSeconds()):
			timeString = times[timeObject]
			self.rules.add(timeObject, timeString)
	
	def resolveTime(self, time):
		# Symbols resolve themselves against self.time, so clone the fields
		# instead of overwriting the object
		self.time.hours = time.hours
		self.time.minutes = time.minutes
		self.time.seconds = time.seconds
		return self.rules.lookup(time)
