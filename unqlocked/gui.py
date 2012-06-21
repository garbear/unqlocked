from unqlocked import log, WINDOW_ID
from elementtree.ElementTree import Element, SubElement
import xbmc, xbmcgui

ACTION_PARENT_DIR = 9
ACTION_PREVIOUS_MENU = 10
ACTION_NAV_BACK = 92


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
	
	def addItemLayout(self, itemlayout, color, infolabel):
		'''infolabel is "ListItem.Label" or "ListItem.Label2"'''
		# <control type="label">
		subControl = SubElement(itemlayout, 'control', type='label')
		if True:
			SubElement(subControl, 'posx').text = str(10) # <posx>
			SubElement(subControl, 'posy').text = str(0) # <posy>
			SubElement(subControl, 'width').text = str(self.letterWidth) # <width>
			SubElement(subControl, 'height').text = str(self.letterHeight) # <height>
			SubElement(subControl, 'font').text = 'font-22' # self.theme.font # <font>
			SubElement(subControl, 'textcolor').text = color # <textcolor>
			SubElement(subControl, 'selectedcolor').text = color # <selectedcolor>
			SubElement(subControl, 'align').text = 'center' # <align>center</align>
			SubElement(subControl, 'aligny').text = 'center' # <aligny>center</aligny>
			SubElement(subControl, 'label').text = '[B]$INFO[%s][/B]' % infolabel # <label>[B]$INFO[ListItem.Label][/B]</label>
		# </control>
	
	def toXML(self):
		'''Generate the xml representation of the letter matrix'''
		# <control type="panel">
		control = Element('control', type='panel')
		if True:
			SubElement(control, 'posx').text = str(self.posx) # <posx>
			SubElement(control, 'posy').text = str(self.posy) # <posy>
			SubElement(control, 'width').text = str(self.width) # <width>
			SubElement(control, 'height').text = str(self.height) # <height>
			SubElement(control, 'onleft').text = '-' # <onleft>-</onleft>
			SubElement(control, 'onright').text = '-' # <onright>-</onright>
			SubElement(control, 'onup').text = '-' # <onup>-</onup>
			SubElement(control, 'ondown').text = '-' # <ondown>-</ondown>
			SubElement(control, 'viewtype', label='').text = 'panel' # <viewtype label="">panel</viewtype>
			SubElement(control, 'pagecontrol').text = '-' # <pagecontrol>-</pagecontrol>
			SubElement(control, 'scrolltime').text = '-' # <scrolltime>-</scrolltime>
			SubElement(control, 'hitrect', x=str(-10), y=str(-10), w=str(1), h=str(1)) # <hitrect x="-10" y="-10" w="1" h="1" />
			# <itemlayout>
			itemlayout = SubElement(control, 'itemlayout', height=str(self.height), width=str(self.width))
			if True:
				self.addItemLayout(itemlayout, self.theme.inactive, 'ListItem.Label')
				self.addItemLayout(itemlayout, self.theme.active, 'ListItem.Label2')
			# </itemlayout>
			SubElement(control, 'focusedlayout', height=str(self.height), width=str(self.width)) # <focusedlayout height="35" width="35"/>
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


class Sprites:
	def __init__(self, layout, theme, config):
		pass


class Background:
	def __init__(self, theme):
		pass
	
	# TODO: Don't hardcode width and height (notice the offsets)
	def toXML(self):
		# <control>
		control = Element('control', type='image')
		if True:
			SubElement(control, 'posx').text = str(428) # <posx>
			SubElement(control, 'posy').text = str(165) # <posy>
			SubElement(control, 'width').text = str(425) # <width>
			SubElement(control, 'height').text = str(390) # <height>
			SubElement(control, 'texture', border=str(10)).text = 'qlock.png' # <texture border="10"></texture>
		# </control>
		return control


class Window:
	def __init__(self, layout, theme):
		self.letters = [Letter('A', 0), Letter('B', 1), Letter('C', 2)]
		self.layout = layout
		self.theme = theme
	
	def toXML(self):
		# <window id="3000">
		window = Element('window')
		window.attrib['id'] = str(3000)
		if True:
			# <controls>
			controls = Element('controls')
			matrix = Matrix(self.letters, self.layout, self.theme)
			controls.append(matrix.toXML())
			#background = Background(self.theme)
			#controls.append(background)
		window.append(controls)
		# </window>
		return window



class Window2:
	class UnqlockedWindow(xbmcgui.WindowXMLDialog):
		class ExitMonitor(xbmc.Monitor):
			def __init__(self, exit_callback):
				self.exit_callback = exit_callback
			
			def onScreensaverDeactivated(self):
				log('Invoking exit_callback')
				self.exit_callback()
		
		# Class UnqlockedWindow
		def onInit(self):
			log('Window Initalized!')
			self.monitor = self.ExitMonitor(self.exit)
		
		def onAction(self, action):
			actionID = action.getId()
			if (actionID in (ACTION_PREVIOUS_MENU, ACTION_NAV_BACK, ACTION_PARENT_DIR)):
				self.close()
		
		def exit(self):
			log('Exit requested')
			self.close()
	
	# Class WindowGUI
	def __init__(self, config, layout, theme):
		self.window = self.UnqlockedWindow('script-unqlocked.xml', config.cwd, 'Default')
	
	def show(self):
		self.window.doModal()

