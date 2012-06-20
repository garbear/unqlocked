from unqlocked import log, WINDOW_ID
import elementtree.ElementTree as ElementTree
import xbmc, xbmcgui


ACTION_PARENT_DIR = 9
ACTION_PREVIOUS_MENU = 10
ACTION_NAV_BACK = 92


class MatrixGUI:
	def __init__(self, solution, settings):
		pass

class SpritesGUI:
	def __init__(self, settings):
		pass


PROPERTY_ACTIVE = 'Unqlocked.%i.Highlight'
PROPERTY_INACTIVE = 'Unqlocked.%i.Background'

class Letter:
	def __init__(self, letter, index):
		self.letter = letter
		self.index = index
	
	def toXML(self):
		'''Generate the xml representation of this Letter'''
		# <item>
		item = ElementTree.Element('item')
		if True:
			# <label>$INFO[Window(Home).Property(Unqlocked.0.Background)]</label>
			label = ElementTree.SubElement(item, 'label')
			label.text = '$INFO[Window(Home).Property(%s)]' % (PROPERTY_INACTIVE % self.index)
			# <label2>$INFO[Window(Home).Property(Unqlocked.0.Highlight)]</label2>
			label2 = ElementTree.SubElement(item, 'label2')
			label2.text = '$INFO[Window(Home).Property(%s)]' % (PROPERTY_ACTIVE % self.index)
			# <onclick>-</onclick>
			onclick = ElementTree.SubElement(item, 'onclick')
			onclick.text = '-'
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
		control = ElementTree.Element('control', type='panel')
		if True:
			# <posx>
			posx = ElementTree.SubElement(control, 'posx')
			posx.text = str(self.posx)
			# <posy>
			posy = ElementTree.SubElement(control, 'posy')
			posy.text = str(self.posy)
			# <width>
			width = ElementTree.SubElement(control, 'width')
			width.text = str(self.width)
			# <height>
			height = ElementTree.SubElement(control, 'height')
			height.text = str(self.height)
			# <onleft>-</onleft>
			onleft = ElementTree.SubElement(control, 'onleft')
			onleft.text = '-'
			# <onright>-</onright>
			onright = ElementTree.SubElement(control, 'onright')
			onright.text = '-'
			# <onup>-</onup>
			onup = ElementTree.SubElement(control, 'onup')
			onup.text = '-'
			# <ondown>-</ondown>
			ondown = ElementTree.SubElement(control, 'ondown')
			ondown.text = '-'
			# <viewtype label="">panel</viewtype>
			viewtype = ElementTree.SubElement(control, 'viewtype', label='')
			viewtype.text = 'panel'
			# <pagecontrol>-</pagecontrol>
			pagecontrol = ElementTree.SubElement(control, 'pagecontrol')
			pagecontrol.text = '-'
			# <scrolltime>-</scrolltime>
			scrolltime = ElementTree.SubElement(control, 'scrolltime')
			scrolltime.text = '-'
			# <hitrect x="-10" y="-10" w="1" h="1" />
			hitrect = ElementTree.SubElement(control, 'hitrect', x=str(-10), y=str(-10), w=str(1), h=str(1))
			# <itemlayout>
			itemlayout = ElementTree.SubElement(control, 'itemlayout', height=str(self.height), width=str(self.width))
			if True:
				# <control type="label">
				subControl = ElementTree.SubElement(itemlayout, 'control', type='label')
				if True:
					# <posx>
					posx = ElementTree.SubElement(subControl, 'posx')
					posx.text = str(10)
					# <posy>
					posy = ElementTree.SubElement(subControl, 'posy')
					posy.text = str(0)
					# <width>
					width = ElementTree.SubElement(subControl, 'width')
					width.text = str(self.letterWidth)
					# <height>
					height = ElementTree.SubElement(subControl, 'height')
					height.text = str(self.letterHeight)
					# <font>
					font = ElementTree.SubElement(subControl, 'font')
					#font.text = self.theme.font
					font.text = 'font-22'
					# <textcolor>
					textcolor = ElementTree.SubElement(subControl, 'textcolor')
					textcolor.text = self.theme.inactive
					# <selectedcolor>
					selectedcolor = ElementTree.SubElement(subControl, 'selectedcolor')
					selectedcolor.text = self.theme.inactive
					# <align>center</align>
					align = ElementTree.SubElement(subControl, 'align')
					align.text = 'center'
					# <aligny>center</aligny>
					aligny = ElementTree.SubElement(subControl, 'aligny')
					aligny.text = 'center'
					# <label>[B]$INFO[ListItem.Label][/B]</label>
					label = ElementTree.SubElement(subControl, 'label')
					label.text = '[B]$INFO[ListItem.Label][/B]'
				# </control>
				# <control type="label">
				subControl = ElementTree.SubElement(itemlayout, 'control', type='label')
				if True:
					# <posx>
					posx = ElementTree.SubElement(subControl, 'posx')
					posx.text = str(10)
					# <posy>
					posy = ElementTree.SubElement(subControl, 'posy')
					posy.text = str(0)
					# <width>
					width = ElementTree.SubElement(subControl, 'width')
					width.text = str(self.letterWidth)
					# <height>
					height = ElementTree.SubElement(subControl, 'height')
					height.text = str(self.letterHeight)
					# <font>
					font = ElementTree.SubElement(subControl, 'font')
					#font.text = self.theme.font
					font.text = 'font-22'
					# <textcolor>
					textcolor = ElementTree.SubElement(subControl, 'textcolor')
					textcolor.text = self.theme.active
					# <selectedcolor>
					selectedcolor = ElementTree.SubElement(subControl, 'selectedcolor')
					selectedcolor.text = self.theme.active
					# <align>center</align>
					align = ElementTree.SubElement(subControl, 'align')
					align.text = 'center'
					# <aligny>center</aligny>
					aligny = ElementTree.SubElement(subControl, 'aligny')
					aligny.text = 'center'
					# <label>[B]$INFO[ListItem.Label][/B]</label>
					label = ElementTree.SubElement(subControl, 'label')
					label.text = '[B]$INFO[ListItem.Label][/B]'
				# </control>
			# </itemlayout
			# <focusedlayout height="35" width="35"/>
			focusedlayout = ElementTree.SubElement(control, 'focusedlayout', height=str(self.height), width=str(self.width))
			# <content>
			content = ElementTree.SubElement(control, 'content')
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
		control = ElementTree.Element('control', type='image')
		if True:
			# <posx>
			posx = ElementTree.SubElement(control, 'posx')
			posx.text = str(428)
			# <posy>
			posy = ElementTree.SubElement(control, 'posy')
			posy.text = str(165)
			# <width>
			width = ElementTree.SubElement(control, 'width')
			width.text = str(425)
			# <height>
			height = ElementTree.SubElement(control, 'height')
			height.text = str(390)
			# <texture border="10"></texture>
			texture = ElementTree.SubElement(control, 'texture', border=str(10))
			texture.text = 'qlock.png'
		# </control>
		return control


class Window:
	def __init__(self, layout, theme):
		self.letters = [Letter('A', 0), Letter('B', 1), Letter('C', 2)]
		self.layout = layout
		self.theme = theme
	
	def toXML(self):
		# <window id="3000">
		window = ElementTree.Element('window')
		window.attrib['id'] = str(3000)
		if True:
			# <controls>
			controls = ElementTree.Element('controls')
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

