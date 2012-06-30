from unqlocked import log, WINDOW_ID
from elementtree.ElementTree import Element, SubElement
import xbmc, xbmcgui

PROPERTY_ACTIVE = 'Unqlocked.%i.Highlight'
PROPERTY_INACTIVE = 'Unqlocked.%i.Background'

class Letter:
	def __init__(self, letter, index):
		self.letter = letter
		self.index = index
	
	def toXML(self):
		'''Generate the xml representation of this Letter'''
		# <item>
		item = Element('item')
		if True:
			# <label>$INFO[Window(Home).Property(Unqlocked.0.Background)]</label>
			SubElement(item, 'label').text = '$INFO[Window(Home).Property(%s)]' % (PROPERTY_INACTIVE % self.index)
			# <label2>$INFO[Window(Home).Property(Unqlocked.0.Highlight)]</label2>
			SubElement(item, 'label2').text = '$INFO[Window(Home).Property(%s)]' % (PROPERTY_ACTIVE % self.index)
			# <onclick>-</onclick>
			SubElement(item, 'onclick').text = '-'
		# </item>
		return item

class Matrix:
	def __init__(self, letters, layout, theme):
		self.letters = letters
		self.layout = layout
		self.theme = theme
		
		self.posx = 455 # 27 + 428
		self.posy = 185 # 20 + 165
		self.width = 385
		self.height = 350
		
		self.letterHeight = 35
		self.letterWidth = 35
	
	def toXML(self):
		'''Generate the xml representation of the letter matrix'''
		# <control type="panel">
		control = Element('control', type='panel')
		if True:
			SubElement(control, 'posx').text = str(self.posx)
			SubElement(control, 'posy').text = str(self.posy)
			SubElement(control, 'width').text = str(self.width)
			SubElement(control, 'height').text = str(self.height)
			SubElement(control, 'onleft').text = '-'
			SubElement(control, 'onright').text = '-'
			SubElement(control, 'onup').text = '-'
			SubElement(control, 'ondown').text = '-'
			SubElement(control, 'viewtype', label='').text = 'panel'
			SubElement(control, 'pagecontrol').text = '-'
			SubElement(control, 'scrolltime').text = '-'
			SubElement(control, 'hitrect', x=str(-10), y=str(-10), w=str(1), h=str(1))
			# <itemlayout>
			itemlayout = SubElement(control, 'itemlayout', height=str(self.height), width=str(self.width))
			if True:
				self.addItemLayout(itemlayout, self.theme.inactive, 'ListItem.Label')
				self.addItemLayout(itemlayout, self.theme.active, 'ListItem.Label2')
			# </itemlayout>
			SubElement(control, 'focusedlayout', height=str(self.height), width=str(self.width))
			# <content>
			content = SubElement(control, 'content')
			if True:
				# <item>
				for letter in self.letters:
					content.append(letter.toXML())
				# </item>
			# </content>
		# </control>
		return control
	
	def addItemLayout(self, itemlayout, color, infolabel):
		'''Add a control to an <itemlayout> tag. infolabel one of the two
		strings: "ListItem.Label" or "ListItem.Label2" '''
		# <control type="label">
		subControl = SubElement(itemlayout, 'control', type='label')
		if True:
			SubElement(subControl, 'posx').text = str(10)
			SubElement(subControl, 'posy').text = str(0)
			SubElement(subControl, 'width').text = str(self.letterWidth)
			SubElement(subControl, 'height').text = str(self.letterHeight)
			SubElement(subControl, 'font').text = 'font-22' # or use self.theme.font
			SubElement(subControl, 'textcolor').text = color
			SubElement(subControl, 'selectedcolor').text = color
			SubElement(subControl, 'align').text = 'center'
			SubElement(subControl, 'aligny').text = 'center'
			# <label>[B]$INFO[ListItem.Label][/B]</label>
			SubElement(subControl, 'label').text = '[B]$INFO[%s][/B]' % infolabel
		# </control>


class Sprites:
	def __init__(self, layout, theme, config):
		pass


class Backgrounds:
	def __init__(self, theme):
		self.theme = theme
	
	# TODO: Don't hardcode width and height (and account for the offsets)
	def toXML(self):
		'''Return an array of controls to be used as backgrounds'''
		controls = []
		# <control>
		control = Element('control', type='image')
		if True:
			SubElement(control, 'posx').text = str(0)
			SubElement(control, 'posy').text = str(0)
			SubElement(control, 'width').text = str(1280)
			SubElement(control, 'height').text = str(720)
			SubElement(control, 'colordiffuse').text = 'DDFFFFFF' # AARRGGBB
			SubElement(control, 'texture').text = 'unqlocked-1px-black.png'
		# </control>
		controls.append(control)
		# <control>
		control = Element('control', type='image')
		if True:
			SubElement(control, 'posx').text = str(428)
			SubElement(control, 'posy').text = str(165)
			SubElement(control, 'width').text = str(425)
			SubElement(control, 'height').text = str(390)
			SubElement(control, 'texture', border=str(10)).text = 'qlock.png'
		# </control>
		controls.append(control)
		return controls

# http://effbot.org/zone/element-lib.htm#prettyprint
def indent(elem, level=0):
	'''In-place prettyprint formatter'''
	i = "\n" + level * "  "
	if len(elem):
		if not elem.text or not elem.text.strip():
			elem.text = i + "  "
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
		for elem in elem:
			indent(elem, level + 1)
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
	else:
		if level and (not elem.tail or not elem.tail.strip()):
			elem.tail = i

class Window:
	def __init__(self, layout, theme):
		self.letters = [Letter('A', 0), Letter('B', 1), Letter('C', 2)]
		self.layout = layout
		self.theme = theme
	
	def toXML(self):
		# <window>
		window = Element('window', id=str(WINDOW_ID))
		if True:
			SubElement(window, 'animation', effect='fade', time=str(1000)).text = 'WindowOpen'
			# <controls>
			controls = SubElement(window, 'controls')
			if True:
				backgrounds = Backgrounds(self.theme)
				for background in backgrounds.toXML():
					controls.append(background)
				#sprites = Matrix(self.layout, self.theme, None)
				#controls.append(sprites.toXML())
				matrix = Matrix(self.letters, self.layout, self.theme)
				controls.append(matrix.toXML())
			# </controls>
		# </window>
		return window
	
	def toPrettyXML(self):
		windowNode = self.toXML()
		indent(windowNode)
		return windowNode

