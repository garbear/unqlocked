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

from unqlocked import log, WINDOW_ID

from elementtree.ElementTree import Element, SubElement, parse
import os
import xbmc

PROPERTY_ACTIVE = 'Unqlocked.%i.Highlight'
PROPERTY_INACTIVE = 'Unqlocked.%i.Background'

BACKGROUND_IMAGE = 'unqlocked-1px-white.png'

CONTROL_BACKGROUND = 1
CONTROL_IMAGE      = 2
CONTROL_PANEL      = 3

WIDTH = 500
HEIGHT = 500


class Letter(object):
	def __init__(self, index):
		'''Initialize a letter object by its index. The value of the label is
		set later by the UnqlockedWindow object. If the layout dimensions are
		the same, it is technically possible to switch languages at runtime.'''
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


class Matrix(object):
	def __init__(self, letters, layout, theme):
		self.letters = letters
		self.layout = layout
		self.theme = theme
		
		self.posx = (1280 - WIDTH) / 2
		self.posy = (720 - HEIGHT) / 2
		self.width = WIDTH
		self.height = HEIGHT
		
		self.letterHeight = HEIGHT / layout.height
		self.letterWidth = WIDTH / layout.width
		
		# Generate front name here because addItemLayout() gets called twice
		self.font = self.getFont()
	
	def toXML(self):
		'''Generate the xml representation of the letter matrix'''
		# <control type="panel">
		control = Element('control', type='panel', id=str(CONTROL_PANEL))
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
			itemlayout = SubElement(control, 'itemlayout', height=str(self.letterHeight), width=str(self.letterWidth))
			if True:
				self.addItemLayout(itemlayout, self.theme.inactive, 1)
				self.addItemLayout(itemlayout, self.theme.active, 2)
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
		'''
		Add a control to an <itemlayout> tag.
		infolabel (int) - 1 or 2
		'''
		label = 'ListItem.Label' if infolabel == 1 else 'ListItem.Label2'
		
		# <control type="label">
		subControl = SubElement(itemlayout, 'control', type='label')
		if True:
			# Center the letter horizontally
			SubElement(subControl, 'posx').text = str(self.letterWidth / 2)
			SubElement(subControl, 'posy').text = str(0)
			SubElement(subControl, 'width').text = str(self.letterWidth)
			SubElement(subControl, 'height').text = str(self.letterHeight)
			SubElement(subControl, 'font').text = self.font
			SubElement(subControl, 'textcolor').text = color
			SubElement(subControl, 'selectedcolor').text = color
			SubElement(subControl, 'align').text = 'center'
			SubElement(subControl, 'aligny').text = 'center'
			# <label>[B]$INFO[ListItem.Label][/B]</label>
			SubElement(subControl, 'label').text = '[B]$INFO[%s][/B]' % label
		# </control>
	
	def getFont(self):
		'''Parse the current skin's Font.xml file for a list of font names by
		size'''
		log('Loading font set from current skin: ' + xbmc.getSkinDir())
		
		fontName = ''
		# Use letterHeight (reasoning: WIDTH may be elastic in the future)
		desiredSize = self.letterHeight * 1 / 2 # Decent ratio
		fallback = 'font'
		
		# Font.xml can be in any resolution folder, keep trying until we find
		# one. Use the first Font.xml we come across.
		skinDir = xbmc.translatePath("special://skin/")
		for item in os.listdir(skinDir):
			fontFile = os.path.join(skinDir, item, 'Font.xml')
			if not os.path.exists(fontFile):
				continue
			try:
				root = parse(fontFile).getroot()
			except:
				continue
			for set in root.findall('fontset'):
				# Now that we've found the file, use the Default fontset
				# (guaranteed to exist regardless of skin)
				if 'id' not in set.attrib or set.attrib['id'] != 'Default':
					continue
				log('Font set loaded. Searching for a font smaller than %dpt' % desiredSize)
				# Index the discovered fonts into two categories
				fontsWithoutStyle = {}
				fontsWithStyle = {}
				for font in set.findall('font'):
					if font.find('size') == None or font.find('name') == None:
						continue
					size = int(font.find('size').text)
					# Skip fonts larger than the desired size
					if size > desiredSize:
						continue
					if not font.find('style'):
						fontsWithoutStyle[size] = font.find('name').text
					else:
						fontsWithStyle[size] = font.find('name').text
				# Categories generated. Prefer unstyled fonts
				if len(fontsWithoutStyle):
					max = sorted(fontsWithoutStyle.keys(), reverse=True)[0]
					log('Using unstyled font "%s" (%dpt)' % (fontsWithoutStyle[max], max))
					return fontsWithoutStyle[max]
				elif len(fontsWithStyle):
					max = sorted(fontsWithStyle.keys(), reverse=True)[0]
					log('Using styled font "%s" (%dpt)' % (fontsWithStyle[max], max))
					return fontsWithStyle[max]
				log('No suitable fonts found. Falling back to ' + fallback)
				return fallback
			log('Default font set not found. Falling back to ' + fallback)
			return fallback
		log('Font.xml not found. Falling back to ' + fallback)
		return fallback


class Sprites(object):
	def __init__(self, layout, theme):
		self.layout = layout
		self.theme = theme
	
	def toXML(self):
		pass


class Image(object):
	def __init__(self, width, height, image, diffuse=None):
		self.width = width
		self.height = height
		self.image = image
		self.diffuse = diffuse
		self.id = CONTROL_BACKGROUND if image == BACKGROUND_IMAGE else CONTROL_IMAGE
	
	def toXML(self):
		# <control>
		control = Element('control', type='image', id=str(self.id))
		if True:
			SubElement(control, 'posx').text = str((1280 - self.width) / 2)
			SubElement(control, 'posy').text = str((720 - self.height) / 2)
			SubElement(control, 'width').text = str(self.width)
			SubElement(control, 'height').text = str(self.height)
			SubElement(control, 'texture').text = self.image
			if self.diffuse:
				SubElement(control, 'colordiffuse').text = self.diffuse # AARRGGBB
			
		# </control>
		return control


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


class Window(object):
	def __init__(self, layout, theme, screensaverMode):
		self.letters = [Letter(i) for i in range(layout.width * layout.height)]
		self.layout = layout
		self.theme = theme
		self.screensaverMode = screensaverMode
	
	def toXML(self):
		# <window>
		window = Element('window', id=str(WINDOW_ID))
		if True:
			# Fade in for 1.0 second (but not in screensaver mode)
			if not self.screensaverMode:
				SubElement(window, 'animation', effect='fade', time=str(1000)).text = 'WindowOpen'
			
			# <controls>
			controls = SubElement(window, 'controls')
			if True:
				# <control type="image">
				color = Image(1280, 720, BACKGROUND_IMAGE, self.theme.background)
				controls.append(color.toXML())
				# </control>
				
				# <control type="image">
				if self.theme.image:
					image = Image(self.theme.imageWidth, self.theme.imageHeight, self.theme.image)
				else:
					# Placeholder for if we change the theme by pressing T
					image = Image(1280, 720, '-')
				controls.append(image.toXML())
				# </control>
				
				#sprites = Sprites(self.layout, self.theme)
				#controls.append(sprites.toXML())
				
				# <control type="panel">
				matrix = Matrix(self.letters, self.layout, self.theme)
				controls.append(matrix.toXML())
				# </control>
			# </controls>
		# </window>
		return window
	
	def toXMLPrettyPlease(self):
		windowNode = self.toXML()
		indent(windowNode)
		return windowNode

