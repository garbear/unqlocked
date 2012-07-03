from unqlocked import log, Time


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
	'''A symbol has these properties:
	self.unit - the hour, minute or second of this symbol
	self.transform - lambda function that determines the actual number of this symbol
	self.stringTable - dictionary for the final conversion of number to string
	self.timeSource - when converted to a string, this is used as the current time
	self.use24 - whether we should wrap around at 12 or 24 hours
	self.use0 - if the clock system's hours start at zero or 1
	
	To update this symbol to the current time, it is sufficient to change
	the timeSource reference and convert to a string again.'''
	def __init__(self, symbol, time, stringTable, timeSource, use24, use0):
		#self.use24 = use24
		#self.use0 = use0
		
		# Unit comes before the last %
		self.unit = symbol[-2]
		
		# Number comes between the % and the unit
		metric = int(symbol[1:-2])
		ref = (time.hours if self.unit == 'h' else (time.minutes if self.unit == 'm' else time.seconds))
		
		if self.unit == 'h':
			if use0:
				self.transform = lambda x: (x + metric - ref) % (24 if use24 else 12)
			else:
				self.transform = lambda x: (x + metric - ref - 1) % (24 if use24 else 12) + 1
		else:
			# Check to see if we're counting down
			if not (ref > 30 and metric < 30):
				self.transform = lambda x: (x + metric - ref) % 60 # Counts up
			else:
				self.transform = lambda x: -(x - metric - ref) % 60 # Counts down
		
		self.stringTable = stringTable
		self.timeSource = timeSource
	
	def __str__(self):
		'''Convert the symbol to a string. If the stringTable entry for the
		calculated number has a space, then the returned value will also have
		a space and will need to be split.'''
		if self.unit == 'h':
			id = self.transform(self.timeSource.hours)
		elif self.unit == 'm':
			id = self.transform(self.timeSource.minutes)
		elif self.unit == 's':
			id = self.transform(self.timeSource.seconds)
		return self.stringTable[id]


class RuleNode(object):
	def __init__(self, rule):
		self.rule = rule
		self.time = None
		self.nextTick = None
		self.nextHour = None

class RuleChain(object):
	def __init__(self, strings, timeSource, use24, use0):
		self.strings = strings
		self.timeSource = timeSource
		self.use24 = use24
		self.use0 = use0
		#self.rules = None
		self.rules = []
	
	def add(self, timeObject, timeString):
		rule = [self.createToken(word, timeObject) for word in timeString.split(' ')]
		
		node = RuleNode(rule)
		
		self.rules.append(rule)
	
	def createToken(self, token, time):
		'''Translate a string into a Constant or a Symbol. Returns a Token
		object.'''
		if self.isSymbol(token):
			log('Creating symbol for %s' % token)
			return Symbol(token, time, self.strings, self.timeSource, self.use24, self.use0)
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
		rule = self.rules[0]
		tokens = []
		for token in rule:
			s = str(token)
			# Need to split up multi-word tokens (in case a <string> entry
			# includes a space)
			tokens.extend(s.split(' ') if ' ' in s else [s])
		return tokens


class Solver(object):
	def __init__(self, times, strings):
		self.strings = strings
		# Time reference used to stringify symbols
		self.time = Time(0, 0, 0)
		
		# Switch to 24-hour mode if a hour >= 13 appears. Use 0 only for
		# 24-hour mode, unless a 0 is found for 12-hour mode or a 24 is found
		# for 24-hour mode
		use24 = False
		use0 = False
		for timeObject in times.keys():
			if timeObject.hours == 0:
				use0 = True
			if timeObject.hours >= 13:
				use24 = True
				use0 = True
				continue
			if timeObject.hours == 24:
				use0 = False
		
		self.rules = RuleChain(self.strings, self.time, use24, use0)
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
