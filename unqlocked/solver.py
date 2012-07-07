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

from unqlocked import log, Time

from copy import deepcopy

class Token(object):
	'''
	Base class, a token can be a string constant or a symbol (appearing as
	%1h% in the <time> text).
	'''
	pass


class Constant(Token):
	def __init__(self, name):
		self.name = name
	
	def __unicode__(self):
		return self.name


class Symbol(Token):
	'''
	A symbol has these properties:
	self.unit - the hour, minute or second of this symbol
	self.transform - lambda function that determines the actual number of this symbol
	self.stringTable - dictionary for the final conversion of number to string
	self.timeSource - when converted to a string, this is used as the current time
	
	Two other properties are passed as parameters (and rolled into the lambda function):
	use24 - whether we should wrap around at 12 or 24 hours
	use0 - if the clock system's hours start at zero or 1
	
	To update this symbol to the current time, it is sufficient to change
	the timeSource reference and convert to a string again.
	'''
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
		'''
		Convert the symbol to a string. If the stringTable entry for the
		calculated number has a space, then the returned value will also have
		a space and will need to be split.
		'''
		if self.unit == 'h':
			id = self.transform(self.timeSource.hours)
		elif self.unit == 'm':
			id = self.transform(self.timeSource.minutes)
		elif self.unit == 's':
			id = self.transform(self.timeSource.seconds)
		return self.stringTable[id]


class Compound(Token):
	'''
	A compound token is a single word consisting of both symbols and plain
	characters.
	'''
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
		
		for i in range(len(self.rules)):
			hour = (i - 1) % (24 if self.use24 else 12) + 1 # make hour 1-based
			
			# Constant times only for the same hour (until duration is supported)
			if isConst and hour != timeObject.hours:
				continue
			
			self.rules[i] = self.insert(self.rules[i], rule, timeObject, hour)
	
	def insert(self, node, rule, time, ruleChainHour):
		i = ruleChainHour
		a = 2
		if node == None:
			# Base case: create a new node
			if (i <= a): log('Base case: new node (%d)' % len(rule))
			return RuleNode(rule, time)
		
		# Assume the same hour as the node so comparisons will work
		tempTime = Time(node.time.hours, time.minutes, time.seconds)
		
		if tempTime.toSeconds() < node.time.toSeconds():
			# If it occurs before this node, simply prepend it to the chain
			if (i <= a): log('Time occurs earlier, prepending rule in front of (%d)' % len(node.rule))
			return RuleNode(rule, time, node)
		
		if tempTime.toSeconds() == node.time.toSeconds():
			# Only replace rule if approapriate (that is, the rule chain we are
			# storing our rule in is later than (or equal to) the rule's time.
			# This prevents us from having a later rule overwrite an earlier one.
			# Thus, <time id="1:00">%1h%</time> and <time id="2:00">%2h%</time>
			# will cause %1h% to be stored for all hours, and %2h% will then
			# overwrite all hours except for hour 1.
			if ruleChainHour >= time.hours:
				if (i <= a): log('Same time: replacing node (%d) (%d <= %d, %d)' % (len(node.rule), time.hours, ruleChainHour, node.time.hours))
				return RuleNode(rule, time, node.next)
			else:
				# Otherwise, ignore it
				if (i <= a): log('Same time: ignoring rule (%d) (%d > %d, %d)' % (len(node.rule), time.hours, ruleChainHour, node.time.hours))
				return node
		
		# tempTime.toSeconds() > node.time.toSeconds()
		
		if node.next and Time(node.next.time.hours, time.minutes, time.seconds).toSeconds() \
					< node.next.time.toSeconds():
			# Time occurs between node.time and node.next.time, perform the linking
			if (i <= a): log('Base case: linking in new node after (%d)' % len(node.rule))
			node.next = RuleNode(rule, time, node.next)
		else:
			# Next node doesn't exist, or is earlier than the rule's time
			# Recurse deeper
			node.next = self.insert(node.next, rule, time, ruleChainHour)
		
		return node
	
	def createToken(self, token, time):
		'''Translate a string into an object inheriting from the Token class.'''
		if self.isSymbol(token):
			return Symbol(token, time, self.strings, self.timeSource, self.use24, self.use0)
		elif self.isCompound(token):
			parts = [self.createToken(part, time) for part in self.getParts(token)]
			return Compound(parts)
		else:
			return Constant(token)

	def isSymbol(self, test):
		'''A symbol looks like this: %1h%'''
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
		'''
		A compound token contains symbols surrounded by other chars. This is
		a pretty naive algorithm; symbols are 4 or 5 tokens, so just test every
		4 and 5 token combination in the string for token-ness. If a symbol is
		passed to this function, it will return true, so test for symbol-ness
		before caling isCompound().
		'''
		if len(test) <= 4:
			return False
		for i in range(len(test) - 3):
			if test[i] == '%' and (self.isSymbol(test[i : i + 4]) or \
						i + 4 < len(test) and self.isSymbol(test[i : i + 5])):
				return True
		return False
	
	def getParts(self, compound):
		'''
		Break a compound token into an array of Constants and Symbols.
		Each part returned is guaranteed to not be a Compound itself.
		'''
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
					
					# We just found some parts. Erase them from compound and reset i
					compound = compound[i + symbolSize : ]
					i = 0
					continue # Don't increment i
			# No part boundaries found, keep going
			i = i + 1
		
		# Tack on whatever was left over
		if i > 0:
			parts.append(compound[:])
		
		return parts
	
	def lookup(self, time):
		log('Looking up rule for %s' % str(time))
		ruleChain = self.rules[time.hours % (24 if self.use24 else 12)]
		tokens = []
		for token in self.lookupRecursive(ruleChain, time):
			s = unicode(token)
			# Need to split up multi-word tokens (such as in the case:
			# <string id="25">twenty five</string>)
			tokens.extend(s.split(' ') if ' ' in s else [s])
		return tokens
	
	def lookupRecursive(self, node, time):
		if node == None:
			log('ERROR: No node, returning []')
			return []
		
		if node.next == None:
			# Base case: next node is null, return this one
			return node.rule
		
		# Compare minutes and seconds (by making the hours equal)
		tempTime = Time(node.time.hours, time.minutes, time.seconds)
		if tempTime.toSeconds() <= node.time.toSeconds():
			# Base case: time comes before node.time, so return node.rule
			return node.rule
		
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
