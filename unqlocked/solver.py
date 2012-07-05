from unqlocked import log, Time


class Token(object):
	'''Base class (to appease my OOP heritage), a token can be a string
	constant or a symbol (appearing as %1h% in the <time> text).'''
	pass


class Constant(Token):
	def __init__(self, name):
		self.name = name
	
	def __unicode__(self):
		return self.name


class Symbol(Token):
	'''A symbol has these properties:
	self.unit - the hour, minute or second of this symbol
	self.transform - lambda function that determines the actual number of this symbol
	self.stringTable - dictionary for the final conversion of number to string
	self.timeSource - when converted to a string, this is used as the current time
	
	Two other properties are passed as parameters (and rolled into the lambda function):
	use24 - whether we should wrap around at 12 or 24 hours
	use0 - if the clock system's hours start at zero or 1
	
	To update this symbol to the current time, it is sufficient to change
	the timeSource reference and convert to a string again.'''
	def __init__(self, symbol, time, stringTable, timeSource, use24, use0):
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
			# If minutes > 30 and the symbol has a number < 30, then assume it's
			# counting down. Example: <time id="1:35">it is %25m% to %2h%</time>
			if not (ref > 30 and metric < 30):
				self.transform = lambda x: (x + metric - ref) % 60 # Counting up
			else:
				self.transform = lambda x: -(x - metric - ref) % 60 # Counting down
		
		self.stringTable = stringTable
		self.timeSource = timeSource
	
	def __unicode__(self):
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


class Compound(Token):
	'''A compound token is a single word consisting of both symbols and plain
	characters.'''
	def __init__(self, parts):
		self.parts = parts
	
	def __unicode__(self):
		return u''.join([unicode(part) for part in self.parts])


class RuleNode(object):
	def __init__(self, rule, time, next = None):
		self.rule = rule
		self.time = time
		self.next = next


class RuleChain(object):
	def __init__(self, strings, timeSource, use24, use0):
		self.strings = strings
		self.timeSource = timeSource
		self.use24 = use24
		self.use0 = use0
		self.rules = [None for i in range(24 if self.use24 else 12)]
	
	def add(self, timeObject, timeString):
		log('Adding rule %s: ' % str(timeObject) + timeString.encode('utf-8'))
		# Use 1-based time for rule resolution
		timeObject.hours = (timeObject.hours - 1) % (24 if self.use24 else 12) + 1
		rule = [self.createToken(word, timeObject) for word in timeString.split(' ')]
		# If rule contains no symbols, only constants, then only add rule for its hour
		isConst = ([isinstance(token, Constant) for token in rule].count(False) == 0)
		# i_0 is 0-based hour, i_1 is 1-based hour
		for i_0 in range(len(self.rules)):
			i_1 = (i_0 - 1) % (24 if self.use24 else 12) + 1
			if isConst and i_1 != timeObject.hours:
				continue
			self.rules[i_0] = self.insert(self.rules[i_0], rule, timeObject, i_1, True)
	
	def insert(self, node, rule, time, ruleChainHour, first = False): # first = only for logging
		i = ruleChainHour
		a = 2
		if (i <= a and first): log('Creating rule for hour %d' % i)
		if node == None:
			# Base case: create a new node
			if (i <= a): log('Base case: new node (%d)' % len(rule))
			return RuleNode(rule, time)
		
		if time.minutes == node.time.minutes and time.seconds == node.time.seconds:
			# Same time, only replace if hour is greater
			if time.hours <= ruleChainHour:
				if (i <= a): log('Same time: replacing node (%d) (%d <= %d)' % (len(node.rule), time.hours, i))
				return RuleNode(rule, time, node.next)
			# Otherwise, ignore it
			if (i <= a): log('Same time: ignoring rule (%d)' % len(rule))
			return node
		
		# Assume the same hour as the node so comparisons will work
		tempTime = Time(node.time.hours, time.minutes, time.seconds)
		
		# If it occurs before this node, simply prepend it to the chain
		if tempTime.toSeconds() < node.time.toSeconds():
			if (i <= a): log('Time occurs earlier, prepending rule in front of (%d)' % len(node.rule))
			return RuleNode(rule, time, node)
		
		# Represent node.next.time in terms of time's hours
		if node.next != None:
			tempTime = Time(node.next.time.hours, time.minutes, time.seconds)
		
		# If no next node, or it doesn't occur before the next node, recurse deeper
		if node.next == None or tempTime.toSeconds() >= node.next.time.toSeconds():
			if (i <= a): log('Recursing deeper (leaving %d)' % len(node.rule))
			node.next = self.insert(node.next, rule, time, ruleChainHour)
			return node
		
		# Time occurs between node.time and node.next.time, perform the linking
		if (i <= a): log('Base case: linking in new node after (%d)' % len(node.rule))
		node.next = RuleNode(rule, time, node.next)
		return node
	
	def createToken(self, token, time):
		'''Translate a string into a Constant or a Symbol. Returns a Token
		object.'''
		if self.isSymbol(token):
			return Symbol(token, time, self.strings, self.timeSource, self.use24, self.use0)
		elif self.isCompound(token):
			parts = [self.createToken(part, time) for part in self.getParts(token)]
			return Compound(parts)
		else:
			return Constant(token)

	def isSymbol(self, test):
		'''A symbol looks like %1h%'''
		if len(test) >= 4 and test[0] == '%' and test[-1] == '%':
			# Unit is the last-but-one char
			unit = test[-2]
			try:
				# Bypass % and unit
				metric = int(test[1:-2])
			except:
				return False
			if unit == 'h':
				return 0 <= metric and metric <= 24 # include 24
			elif unit == 'm' or unit == 's':
				return 0 <= metric and metric <= 60 # include 60
		return False
	
	def isCompound(self, test):
		'''A compound token contains symbols surrounded by other chars. This is
		a pretty naive algorithm; symbols are 4 or 5 tokens, so just test every
		4 and 5 token combination in the string for token-ness. If a symbol is
		passed to this function, it will return true, so test for symbol-ness
		before caling isCompound().'''
		if len(test) <= 4:
			return False
		for i in range(len(test) - 3):
			if test[i] == '%' and (self.isSymbol(test[i : i + 4]) or \
						i + 4 < len(test) and self.isSymbol(test[i : i + 5])):
				return True
		return False
	
	def getParts(self, compound):
		'''Break a compound token into an array of Constants and Symbols.
		Each part returned is guaranteed to not be a Compound itself.'''
		parts = []
		i = 0
		while i < len(compound):
			if compound[i] == '%':
				is4chars = i + 4 <= len(compound) and self.isSymbol(compound[i : i + 4])
				is5chars = i + 5 <= len(compound) and self.isSymbol(compound[i : i + 5])
				if is4chars or is5chars:
					symbolSize = 4 if is4chars else 5
					if i > 0:
						parts.append(compound[:i])
					parts.append(compound[i : i + symbolSize])
					compound = compound[i + symbolSize : ]
					i = 0
					continue
			i = i + 1
		if i > 0:
			parts.append(compound[:])
		return parts
	
	def lookup(self, time):
		log('Looking up rule for %s' % str(time))
		ruleChain = self.rules[time.hours % (24 if self.use24 else 12)]
		tokens = []
		for token in self.lookupRecursive(ruleChain, time):
			s = unicode(token)
			# Need to split up multi-word tokens (in case a <string> entry
			# includes a space)
			tokens.extend(s.split(' ') if ' ' in s else [s])
		return tokens
	
	def lookupRecursive(self, node, time):
		if node == None:
			log('ERROR: No node, returning []')
			return []
		log('Testing node (%d)' % len(node.rule))
		
		# Same as insert(), mimic the node's hours to use comparison operators
		tempTime = Time(node.time.hours, time.minutes, time.seconds)
		if tempTime.toSeconds() <= node.time.toSeconds():
			log('Returning (%d): %s <= %s' % (len(node.rule), str(tempTime), str(node.time)))
			return node.rule
		
		log('Continuing: %s > %s' % (str(tempTime), str(node.time)))
		log('Continuing: %d > %d' % (tempTime.toSeconds(), node.time.toSeconds()))
		
		if node.next == None:
			log('Base case: Next node is null, returning this one (%d)' % len(node.rule))
			return node.rule
		
		# Same as insert(), mimic the next node's hours to use comparison operators
		tempTime = Time(node.next.time.hours, time.minutes, time.seconds)
		log('My time: ' + str(tempTime) + ', Next node time: ' + str(node.next.time))
		if tempTime.toSeconds() < node.next.time.toSeconds():
			log('Base case: Next node in the future, returning this one (%d)' % len(node.rule))
			return node.rule
		
		# Our time comes after the next node, so continue the lookup from the next node
		log('Searching deeper (%d)' % len(node.rule))
		return self.lookupRecursive(node.next, time)


class Solver(object):
	def __init__(self, times, use24, strings):
		self.strings = strings
		# Time reference used to stringify symbols
		self.time = Time(0, 0, 0)
		
		# Use 0 only for 24-hour mode, unless a 0 is found in 12-hour mode or
		# a 24 is found in 24-hour mode
		use0 = use24
		for timeObject in times.keys():
			if not use24 and timeObject.hours == 0:
				use0 = True
				break
			if use24 and timeObject.hours == 24:
				use0 = False
				break
		
		self.rules = RuleChain(self.strings, self.time, use24, use0)
		for timeObject in sorted(times.keys(), key=lambda t: t.toSeconds()):
			timeString = times[timeObject]
			timeObject.hours = timeObject.hours % 12
			self.rules.add(timeObject, timeString)
	
	def resolveTime(self, time):
		# Symbols resolve themselves against self.time, so clone the fields
		# instead of overwriting the object
		self.time.hours = time.hours
		self.time.minutes = time.minutes
		self.time.seconds = time.seconds
		return self.rules.lookup(time)
