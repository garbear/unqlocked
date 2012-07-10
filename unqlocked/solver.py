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
			if not (ref > 30 and metric < 30 or ref < 30 and metric > 30):
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
	def __init__(self, strings, timeSource, use24, use0, defaultDuration):
		self.strings = strings
		self.timeSource = timeSource
		self.use24 = use24
		self.use0 = use0
		self.defaultDuration = defaultDuration
		self.rules = [None for i in range(24 if self.use24 else 12)]
	
	def add(self, timeObject, timeString, rule = None):
		'''
		timeObject - the id found in the <time> tag
		timeString - the text of the <time> tag
		rule - if the rule has already been created, it can be passed in as a
		parameter to avoid creating an unnecessary copy. Only do this if the
		rule is a constant (no symbols); otherwise, a modified timeObject will
		invalidate the rule.
		'''
		log('Adding rule %s: ' % str(timeObject) + timeString.encode('utf-8'))
		
		# Use 1-based time for rule resolution
		timeObject.hours = (timeObject.hours - 1) % (24 if self.use24 else 12) + 1
		
		# Create the rule
		if not rule:
			rule = [self.createToken(word, timeObject) for word in timeString.split(' ')]
		
		# If rule contains no symbols, only constants, then only add rule for its hour
		isConst = self.isConstant(rule)
		
		# Now that the rule is created, we can apply the default duration if
		# the rule is all constant
		if isConst and not timeObject.duration:
			timeObject.duration = Time.fromSeconds(self.defaultDuration)
		
		for i in range(len(self.rules)):
			hour = (i - 1) % (24 if self.use24 else 12) + 1 # make hour 1-based
			
			# Constant times are only for a single hour
			if isConst and hour != timeObject.hours:
				continue
			
			self.rules[i] = self.insert(self.rules[i], rule, timeObject, hour)
			
			if isConst:
				# However, if the duration pushes the rule into the next hour,
				# clone the rule (with an appropriately shorter duration) and
				# recursively add to the next hour as well.
				hourBoundary = (timeObject.hours + 1) * 3600
				if timeObject.end() > hourBoundary:
					# Start at the beginning of the next hour
					nextTime = Time(timeObject.hours + 1, 0, 0)
					nextTime.duration = Time.fromSeconds(timeObject.end() - hourBoundary)
					nextTime.useSeconds = timeObject.useSeconds # For cosmetics
					self.add(nextTime, timeString, rule)
				break
	
	def insert(self, node, rule, time, ruleChainHour):
		'''
		Recursive functions can get really tricky really quickly sticky.
		
		Ideally, this docstring would contain some helpful hints. Here's some
		terminology:
		"this node" - the parameter called node
		"this rule" - the parameter called rule, not this node's rule
		
		Beyond that... good luck!
		'''
		# If true, rule will override node during conflicts
		precedence = ruleChainHour >= time.hours
		
		if node == None:
			# Base case: insert a new node into the rule chain by creating it
			# and setting its child to this node.
			return RuleNode(rule, time, node)
		
		# Assume the same hour as the node so comparisons will work
		tempTime = Time(node.time.hours, time.minutes, time.seconds)
		tempTime.duration = time.duration
		
		if tempTime.toSeconds() < node.time.toSeconds():
			# Time occurs before this node, prepend it to the chain
			if not time.duration:
				return RuleNode(rule, time, node)
			
			# Three cases: rules don't overlap, rules overlap partially, rules overlap fully
			# Case 1
			if tempTime.end() <= node.time.toSeconds():
				return RuleNode(rule, time, node)
			
			# Case 2
			if tempTime.end() < node.time.end():
				if precedence:
					# Shorten node.time
					newBeginning = Time.fromSeconds(tempTime.end())
					newDuration = node.time.duration.toSeconds() - (node.time.end() - tempTime.end())
					newBeginning.duration = Time.fromSeconds(newDuration)
					node.time = newBeginning
					return RuleNode(rule, time, node)
				else:
					# Shorten time
					time.duration = Time.fromSeconds(node.time.toSeconds() - tempTime.toSeconds())
					return RuleNode(rule, time, node)
			
			# Case 3: time.end() >= node.time.end()
			if precedence:
				# Not including this node in the return statement effectively
				# eliminates it. However, things aren't this simple. We need to
				# check if the next node is partially/fully consumed via
				# recursion.
				return self.insert(node.next, rule, time, ruleChainHour)
			else:
				# Split the rule into two nodes that fall on either side of
				# this node. We create the following chain:
				# parent node -> node1 -> node -> node2 -> node.next
				time1 = time.copy()
				time1.duration = Time.fromSeconds(node.time.toSeconds() - tempTime.toSeconds())
				node1 = RuleNode(rule, time1, node)
				time2 = Time.fromSeconds(node.time.end())
				time2.hours = time.hours # Use original hours to maintain precedence
				time2.duration = Time.fromSeconds(tempTime.end() - node.time.end())
				# Use recursion, because time2 might extend past node.next
				node2 = self.insert(node.next, rule, time2, ruleChainHour)
				node.next = node2
				return node1
		
		if tempTime.toSeconds() == node.time.toSeconds():
			if not precedence:
				# Ignore the rule
				return node
			
			# Three cases: tempTime.duration and node.time.duration are True/False
			# Case 1
			if not tempTime.duration:
				# Replace the node
				return RuleNode(rule, time, node.next)
			
			# Case 2
			if not node.time.duration: # and tempTime.duration
				# Peek ahead at the future node
				if node.next:
					tempTime2 = Time(node.next.time.hours, time.minutes, time.seconds)
					tempTime2.duration = time.duration
					if tempTime2.end() > node.next.time.toSeconds():
						# Replace the node, and make sure that we replace any other
						# overlapped nodes (recursively, of course)
						# parent node -> node1 -> node.next
						node1 = self.insert(node.next, rule, time, ruleChainHour)
						return node1
				node.time = Time.fromSeconds(tempTime.end())
				return RuleNode(rule, time, node)
			
			# Case 3: node.time.duration and tempTime.duration
			if tempTime.end() >= node.time.end():
				# Replace the node and any following nodes if necessary
				node1 = self.insert(node.next, rule, time, ruleChainHour)
				return node1
			else:
				# Chop off and preserve the dangling part
				end = node.time.end()
				node.time = Time.fromSeconds(tempTime.end())
				# node.time.hours is already set because tempTime.hours was copied earlier
				node.time.duration = Time.fromSeconds(end - tempTime.end())
				return RuleNode(rule, time, node)
		
		# Rule occurs in the future: tempTime.toSeconds() > node.time.toSeconds()
		
		# Three cases: rules don't overlap, rules overlap partially, rules overlap fully
		# Case 1
		if node.time.end() <= tempTime.toSeconds():
			# If node.rule is a constant, it doesn't need to persist after its duration
			if not tempTime.duration or self.isConstant(node.rule):
				# Regular rule or node is constant, recurse deeper
				node.next = self.insert(node.next, rule, time, ruleChainHour)
				return node
			else:
				# Peek ahead at the future node
				if node.next:
					tempTime2 = Time(node.next.time.hours, time.minutes, time.seconds)
					tempTime2.duration = time.duration
					if tempTime2.toSeconds() > node.next.time.toSeconds():
						# Next node is in the future too, recurse deeper
						node.next = self.insert(node.next, rule, time, ruleChainHour)
						return node
				
				# tempTime has a duration so node should persist after rule's completion
				# To do so, we dupe node and let recursion do the rest
				timeCopy = Time.fromSeconds(tempTime.toSeconds())
				if node.time.duration:
					# Need to modify duration of both old and new time
					timeCopy.duration = Time.fromSeconds(node.time.end() - tempTime.toSeconds())
					node.time = node.time.copy()
					node.time.duration = Time.fromSeconds(tempTime.toSeconds() - node.time.toSeconds())
				nodeCopy = RuleNode(node.rule, timeCopy, node.next)
				node.next = self.insert(nodeCopy, rule, time, ruleChainHour)
				return node
		
		# Implicit that node.time.duration exists
		# Case 2
		if tempTime.end() > node.time.end():
			# Implicit that tempTime.duration exists
			if precedence:
				# Shorten node
				node.time = node.time.copy()
				node.time.duration = Time.fromSeconds(tempTime.toSeconds() - node.time.toSeconds())
				# Link in the new node after this one
				node.next = RuleNode(rule, time, node.next)
				return node
			else:
				# Shorten rule by giving it a later starting time
				time2 = Time.fromSeconds(node.time.end())
				time2.hours = time.hours # Use original hours to maintain precedence
				time2.duration = Time.fromSeconds(tempTime.end() - node.time.end())
				node.next = RuleNode(rule, time2, node.next)
				return node
		
		# Case 3: node.time has a duration and tempTime occurs in the middle of it
		if not precedence:
			if tempTime.duration:
				# tempTime is fully engulfed by node
				return node
			else:
				# tempTime is a rule, so it continues past node
				time2 = Time.fromSeconds(node.time.end())
				node.next = self.insert(node.next, rule, time2, ruleChainHour)
				return node
		if not tempTime.duration:
			# tempTime is a regular rule, so chop node in half and occupy the
			# second half with this rule
			node.time = node.time.copy()
			node.time.duration = Time.fromSeconds(tempTime.toSeconds() - node.time.toSeconds())
			# Link in the new node after this one
			node.next = RuleNode(rule, time, node.next)
			return node
		if tempTime.end() == node.time.end():
			# Ends coincide. Things are easy, just chop and link
			node.time = node.time.copy()
			node.time.duration = Time.fromSeconds(tempTime.toSeconds() - node.time.toSeconds())
			# Link in the new node after this one
			node.next = RuleNode(rule, time, node.next)
			return node
		# Things are messy. Bisect node:
		# parent node -> node(1) -> rule -> node(2) -> node.next
		# Go from last to first. Start with second node:
		time2 = Time.fromSeconds(tempTime.end())
		time2.duration = Time.fromSeconds(node.time.end() - tempTime.end())
		node2 = RuleNode(node.rule, time2, node.next)
		newNode = RuleNode(rule, time, node2)
		time1 = node.time.copy()
		time1.duration = Time.fromSeconds(tempTime.toSeconds() - node.time.toSeconds())
		node.time = time1
		node.next = newNode
		return node
	
	def isConstant(self, rule):
		'''
		Unlink the following is* functions, this operates on rules, not
		strings. A rule is an array of tokens created from strings.
		'''
		return ([isinstance(token, Constant) for token in rule].count(False) == 0)
	
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
		ruleChain = self.rules[time.hours % (24 if self.use24 else 12)]
		tokens = []
		for token in self.lookupRecursive(ruleChain, time):
			s = unicode(token)
			# Need to split up multi-word tokens, such as in the case:
			# <string id="25">twenty five</string>
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
		tempTime = Time(node.next.time.hours, time.minutes, time.seconds)
		if tempTime.toSeconds() < node.next.time.toSeconds():
			# Base case: time comes before node.time, so return node.rule
			return node.rule
		
		return self.lookupRecursive(node.next, time)
	
	def countNodes(self):
		'''Returns a count of nodes in this RuleChain'''
		nodes = 0
		for i in range(len(self.rules)):
			nodes = nodes + self.countRecursive(self.rules[i])
		return nodes
	
	def countRecursive(self, node):
		return 1 + self.countRecursive(node.next) if node else 0


class Solver(object):
	def __init__(self, layout, defaultDuration):
		self.strings = layout.strings
		# Time reference used to stringify symbols
		self.time = Time(0, 0, 0)
		
		# Use 0 only for 24-hour mode, unless a 0 is found in 12-hour mode or
		# a 24 is found in 24-hour mode
		use0 = layout.use24
		for timeObject in layout.times.keys():
			if not layout.use24 and timeObject.hours == 0:
				use0 = True
				break
			if layout.use24 and timeObject.hours == 24:
				use0 = False
				break
		
		self.rules = RuleChain(self.strings, self.time, layout.use24, use0, defaultDuration)
		for timeObject in sorted(layout.times.keys(), key=lambda t: t.toSeconds()):
			timeString = layout.times[timeObject]
			timeObject.hours = timeObject.hours % 12
			self.rules.add(timeObject, timeString)
	
	def resolveTime(self, time):
		# Symbols resolve themselves against self.time, so clone the fields
		# instead of overwriting the object
		self.time.hours = time.hours
		self.time.minutes = time.minutes
		self.time.seconds = time.seconds
		return self.rules.lookup(time)
	
	def countNodes(self):
		return self.rules.countNodes()
