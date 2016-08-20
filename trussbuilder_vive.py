﻿"""
[ Objective ]----------------------------Order truss members required to build a 20m bridge across the Singapore River

[ Controls ]

[ General ]
[ JOYBUTTON2 ]---------------------Toggle Main Menu
[ MIDDLE MOUSE CLICK ]---------Toggle Utility Menu
[ JOYCURSOR LEFT/RIGHT ]-----Cycle between menu tabs
[ ESC KEY ]----------------------------Close Menu / Quit Application

[ Movement ]
[ VR HEADSET ]----------------------Look around
[ JOYSTICK ]--------------------------Navigate
[ JOYBUTTON 5/3 ]-----------------Lower/Raise elevation

[ Build | Edit ]
[ JOYBUTTON6 ]---------------------Cycle between Edit and Build Modes
[ JOYBUTTON4 ]---------------------Cycle between Side, Top, and Bottom Orientations
[ JOYCURSOR UP/DOWN]---------Slide bridge away or towards in Top or Bottom Orientation
[ VIRTUAL MOUSE ]-----------------Interact with menu elements
[ LEFT MOUSE CLICK ]--------------Create new truss in Build Mode | Grab and move truss in Edit Mode
[ LEFT MOUSE HOLD ]--------------Hold onto white spherical connectors to rotate truss
[ MIDDLE MOUSE CLICK ]----------Rotate grabbed truss member in 45 degree intervals
[ RIGHT MOUSE CLICK ]------------Delete grabbed truss member
[ SCROLL WHEEL ]-------------------Extend and retract virtual hand
"""

#--UTF-8 Encoding
# -*- coding: utf-8 -*-

INVENTORY_TEXT = """Order truss members from the catalogue & manage your inventory"""

FEEDBACK_MESSAGE = """<FEEDBACK>"""

INITIAL_MESSAGE = """[ To begin building, switch to Build Mode ]
[ JOYBUTTON6 ]"""

VIEW_MESSAGE = """[  JOYBUTTON2  ] Toggle Main Menu
[ JOYHATDOWN | JOYHATUP ] Slide bridge towards or away"""
SIDE_VIEW_MESSAGE = """[  JOYBUTTON2  ] Toggle Main Menu
[  JOYBUTTON4  ] Cycle between side, top, and bottom""" 
MODE_MESSAGE = """<MODE>"""

LOAD_MESSAGE = """Any unsaved progress will be lost! 
Are you sure you want to proceed?
(Please remove headset if proceeding)"""

CLEAR_MESSAGE = """The current bridge will be wiped! 
Are you sure you want to proceed?"""

QUIT_MESSAGE = """Any unsaved progress will be lost! 
Are you sure you want to proceed?"""

# Imports
import viz
import vizact
import vizcam
import vizconnect
import vizdlg
import vizfx
import vizfx.postprocess
from vizfx.postprocess.color import GrayscaleEffect
from vizfx.postprocess.composite import BlendEffect
import vizinfo
import vizinput
import vizmenu
import vizproximity
import vizshape
import viztask
import csv
import inventory
import mathlite
import navigation
import panels
import roots
import structures
import sys
import themes
import tools
from tools import highlighter
import xml.etree.ElementTree as ET

# Globals
RESOLUTION = ([1280,720])
UTILITY_CANVAS_RES = ([80,80])
MULTISAMPLING = 8
FOV = 35
START_FOV = 100
STENCIL = 8
STEREOMODE = viz.STEREO_HORZ
FULLSCREEN = viz.FULLSCREEN
CLEAR_COLOR = viz.GRAY
GRID_COLOR = viz.BLACK
BUTTON_SCALE = 0.5
INITIALIZED = False
SOUNDS = []
SFX_VOLUME = 0.5
WARNING_VOLUME = 0.05
ISMUTED = False

BUILD_ROAM_LIMIT = ([12,-12,-10,10])	# Front,back,left,right limits in meters(m)
START_POS = ([0,5,-17])					# Set at 5m + avatar height above ground and 17m back fron center
BUILD_ROTATION = ([0,0,0])				# Zero-rotation to face dead center
WALK_POS = ([21,5.5,-7])
WALK_ROT = ([-60,0,0])
VIEW_SPOTS = {
	 0	: [[-15,12,-13],[50,0,0]]
	,1	: [[15,12,-13],[-40,0,0]]
	,2	: [[-12,10,6],[130,0,0]]
	,3	: [[0,11,14],[180,0,0]]
}

MENU_RES = ([1000,750])
MENU_POS = ([0,18,-8])
INSPECTOR_POS_OFFSET = ( [0,0,2] )
INSPECTOR_ROT_OFFSET = ( [] )
HEADER_TEXT = 'Truss Bridge Builder & Visualiser'
INVENTORY_MESSAGE = 'Order truss members from the catalogue and manage'
DESIGNERS_TEXT = '   Dave\n   Tracy'
PROGRAMMERS_TEXT = '   Justin'
ARTISTS_TEXT = '   Rakesh\n   Jason\n   Anas'

LEN_MIN = 0.1				# Min length allowed for truss
LEN_MAX = 20.0				# Max length allowed for truss
QTY_MIN = 1					# Min quantity allowed for truss
QTY_MAX = 20				# Max quantity allowed for truss

GRIDS = []

ORDERS = []
ORDERS_SIDE = inventory.OrderList()
ORDERS_TOP = inventory.OrderList()
ORDERS_BOT = inventory.OrderList()
ROWS = []
ORDERS_SIDE_ROWS = []
ORDERS_TOP_ROWS = []
ORDERS_BOT_ROWS = []
ORDERS_SIDE_FLAG = 'Side'
ORDERS_TOP_FLAG = 'Top'
ORDERS_BOT_FLAG = 'Bot'

BUILD_MEMBERS = []				# Array to store all truss members of bridge for saving/loading
SIDE_MEMBERS = []				# Array to store Side truss
SIDE_CLONES = []				# Array to store cloned Side truss
TOP_MEMBERS = []				# Array to store Top truss
BOT_MEMBERS = []				# Array to store Bottom truss
GRAB_LINKS = []					# Array to store grab links between bridge root and truss members

BRIDGE_LENGTH = 20				# Length of bridge in meters
BRIDGE_SPAN = 10				# Span of bridge in meters
GRID_Z = -5						# Grid z-position for Build members to snap to
BRIDGE_ROOT_POS = [0,5,0]		# Origin point of bridge group to position and rotate
TOP_VIEW_POS = [0,5,-4]			# Position of Top View Bridge Root
BOT_VIEW_POS = [0,5,-5]			# Position of bottom view bridge root
SIDE_VIEW_ROT = [0,0,0]			# Rotation of Side View
TOP_VIEW_ROT = [0,-90,0]		# Rotation of Top View
BOT_VIEW_ROT = [0,90,0]			# Rotation of Bottom View
TOP_CACHED_Z = -4				# Cache z-position of Top Bridge View
TOP_Z_MIN = -4					# Minimum z-position of Top Bridge Root
BOT_CACHED_Z = -5				# Cache z-position of Bot Bridge View
BOT_Z_MIN = -5					# Minimum z-position of Bottom Bridge Root
SLIDE_MAX = 100					# Max z-position of bridge root sliding
SLIDE_INTERVAL = 0.05			# Interval to slide bridge root in TOP/BOTTOM View
SUPPORT_ALPHA = 0.25			# Alpha value for bridge red supports	
INACTIVE_ALPHA = 0.25			# Alpha value for inactive truss members
ORIENTATION = structures.Orientation.Side
MODE = structures.Mode.View

PROXY_NODES = []
TARGET_NODES = []
SENSOR_NODES = []

PRE_SNAP_POS = []
PRE_SNAP_ROT = []
SNAP_TO_POS = []
VALID_SNAP = False

SHOW_HIGHLIGHTER = False
HAND_DISTANCE = 2.5
SCROLL_MIN = 0.2
SCROLL_MAX = 20

CACHED_GLOVE_Z = 0

OPTIONS_BUTTON_LENGTH = 1.75

DEBUG_PROXIMITY = True
DEBUG_CAMBOUNDS = False

# Setup key commands
KEYS = { 'forward'	: 'w'
		,'FORWARD'	: 'W'
		,'back'		: 's'
		,'left'		: 'a'
		,'right'	: 'd'	
		,'reset'	: 'r'
		,'restart'	: viz.KEY_END
		,'home'		: viz.KEY_HOME
		,'builder'	: 'b'
		,'viewer'	: 'v'
		,'env'		: 't'
		,'grid'		: 'g'
		,'hand'		: 'h'
		,'showMenu' : ' '
		,'snapMenu'	: viz.KEY_CONTROL_L
		,'interact' : viz.MOUSEBUTTON_LEFT
		,'utility'	: viz.MOUSEBUTTON_MIDDLE
		,'rotate'	: viz.MOUSEBUTTON_RIGHT
		,'orient'	: viz.KEY_TAB
		,'mode'		: viz.KEY_SHIFT_L
		,'angles'	: ';'
		,'road'		: 'n'
		,'proxi'	: 'p'
		,'collide'	: 'c'
		,'walk'		: '/'
		,'esc'		: viz.KEY_ESCAPE
		,'viewMode' : 'm'
		,'capslock'	: viz.KEY_CAPS_LOCK
		,'slideFar'	: '2'
		,'slideNear': '1'
}

# Initialize scene
def initScene(res=RESOLUTION,quality=4,fov=FOV,stencil=8,stereoMode=viz.STEREO_HORZ,fullscreen=viz.FULLSCREEN,clearColor=viz.BLACK):
	viz.setOption('viz.splashscreen', './resources/splash/splash.jpg')
	viz.window.setSize(res)
	viz.setMultiSample(quality)
	viz.fov(fov)
	viz.setOption('viz.display.stencil', stencil)
	viz.setOption('viz.default_key.quit', 0)
	viz.setOption('viz.dwm_composition',viz.OFF)
	viz.setOption('viz.model.optimize', 1)
	viz.setOption('viz.publish.allow_capture_video', 1)	# Allow capturing videos in published EXE 
	viz.window.setName( 'Virtual Truss Bridge Builder & Visualiser' ) 
	viz.window.setBorder( viz.BORDER_FIXED )
	viz.clearcolor(clearColor)
	darkTheme = themes.getDarkTheme()
	viz.setTheme(darkTheme)	
	viz.go(fullscreen)
	
	
# Disable mouse navigation and hide the mouse cursor
def initMouse():
#	viz.mouse(viz.OFF)
	viz.mouse.setVisible(viz.OFF)
	viz.mouse.setTrap()
	viz.mouse.setOverride() 
	
	
def initProxy():
	"""Initialize proximity manager and register callbacks"""
	# Create proximity manager
	proxyManager = vizproximity.Manager()
	proxyManager.setDebug(DEBUG_PROXIMITY)
	
	# Register callbacks for proximity SENSOR_NODES
	def enterProximity(e):
		global SENSOR_NODE
		global SNAP_TO_POS
		global VALID_SNAP
		SENSOR_NODE = e.sensor.getSource()
		SNAP_TO_POS = e.sensor.getSource().getPosition()
		VALID_SNAP = True
		print 'EnterProximity: SNAP_TO_POS',SNAP_TO_POS
	
	def exitProximity(e):
		global SENSOR_NODE
		global VALID_SNAP
		SENSOR_NODE = None
		VALID_SNAP = False

	proxyManager.onEnter(None, enterProximity)
	proxyManager.onExit(None, exitProximity)
	
	return proxyManager
	
	
def initTracker(distance=0.5):
	"""Initialize scroll wheel tracker"""
	from vizconnect.util import virtual_trackers
	tracker = virtual_trackers.ScrollWheel(followMouse=True)
	tracker.distance = distance
	return tracker


def initLink(modelPath,tracker):
	"""Initialize hand link with tracker and link group with main view"""
	model = viz.addChild(modelPath)
	link = viz.link(tracker,model)
#	link.postMultLinkable(viz.MainView)
	return link
	
	
def initLighting():
	# Disable the head lamps since we're doing lighting ourselves
	for window in viz.getWindowList():
		window.getView().getHeadLight().disable()
	# Create directional light
	sky_light = vizfx.addDirectionalLight(euler=(30,45,0),color=[0.8,0.8,0.8])
#	sky_light2 = vizfx.addDirectionalLight(euler=(-30,45,0),color=[0.8,0.8,0.8])	
#	light1 = vizfx.addDirectionalLight(euler=(40,20,0), color=[0.7,0.7,0.7])
#	light2 = vizfx.addDirectionalLight(euler=(-65,15,0), color=[0.5,0.25,0.0])
#	sky_light.color(viz.WHITE)
	# Adjust ambient color
#	viz.setOption('viz.lightModel.ambient',[0]*3)
#	sky_light.ambient([0.8]*3)
#	sky_light2.ambient([0.8]*3)
#	vizfx.setAmbientColor([0.3,0.3,0.4])

def getCatalogue(path):
	"""Parse catalogue from data subdirectory"""
	return ET.parse(str(path)).getroot()

# Initialize
initScene(RESOLUTION,MULTISAMPLING,FOV,STENCIL,STEREOMODE,FULLSCREEN,(0.1, 0.1, 0.1, 1.0))
initMouse()
initLighting()
highlightTool = highlighter.Highlighter()
proxyManager = initProxy()
catalogue_root = getCatalogue('data/catalogues/catalogue_CHS.xml')
environment_root = roots.EnvironmentRoot()
environment_root.visible(False)
environment_root.setWaveAnimationSpeed(0.01);
bridge_root = roots.Root()
bridge_root.getGroup().setPosition(BRIDGE_ROOT_POS)
bridge_root.getGroup().setEuler(SIDE_VIEW_ROT)
grid_root = roots.GridRoot(GRID_COLOR)
info_root = roots.InfoRoot()

# Setup audio
startSound = viz.addAudio('./resources/sounds/return_to_holodeck.wav')
buttonHighlightSound = viz.addAudio('./resources/sounds/button_highlight.wav')
clickSound = viz.addAudio('./resources/sounds/click.wav')
showMenuSound = viz.addAudio('./resources/sounds/show_menu.wav')
hideMenuSound = viz.addAudio('./resources/sounds/hide_menu.wav')
viewChangeSound = viz.addAudio('./resources/sounds/page_advance.wav')
warningSound = viz.addAudio('./resources/sounds/out_of_bounds_warning.wav')

SOUNDS = [ startSound,buttonHighlightSound,clickSound,showMenuSound,
			hideMenuSound,viewChangeSound,warningSound ]

# Set volume
for sound in SOUNDS:
	sound.volume(SFX_VOLUME)
warningSound.volume(WARNING_VOLUME)


def updateResolution(panel,canvas):
	bb = panel.getBoundingBox()
	canvas.setRenderWorldOverlay([bb.width + 5, bb.height + 5], fov=bb.height * 0.15, distance=3.0)	
	canvas.setCursorPosition([0.5,0.5])


def updateMouseStyle(canvas):
	canvas.setMouseStyle(viz.CANVAS_MOUSE_BUTTON)


# Add environment effects
env = viz.addEnvironmentMap('resources/textures/sky.jpg')
#effect = vizfx.addAmbientCubeEffect(env)
#vizfx.getComposer().addEffect(effect)
#lightEffect = vizfx.addLightingModel(diffuse=vizfx.DIFFUSE_LAMBERT,specular=None)
#vizfx.getComposer().addEffect(lightEffect)


def applyEnvironmentEffect(obj):
	obj.texture(env)
	obj.appearance(viz.ENVIRONMENT_MAP)	

#--Create middle road
#road = vizfx.addChild('resources/road.osgb',pos=(0,5.25,0),parent=environment_root.getGroup())
road = vizfx.addChild('resources/road.osgb',pos=(0,0.25,0),parent=environment_root.getGroup())
#road.visible(False)
#applyEnvironmentEffect(road)


# Bridge pin and roller supports
pinSupport = viz.addChild('resources/support_pin.osgb',pos=(-9.5,4,0),scale=[1,1,11])
rollerSupport = viz.addChild('resources/support_roller.osgb',pos=(9.5,4,0),scale=[1,1,11])
supports = [pinSupport,rollerSupport]

#Setup anchor points for truss members
pinAnchorSphere = vizshape.addSphere(0.2,pos=([-BRIDGE_SPAN,BRIDGE_ROOT_POS[1],-(BRIDGE_SPAN*0.5)]))
pinAnchorSphere.visible(False)
pinLink = viz.link(pinAnchorSphere,viz.NullLinkable)
pinAnchorSensor = vizproximity.Sensor(vizproximity.Sphere(0.3,center=[0,0.1,0]),pinLink)
proxyManager.addSensor(pinAnchorSensor)
viz.grab(pinSupport,pinAnchorSphere)

rollerAnchorSphere = vizshape.addSphere(0.2,pos=([BRIDGE_SPAN,BRIDGE_ROOT_POS[1],-(BRIDGE_SPAN*0.5)]))
rollerAnchorSphere.visible(False)
rollerLink = viz.link(rollerAnchorSphere,viz.NullLinkable)
rollerAnchorSensor = vizproximity.Sensor(vizproximity.Sphere(0.3,center=[0,0.1,0]), rollerLink)
proxyManager.addSensor(rollerAnchorSensor)
viz.grab(rollerSupport,rollerAnchorSphere)

for model in supports:
	viz.grab(bridge_root.getGroup(),model)

# Create canvas for displaying GUI objects
instructionsPanel = vizinfo.InfoPanel(title=HEADER_TEXT,align=viz.ALIGN_CENTER_BASE,icon=False,key=None)
instructionsPanel.getTitleBar().fontSize(36)

# Initialize order panel containing mainRow and midRow
#inventoryPanel = vizdlg.Panel(layout=vizdlg.LAYOUT_VERT_CENTER,align=viz.ALIGN_CENTER,spacing=0,margin=(0,0))
inventoryPanel = vizinfo.InfoPanel(title=HEADER_TEXT,text=INVENTORY_TEXT,align=viz.ALIGN_CENTER_TOP,icon=False,key=None)
inventoryPanel.getTitleBar().fontSize(36)

# Initialize midRow
inventoryRow = vizdlg.Panel(layout=vizdlg.LAYOUT_HORZ_TOP,border=False,background=False,margin=0)
#inventoryGrid = vizdlg.GridPanel(cellAlign=vizdlg.ALIGN_LEFT_TOP,border=False)

# Initialize orderPanel
orderPanel = vizinfo.InfoPanel('Fill in all required fields',icon=False,key=None)
orderPanel.setTitle( 'Order' )	
orderPanel.getTitleBar().fontSize(28)
orderPanel.addSeparator()
# Initialize type
typeDropList = viz.addDropList()
typeDropList.addItem('CHS', 0)
trussType = orderPanel.addLabelItem('Type', typeDropList)
# Initialize diameterDropList
diameterDropList = viz.addDropList()
for member in catalogue_root.iter('member'):
	diameter = member.get('diameter')
	diameterDropList.addItem(diameter)
diameterDropList.select(19)
diameter = orderPanel.addLabelItem('Diameter (mm)', diameterDropList)
# Initialize thicknessDropList
thicknessDropList = viz.addDropList()
thicknesses = []
for thickness in catalogue_root[diameterDropList.getSelection()]:
	thicknesses.append(thickness.text)
thicknessDropList.addItems(thicknesses)
thicknessDropList.select(2)
thickness = orderPanel.addLabelItem('Thickness (mm)', thicknessDropList)
# Initilize lengthTextbox with default value of 5m
lengthTextbox = viz.addTextbox()
lengthTextbox.message('5')
length = orderPanel.addLabelItem('Length (m)', lengthTextbox)
# Initialize quantitySlider with default value of 1
quantitySlider = viz.addProgressBar('1')
qtyProgressPos = mathlite.getNewRange(1,QTY_MIN,QTY_MAX,0.0,1.0)
quantitySlider.set(qtyProgressPos)
quantity = orderPanel.addLabelItem('Quantity', quantitySlider)
# Initialize ordering buttons
orderSideButton = orderPanel.addItem(viz.addButtonLabel('Add to Side'),align=viz.ALIGN_RIGHT_BOTTOM)
orderTopButton = orderPanel.addItem(viz.addButtonLabel('Add to Top'),align=viz.ALIGN_RIGHT_BOTTOM)
orderBottomButton = orderPanel.addItem(viz.addButtonLabel('Add to Bottom'),align=viz.ALIGN_RIGHT_BOTTOM)

# Initialize Stock Main Panel
stockMainPanel = vizinfo.InfoPanel('Ordered truss members',icon=False,key=None)
stockMainPanel.setTitle( 'Stock' )
stockMainPanel.getTitleBar().fontSize(28)
stockMainPanel.addSeparator()
# Initialize Side order tab
stockPanel = vizdlg.TabPanel()
# Side orders inventory
ORDERS_SIDE_GRID = panels.CreateLabelledPanel()
stockPanel.addPanel('Side',ORDERS_SIDE_GRID)
# Top orders inventory
ORDERS_TOP_GRID = panels.CreateLabelledPanel()
stockPanel.addPanel('Top',ORDERS_TOP_GRID)
# Bottom orders inventory
ORDERS_BOT_GRID = panels.CreateLabelledPanel()
stockPanel.addPanel('Bottom',ORDERS_BOT_GRID)
stockMainPanel.addItem(stockPanel)

inventoryRow.addItem(orderPanel)
inventoryRow.addItem(stockMainPanel)
#inventoryGrid.addRow([orderPanel,stockPanel])

bottomRow = vizdlg.Panel(border=False)
doneButton = bottomRow.addItem(viz.addButtonLabel('Confirm order and start building in VR'))
doneButton.length(2)

# Add rows to inventory main panel
inventoryPanel.addItem(inventoryRow)
inventoryPanel.addItem(bottomRow)

# TAB 3: Options panel
optionPanel = vizinfo.InfoPanel(title=HEADER_TEXT,text='Options',align=viz.ALIGN_CENTER_TOP,icon=False,key=None)
optionPanel.getTitleBar().fontSize(36)
optionPanel.addSection('    [ File ]')
#saveHeader = optionPanel.addItem(viz.addText('    [ Append ".csv" when saving ]'))
saveButton = optionPanel.addItem(viz.addButtonLabel('Save Bridge'),align=viz.ALIGN_CENTER)
saveButton.length(OPTIONS_BUTTON_LENGTH)
loadButton = optionPanel.addItem(viz.addButtonLabel('Load Bridge'),align=viz.ALIGN_CENTER)
loadButton.length(OPTIONS_BUTTON_LENGTH)
optionPanel.addSection('    [ Application ]')
soundButton = optionPanel.addItem(viz.addButtonLabel('Toggle Audio'),align=viz.ALIGN_CENTER)
soundButton.length(OPTIONS_BUTTON_LENGTH)
resetButton = optionPanel.addItem(viz.addButtonLabel('Clear Bridge'),align=viz.ALIGN_CENTER)
resetButton.length(OPTIONS_BUTTON_LENGTH)
quitButton = optionPanel.addItem(viz.addButtonLabel('Quit Application'),align=viz.ALIGN_CENTER)
quitButton.length(OPTIONS_BUTTON_LENGTH)

# TAB 4: Credits panel
creditsPanel = vizinfo.InfoPanel(title=HEADER_TEXT,text='Credits',align=viz.ALIGN_CENTER_TOP,icon=False,key=None)
creditsPanel.getTitleBar().fontSize(36)
creditsPanel.addSection('    [ Design ]')
creditsPanel.addItem(viz.addText(DESIGNERS_TEXT))
creditsPanel.addSection('    [ Programming ]')
creditsPanel.addItem(viz.addText(PROGRAMMERS_TEXT))
creditsPanel.addSection('    [ Art ]')
creditsPanel.addItem(viz.addText(ARTISTS_TEXT))

# Create inspector panel
inspectorCanvas = viz.addGUICanvas(align=viz.ALIGN_CENTER)
inspector = panels.InspectorPanel()
statPanel = inspector.GetPanel()
statPanel.setParent(inspectorCanvas)

# Create docked utility panel
utilityCanvas = viz.addGUICanvas(align=viz.ALIGN_CENTER)
points = mathlite.getPointsInCircum(30,8)
# Menu button
menuButton = viz.addButton(parent=utilityCanvas)
menuButton.texture(viz.addTexture('resources/gui/menu-128.png'))
menuButton.setScale(BUTTON_SCALE,BUTTON_SCALE)
# Reset View button
homeButton = viz.addButton(parent=utilityCanvas)
homeButton.texture(viz.addTexture('resources/gui/reset-128.png'))
homeButton.setScale(BUTTON_SCALE,BUTTON_SCALE)
# Build mode button
buildModeButton = viz.addButton(parent=utilityCanvas)
buildModeButton.texture(viz.addTexture('resources/gui/wrench-128.png'))
buildModeButton.setScale(BUTTON_SCALE,BUTTON_SCALE)
# Viewer mode button
viewerModeButton = viz.addButton(parent=utilityCanvas)
viewerModeButton.texture(viz.addTexture('resources/gui/viewer-128.png'))
viewerModeButton.setScale(BUTTON_SCALE,BUTTON_SCALE)
# Walk mode button
walkModeButton = viz.addButton(parent=utilityCanvas)
walkModeButton.texture(viz.addTexture('resources/gui/walking-128.png'))
walkModeButton.setScale(BUTTON_SCALE,BUTTON_SCALE)
# Toggle environment button
toggleEnvButton = viz.addButton(parent=utilityCanvas)
toggleEnvButton.texture(viz.addTexture('resources/gui/environment-128.png'))
toggleEnvButton.setScale(BUTTON_SCALE,BUTTON_SCALE)
# Toggle grid button
toggleGridButton = viz.addButton(parent=utilityCanvas)
toggleGridButton.texture(viz.addTexture('resources/gui/grid-64.png'))
toggleGridButton.setScale(BUTTON_SCALE,BUTTON_SCALE)
# Reset orientation button
resetOriButton = viz.addButton(parent=utilityCanvas)
resetOriButton.texture(viz.addTexture('resources/gui/compass-128.png'))
resetOriButton.setScale(BUTTON_SCALE,BUTTON_SCALE)

utilityButtons = ( [menuButton,homeButton,buildModeButton,viewerModeButton,walkModeButton,toggleEnvButton,toggleGridButton,resetOriButton] )
for i, button in enumerate(utilityButtons):
	button.setPosition(0.5 + points[i][0], 0.5 + points[i][1])
	
# Link utility canvas with main View
utilityLink = viz.link(viz.MainView,utilityCanvas)
#utilityLink.postMultLinkable(viz.MainView)
utilityLink.preTrans( [0, 0, 3] )


# Rotation Canvas/Panel
rotationCanvas = viz.addGUICanvas(align=viz.ALIGN_CENTER)
rotationPanel = vizdlg.GridPanel(parent=rotationCanvas,align=viz.ALIGN_CENTER,border=False)
rotationSlider = viz.addProgressBar('Angle')
rotationLabel = viz.addText('0')
row = rotationPanel.addRow([rotationSlider,rotationLabel])

# Menu Canvas
menuCanvas = viz.addGUICanvas(align=viz.ALIGN_CENTER_TOP)
controlsQuad = viz.addTexQuad(size=[1024,512],parent=menuCanvas)
controlsPic = viz.addTexture('resources/gui/merged_mapping_truss.png',parent=controlsQuad)
controlsQuad.texture(controlsPic)

# Add tabbed panels to main menu canvas
menuTabPanel = vizdlg.TabPanel(align=viz.ALIGN_CENTER_TOP,parent=menuCanvas)
menuTabPanel.addPanel('Instructions',instructionsPanel)
menuTabPanel.addPanel('Controls',controlsQuad)
menuTabPanel.addPanel('Inventory',inventoryPanel)
menuTabPanel.addPanel('Options',optionPanel)
menuTabPanel.addPanel('Credits',creditsPanel)

# Add dialog canvas
dialogCanvas = viz.addGUICanvas(align=viz.ALIGN_CENTER)
dialog = vizdlg.MessageDialog(message='<Message>', title='Warning', accept='Yes (Enter)', cancel='No (Esc)',parent=dialogCanvas)
dialog.setScreenAlignment(viz.ALIGN_CENTER)
dialogCanvas.visible(viz.OFF)

# Add feedback canvas
feedbackCanvas = viz.addGUICanvas(align=viz.ALIGN_CENTER)
feedbackQuad = viz.addTexQuad(size=[500,100],parent=feedbackCanvas)
blackTex = viz.addTexture('resources/textures/blackTex.bmp',parent=feedbackQuad)
blackTex.wrap(viz.WRAP_S,viz.REPEAT) 
blackTex.wrap(viz.WRAP_T,viz.REPEAT)
feedbackText = viz.addText(FEEDBACK_MESSAGE,parent=feedbackQuad,align=viz.ALIGN_CENTER)
feedbackQuad.texture(blackTex)
feedbackQuad.alpha(0.5) 
feedbackText.color(viz.WHITE)
feedbackText.fontSize(50)
feedbackCanvas.visible(viz.OFF)

def initCanvas():	
	# Set canvas resolution to fit bounds of info panel
	bb = menuTabPanel.getBoundingBox()
	menuCanvas.setRenderWorld([bb.width,bb.height+50],[1,viz.AUTO_COMPUTE])
	menuCanvas.setCursorPosition([0,0])
	menuCanvas.setPosition(0,2.275,1.5)
	menuCanvas.setMouseStyle(viz.CANVAS_MOUSE_VIRTUAL)
	
	updateResolution(dialog,dialogCanvas)
	dialogCanvas.setPosition(0,1.5,3)
	dialogCanvas.setMouseStyle(viz.CANVAS_MOUSE_VIRTUAL)
	
	updateResolution(feedbackQuad,feedbackCanvas)
	feedbackCanvas.setPosition(0,0,6)	
	
#	inspectorCanvas.setRenderWorldOverlay(RESOLUTION,fov=90.0,distance=3.0)
	inspectorCanvas.setRenderWorld(RESOLUTION,[10,viz.AUTO_COMPUTE])
	
	utilityCanvas.setRenderWorld(UTILITY_CANVAS_RES,[1,viz.AUTO_COMPUTE])
	utilityCanvas.setPosition(0,0,0)
	utilityCanvas.setEuler(0,0,0)
	utilityCanvas.setCursorPosition([0,0])
	utilityCanvas.visible(False)
	utilityCanvas.setMouseStyle(viz.CANVAS_MOUSE_VIRTUAL)
	
#	rotationCanvas.setRenderWorld(RESOLUTION,[1,viz.AUTO_COMPUTE])
#	rotationCanvas.setRenderWorldOverlay(MENU_RES,fov=90.0,distance=3.0)
	updateResolution(rotationPanel,rotationCanvas)
	rotationCanvas.setPosition(0,0,0)
	rotationCanvas.setEuler(0,0,0)
	rotationCanvas.visible(False)
initCanvas()

#--Start at inventory tab
#menuTabPanel.selectPanel(2)

def inspectMember(obj):
	if obj is not None:			
		inspector.SetMessage(str(obj.length) + 'm x ' +
								str(obj.diameter) + 'mm x ' +
								str(obj.thickness) + 'mm x at ' +
								str(int(obj.getEuler()[2])) + '°')
		inspectorCanvas.visible(True)
	else:
		inspectorCanvas.visible(False)

def showFeedback():
	while True:
		feedbackCanvas.runAction(vizact.fadeTo(.5,begin=0,time=0.5))
		feedbackText.runAction(vizact.fadeTo(1,begin=0,time=0.5))
		yield viztask.waitTime(1)
		feedbackCanvas.runAction(vizact.fadeTo(0,begin=.5,time=0.25))
		feedbackText.runAction(vizact.fadeTo(0,begin=1,time=0.25))
		break


task = viztask.schedule( showFeedback() )
def runFeedbackTask(message='Welcome'):
	global task
	task.kill()
	
	feedbackCanvas.alpha(0)
	feedbackText.alpha(0)
	feedbackText.message(message)
	feedbackCanvas.visible(viz.ON)
	task = viztask.schedule( showFeedback() )
	

def showdialog(message,func):
	menuCanvas.setMouseStyle(viz.CANVAS_MOUSE_VISIBLE)
	inventoryCanvas.setMouseStyle(viz.CANVAS_MOUSE_VISIBLE)
	
	global dialog
	dialog.remove()
	# Re-adjust resolution	
	dialog = vizdlg.MessageDialog(message=message, title='Warning', accept='Yes (Enter)', cancel='No (Esc)',parent=dialogCanvas)
	dialog.setScreenAlignment(viz.ALIGN_CENTER)
	
#	updateResolution(dialog,dialogCanvas)
	bb = dialog.getBoundingBox()
	dialogCanvas.setRenderWorld([bb.width + 5, bb.height + 5], [1,viz.AUTO_COMPUTE])	
	dialogCanvas.visible(viz.ON)
	
	warningSound.play()
	
	while True:
		yield dialog.show()
		if dialog.accepted:
			func()
		else:
			pass
		dialog.remove()
		dialogCanvas.visible(viz.OFF)
		
		menuCanvas.setMouseStyle(viz.CANVAS_MOUSE_VIRTUAL)
		if MODE is structures.Mode.Build:
			inventoryCanvas.setMouseStyle(viz.CANVAS_MOUSE_VIRTUAL)
		
def clearBridge():
	viztask.schedule(showdialog(CLEAR_MESSAGE,clearMembers))

def quitGame():
	viztask.schedule(showdialog(QUIT_MESSAGE,viz.quit))
	
def loadBridge():
	clickSound.play()
	viztask.schedule(showdialog(LOAD_MESSAGE,LoadData))
	
class Order(object):
	'Base class for all ORDERS'
	orderCount = 0
	
	def __init__(self,type='CHS',diameter=508,thickness=16,length=4,quantity=1):
		self.type = type
		self.diameter = diameter
		self.thickness = thickness
		self.length = length
		self.quantity = quantity
		Order.orderCount += 1		
		
	def __repr__(self):
		return repr((self.diameter, self.thickness, self.length, self.quantity))

	def __del__(self):
		class_name = self.__class__.__name__
		
	def __add__(self,other):
		return Order(self.type,self.diameter,self.thickness,self.length,self.quantity+other.quantity)
		
	def displayCount(self):
		print "Total ORDERS %d" % Order.orderCount
		
	def displayOrder(self):
		print "Type: ", self.type, ", Diameter: ", self.diameter, ", Thickness: ", self.thickness, " Length: ", self.length, " Quantity: ", self.quantity
		
def addOrder(orderTab,orderList=inventory.OrderList(),orderRow=[],flag=''):
	"""
	adds new truss member order
	"""	
	newOrder = Order()
	
	_diameter = diameterDropList.getItem(diameterDropList.getSelection())
	_thickness = thicknessDropList.getItem(thicknessDropList.getSelection())
	try:
		_length = viz.clamp(float(lengthTextbox.get()),LEN_MIN,LEN_MAX)
		_length = round(_length,2)
	except:
		runFeedbackTask('Invalid length!')
		warningSound.play()
		lengthTextbox.message('')
		return
	_quantity = mathlite.getNewRange(quantitySlider.get(),0.0,1.0,QTY_MIN,QTY_MAX)
	
	setattr(newOrder, 'diameter', float(_diameter))
	setattr(newOrder, 'thickness', float(_thickness))
	setattr(newOrder, 'length', float(_length))
	setattr(newOrder, 'quantity', int(_quantity))

	global ORDERS_SIDE
	global ORDERS_TOP
	global ORDERS_BOT

	if flag == ORDERS_SIDE_FLAG:
		orderList = inventory.OrderList(ORDERS_SIDE)
	elif flag == ORDERS_TOP_FLAG:
		orderList = inventory.OrderList(ORDERS_TOP)
	elif flag == ORDERS_BOT_FLAG:
		orderList = inventory.OrderList(ORDERS_BOT)	
	
	#Check for existing order
	append = True
	if len(orderList) < 1:
		orderList.append(newOrder)
		append = False
	else:	
		for order in orderList:
			_d = order.diameter
			_t = order.thickness
			_l = order.length
			_q = order.quantity
					
			if newOrder.diameter == _d and newOrder.thickness == _t and newOrder.length == _l:
				order.quantity += newOrder.quantity
				if(order.quantity > 99):
					setattr(order, 'quantity', 99)
				append = False
	
	if append == True:	
		orderList.append(newOrder)
	
	#Clear grid
	for row in orderRow:
		orderTab.removeRow(row)
	
	#Sort lowest to highest (d x Th x l)
	orderList = orderList.sortByAttr()

	# Change global list based on order flag
	if flag == ORDERS_SIDE_FLAG:
		ORDERS_SIDE = orderList
	elif flag == ORDERS_TOP_FLAG:
		ORDERS_TOP = orderList
	elif flag == ORDERS_BOT_FLAG:
		ORDERS_BOT = orderList
	
	#Populate grid with ORDERS in order list
	for _order in orderList:
		__d = viz.addText(str(_order.diameter))
		__t = viz.addText(str(_order.thickness))
		__l = viz.addText(str(_order.length))
		__q = viz.addText(str(_order.quantity))
		deleteButton = viz.addButtonLabel('X')
		_index = orderList.index(_order)
		_row = orderTab.addRow( [__d,__t,__l,__q,deleteButton] )
		vizact.onbuttonup ( deleteButton, deleteOrder, _order, orderList, _index, _row, orderRow, orderTab, flag )
		orderRow.append(_row)


def deleteOrder(order, orderList, index, row, orderRow, orderTab, flag ):	
#	orderList.pop(index)
	viz.logNotice('Deleting', order)
	orderList.remove(order)
	orderTab.removeRow(row)
	orderRow.remove(row)		
	
	
def createInventory():
#	Create inventory panel
	global inventoryCanvas
	inventoryCanvas = viz.addGUICanvas(align=viz.ALIGN_CENTER_TOP)
	
	global inventoryGrid
	inventoryGrid = vizdlg.GridPanel(align=viz.ALIGN_CENTER_TOP,cellAlign=vizdlg.LAYOUT_HORZ_TOP,parent=inventoryCanvas,border=False,background=False)
	
	global inventoryTabPanel
	inventoryTabPanel = vizdlg.TabPanel(align=viz.ALIGN_CENTER_TOP,layout=vizdlg.LAYOUT_VERT_LEFT,parent=inventoryCanvas,border=False)

	# Side truss inventory
	global sideInventory
	sideInventory = vizdlg.GridPanel(cellAlign=vizdlg.ALIGN_CENTER_TOP,border=False,spacing=0,padding=1,background=False,margin=0)
	sideInventory.layout = vizdlg.LAYOUT_VERT_LEFT
	
	global sidePanel
	sidePanel = inventoryTabPanel.addPanel('Side',sideInventory)
	
	global sideRows
	sideRows = []
	
	# Top truss inventory
	global topInventory
	topInventory = vizdlg.GridPanel(cellAlign=vizdlg.ALIGN_CENTER_TOP,border=False,spacing=0,padding=1,background=False,margin=0)
	topInventory.layout = vizdlg.LAYOUT_VERT_LEFT
	
	global topPanel
	topPanel = inventoryTabPanel.addPanel('Top',topInventory)
	
	global topRows
	topRows = []
	
	# Bottom truss inventory
	global bottomInventory
	bottomInventory = vizdlg.GridPanel(cellAlign=vizdlg.ALIGN_CENTER_TOP,border=False,spacing=0,padding=1,background=False,margin=0)
	bottomInventory.layout = vizdlg.LAYOUT_VERT_LEFT
	
	global bottomPanel
	bottomPanel = inventoryTabPanel.addPanel('Bottom',bottomInventory)

	global bottomRows
	bottomRows = []

#	inventoryGrid.addRow([statPanel])
	inventoryGrid.addRow([inventoryTabPanel])

	bb = inventoryGrid.getBoundingBox()
	inventoryCanvas.setRenderWorld([bb.width*.95,bb.height*.95],[1,viz.AUTO_COMPUTE])
	inventoryCanvas.setMouseStyle(viz.CANVAS_MOUSE_VIRTUAL)
createInventory()


def clearInventory():
	global sideRows
	global topRows
	global bottomRows
	
	for row in sideRows:
		sideInventory.removeRow(row)
	for row in topRows:
		topInventory.removeRow(row)
	for row in bottomRows:
		bottomInventory.removeRow(row)
		
	sideRows = []
	topRows = []
	bottomRows = []
	

def populateInventory():
	clearInventory()
	
	# Generate truss buttons based on respective lists
	global ORDERS_SIDE
	for sideOrder in ORDERS_SIDE:
		msg = '{}m(l) x {}mm(d) x {}mm(th) [{}]'.format ( sideOrder.length, sideOrder.diameter, sideOrder.thickness, sideOrder.quantity )
		sideButton = viz.addButtonLabel ( msg )
		vizact.onbuttonup ( sideButton, createTrussNew, sideOrder, 'resources/chs.osgb' )
		row = sideInventory.addRow ( [sideButton] )
		sideRows.append ( row )
		vizact.onbuttonup ( sideButton, updateQuantity, sideOrder, sideButton, ORDERS_SIDE, sideInventory, row )
		vizact.onbuttonup ( sideButton, clickSound.play )
	global ORDERS_TOP
	for topOrder in ORDERS_TOP:
		msg = '{}m(l) x {}mm(d) x {}mm(th) [{}]'.format ( topOrder.length, topOrder.diameter, topOrder.thickness, topOrder.quantity )
		topButton = viz.addButtonLabel ( msg )
		vizact.onbuttonup ( topButton, createTrussNew, topOrder, 'resources/chs.osgb' )
		row = topInventory.addRow( [topButton] )
		topRows.append ( row )
		vizact.onbuttonup ( topButton, updateQuantity, topOrder, topButton, ORDERS_TOP, topInventory, row )
		vizact.onbuttonup ( topButton, clickSound.play )
	global ORDERS_BOT
	for botOrder in ORDERS_BOT:
		msg = '{}m(l) x {}mm(d) x {}mm(th) [{}]'.format ( botOrder.length, botOrder.diameter, botOrder.thickness,  botOrder.quantity )
		botButton = viz.addButtonLabel ( msg )
		vizact.onbuttonup ( botButton, createTrussNew, botOrder, 'resources/chs.osgb' )
		row = bottomInventory.addRow ( [botButton] )
		bottomRows.append ( row )
		vizact.onbuttonup ( botButton, updateQuantity, botOrder, botButton, ORDERS_BOT, bottomInventory, row )
		vizact.onbuttonup ( botButton, clickSound.play )
		
	# Clear order panel rows
	for topRow in ORDERS_TOP_ROWS:
		ORDERS_TOP_GRID.removeRow(topRow)
	for sideRow in ORDERS_SIDE_ROWS:
		ORDERS_SIDE_GRID.removeRow(sideRow)
	for botRow in ORDERS_BOT_ROWS:
		ORDERS_BOT_GRID.removeRow(botRow)
	
	# Clear orders from order list
	for order in ORDERS_SIDE:
		ORDERS_SIDE.pop()
	ORDERS_SIDE = []
	for order in ORDERS_TOP:
		ORDERS_TOP.pop()
	ORDERS_TOP = []
	for order in ORDERS_BOT:
		ORDERS_BOT.pop()
	ORDERS_BOT = []
	
	# Show menu
	inventoryCanvas.visible(False)
	
	bb = inventoryGrid.getBoundingBox()
	inventoryCanvas.setRenderWorld([bb.width,bb.height],[1,viz.AUTO_COMPUTE])


def createTruss(order=Order(),path=''):
	truss = viz.addChild(path,cache=viz.CACHE_COPY)
	truss.order = order
	truss.diameter = float(order.diameter)
	truss.thickness = float(order.thickness)
	truss.length = float(order.length)
	truss.quantity = int(order.quantity)
	truss.orientation = ORIENTATION
	truss.level = structures.Level.Horizontal
	truss.isNewMember = False
	
	truss.setScale([truss.length,truss.diameter*0.001,truss.diameter*0.001])	

	posA = truss.getPosition()
	posA[0] -= truss.length * 0.5
	nodeA = vizshape.addSphere(0.3,pos=posA)
	nodeA.isNode = True
	nodeA.parent = truss
	nodeA.index = 0
#	nodeA.visible(False)
	truss.nodeA = nodeA
	truss.linkA = viz.grab(truss,nodeA)
	
	posB = truss.getPosition()
	posB[0] += truss.length * 0.5
	nodeB = vizshape.addSphere(0.3,pos=posB)
	nodeB.isNode = True
	nodeB.parent = truss
	nodeB.index = 1
#	nodeB.visible(False)
	truss.nodeB = nodeB
	truss.linkB = viz.grab(truss,nodeB)
		
	nodeA.otherNode = nodeB
	nodeB.otherNode = nodeA
	truss.proxyNodes = [nodeA,nodeB]
	
	targetA = vizproximity.Target(truss.proxyNodes[0])
	targetB = vizproximity.Target(truss.proxyNodes[1])
	truss.targetNodes = [targetA,targetB]
	
	sensorA =  vizproximity.addBoundingSphereSensor(truss.proxyNodes[0])
	sensorB =  vizproximity.addBoundingSphereSensor(truss.proxyNodes[1])
	truss.sensorNodes = [sensorA,sensorB]
	
	applyEnvironmentEffect(truss)	
	
	return truss


def createTrussNew(order=Order(),path='',loading=False):
	truss = viz.addChild(path,cache=viz.CACHE_COPY)
	truss.order = order
	truss.diameter = float(order.diameter)
	truss.thickness = float(order.thickness)
	truss.length = float(order.length)
	truss.quantity = int(order.quantity)
	truss.orientation = ORIENTATION
	truss.level = structures.Level.Horizontal
	
	truss.setScale([truss.length,truss.diameter*0.001,truss.diameter*0.001])	
	
	# Setup proximity-based snapping nodes
	posA = truss.getPosition()
	posA[0] -= truss.length * 0.5
	nodeA = vizshape.addSphere(0.3,pos=posA)
	nodeA.isNode = True
	nodeA.parent = truss
	nodeA.index = 0
#	nodeA.visible(False)
	truss.nodeA = nodeA
	truss.linkA = viz.grab(truss,nodeA)
	
	posB = truss.getPosition()
	posB[0] += truss.length * 0.5
	nodeB = vizshape.addSphere(0.3,pos=posB)
	nodeB.isNode = True
	nodeB.parent = truss
	nodeB.index = 1
#	nodeB.visible(False)
	truss.nodeB = nodeB
	truss.linkB = viz.grab(truss,nodeB)
	
	nodeA.otherNode = nodeB
	nodeB.otherNode = nodeA
	truss.proxyNodes = [nodeA,nodeB]
	
	# Setup target nodes at both ends
	targetA = vizproximity.Target(truss.proxyNodes[0])
	targetB = vizproximity.Target(truss.proxyNodes[1])	
	truss.targetNodes = [targetA,targetB]
	
	# Setup sensor nodes at both ends
	sensorA =  vizproximity.addBoundingSphereSensor(truss.proxyNodes[0])
	sensorB =  vizproximity.addBoundingSphereSensor(truss.proxyNodes[1])	
	truss.sensorNodes = [sensorA,sensorB]
	
	global BUILD_MEMBERS
	global highlightTool
	global proxyManager
	global PROXY_NODES
	global TARGET_NODES
	global SENSOR_NODES
	
	global PRE_SNAP_POS	
	global PRE_SNAP_ROT

	PRE_SNAP_POS = truss.getPosition()
	PRE_SNAP_ROT = truss.getEuler()
	
	PROXY_NODES.append(truss.proxyNodes[0])
	PROXY_NODES.append(truss.proxyNodes[1])
	TARGET_NODES.append(truss.targetNodes[0])
	TARGET_NODES.append(truss.targetNodes[1])
	SENSOR_NODES.append(truss.sensorNodes[0])
	SENSOR_NODES.append(truss.sensorNodes[1])
	
	# Enable truss nodes to interact with other sensors
	proxyManager.addTarget(truss.targetNodes[0])
	proxyManager.addTarget(truss.targetNodes[1])

	BUILD_MEMBERS.append(truss)
	applyEnvironmentEffect(truss)
	
	try:
		# Clear highlighter
		highlightTool.clear()
		currentTruss = [truss]
		highlightTool.setItems(currentTruss)
	except:
		print 'Failed: Highlighter not initialized!'
	
	if not loading:
		global grabbedItem
		global highlightedItem
		global isgrabbing
		global VALID_SNAP
		
		grabbedItem = truss		
		highlightedItem = truss
		isgrabbing = True
		VALID_SNAP = False
		
		truss.isNewMember = True		
		cycleMode(structures.Mode.Add)
		
		#--Set alpha to 1
		truss.alpha(1)
		truss.proxyNodes[0].alpha(1)
		truss.proxyNodes[1].alpha(1)
	else:
		truss.isNewMember = False
	
	return truss

def deleteTruss():
	global highlightedItem
	global grabbedItem
	global isgrabbing
	
	PROXY_NODES.remove(grabbedItem.proxyNodes[0])
	PROXY_NODES.remove(grabbedItem.proxyNodes[1])
	grabbedItem.proxyNodes[0].remove()
	grabbedItem.proxyNodes[1].remove()
	
	TARGET_NODES.remove(grabbedItem.targetNodes[0])
	TARGET_NODES.remove(grabbedItem.targetNodes[1])
	
	SENSOR_NODES.remove(grabbedItem.sensorNodes[0])
	SENSOR_NODES.remove(grabbedItem.sensorNodes[1])
	proxyManager.removeSensor(grabbedItem.sensorNodes[0])
	proxyManager.removeSensor(grabbedItem.sensorNodes[1])
	
	BUILD_MEMBERS.remove(grabbedItem)
	
	if grabbedItem.isNewMember == True:
		proxyManager.removeTarget(grabbedItem.targetNodes[0])
		proxyManager.removeTarget(grabbedItem.targetNodes[1])
	else:
		if grabbedItem.orientation == structures.Orientation.Side:
			try:
				grabbedItem.clonedSide.nodeA.remove()
				grabbedItem.clonedSide.nodeB.remove()
				SIDE_CLONES.remove(grabbedItem.clonedSide)
				grabbedItem.clonedSide.remove()
				grabbedItem.clonedSide = None
			except:
				print 'deleteTruss: No cloned side to remove!'
		
			SIDE_MEMBERS.remove(grabbedItem)
		elif grabbedItem.orientation == structures.Orientation.Top:
			TOP_MEMBERS.remove(grabbedItem)
		elif grabbedItem.orientation == structures.Orientation.Bottom:
			BOT_MEMBERS.remove(grabbedItem)
		
		try:
			GRAB_LINKS.remove(grabbedItem.link)
		except:
			print 'deleteTruss: No link to remove!'
	
	highlightTool.clear()
	highlightedItem = None
	grabbedItem.remove()
	grabbedItem = None
	isgrabbing = False
	
	if MODE != structures.Mode.Edit:
		cycleMode(structures.Mode.Build)
		
	toggleHighlightables()
	
	# Play warning sound
	warningSound.play()

def generateMembers(loading=False):
	"""Create truss members based on order list"""
	global BUILD_MEMBERS
	global highlightTool
	global ORDERS
	global ROWS
	global proxyManager
	global highlightTool
	
	#Clear order ROWS
	for row in ROWS:
		ORDERS_SIDE_GRID.removeRow(row)
	ROWS = []
	
	# Clear current inventory
	for member in BUILD_MEMBERS:
		PROXY_NODES.remove(member.proxyNodes[0])
		PROXY_NODES.remove(member.proxyNodes[1])
		TARGET_NODES.remove(member.targetNodes[0])
		TARGET_NODES.remove(member.targetNodes[1])
		SENSOR_NODES.remove(member.sensorNodes[0])
		SENSOR_NODES.remove(member.sensorNodes[1])
		proxyManager.removeSensor(member.sensorNodes[0])
		proxyManager.removeSensor(member.sensorNodes[1])
		member.remove()
		del member
		member = None
	BUILD_MEMBERS = []
	
#	clearMembers()
	
	for i, order in enumerate(ORDERS):
		trussMember = createTruss(order,'resources/chs.osgb')
		trussMember.order = order
		
		PROXY_NODES.append(trussMember.proxyNodes[0])
		PROXY_NODES.append(trussMember.proxyNodes[1])
		TARGET_NODES.append(trussMember.targetNodes[0])
		TARGET_NODES.append(trussMember.targetNodes[1])
		SENSOR_NODES.append(trussMember.sensorNodes[0])
		SENSOR_NODES.append(trussMember.sensorNodes[1])
		proxyManager.addSensor(trussMember.sensorNodes[0])
		proxyManager.addSensor(trussMember.sensorNodes[1])

		BUILD_MEMBERS.append(trussMember)

	# Clear ORDERS
	ORDERS = []


def clearMembers():
	"""Delete truss members"""
	global highlightTool
	global PROXY_NODES
	global TARGET_NODES
	global SENSOR_NODES
	global BUILD_MEMBERS
	global SIDE_MEMBERS
	global TOP_MEMBERS
	global BOT_MEMBERS
	global SIDE_CLONES
	global GRAB_LINKS
	
	#--Force clear highlight
	highlightTool.clear()
	
	try:
		highlightTool.removeItems(BUILD_MEMBERS)
		highlightTool.removeItems(PROXY_NODES)
	except:
		print 'clearMembers: Failed to remove highlightable items'
	
	highlightTool.setItems([])
	proxyManager.clearTargets()
			
	for node in PROXY_NODES:
		node.remove()
		node = None
		del node
	PROXY_NODES = []
	for target in TARGET_NODES:
		target = None
		del target
	TARGET_NODES = []
	for sensor in SENSOR_NODES:
		proxyManager.removeSensor(sensor)
		sensor = None
		del sensor
	SENSOR_NODES = []
	
	# Clear previous bridge
	for member in BUILD_MEMBERS:
		member.remove()
		member = None
	BUILD_MEMBERS = []
	for clone in SIDE_CLONES:
		clone.nodeA.remove()
		clone.nodeB.remove()
		clone.remove()
		clone = None
	SIDE_CLONES = []
	for member in SIDE_MEMBERS:
		member.remove()
		member = None
	SIDE_MEMBERS = []
	for member in TOP_MEMBERS:
		member.remove()
		member = None
	TOP_MEMBERS = []
	for member in BOT_MEMBERS:
		member.remove()
		member = None
	BOT_MEMBERS = []
	
	# Clear grab links
	for link in GRAB_LINKS:
		link.remove()
		link = None
	GRAB_LINKS = []
	
	#--Clear road
	toggleRoad(road)
	
	# Show feedback
	runFeedbackTask('Bridge cleared!')
	hideMenuSound.play()

def toggleAudio(value=viz.TOGGLE):
	global ISMUTED
	if ISMUTED:
		for sound in SOUNDS:
			sound.volume(SFX_VOLUME)
		warningSound.volume(WARNING_VOLUME)
		runFeedbackTask('Sound ON')
	else:
		for sound in SOUNDS:
			sound.volume(0)
		runFeedbackTask('Sound OFF')

	ISMUTED = not ISMUTED
	clickSound.play()
	
	
def toggleEnvironment(value=viz.TOGGLE):
	environment_root.visible(value)
	
	# Show feedback
	if environment_root.getVisible() is True:
		runFeedbackTask('Environment ON')
		clickSound.play()
	else:
		runFeedbackTask('Environment OFF')
		hideMenuSound.play()

def toggleGrid(value=viz.TOGGLE):
	grid_root.visible(value)
	
	# Show feedback
	if grid_root.getVisible() is True:
		runFeedbackTask('Grid ON')
		clickSound.play()
	else:
		runFeedbackTask('Grid OFF')
		hideMenuSound.play()

def toggleMembers(side=True,sideClones=True,top=True,bottom=True):
		for member in SIDE_MEMBERS:
			member.visible(side)
			member.nodeA.visible(side)
			member.nodeB.visible(side)
		for member in SIDE_CLONES:
			member.visible(sideClones)
			member.nodeA.visible(sideClones)
			member.nodeB.visible(sideClones)
			member.alpha(1)
			member.nodeA.alpha(1)
			member.nodeB.alpha(1)			
		for member in TOP_MEMBERS:
			member.visible(top)
			member.nodeA.visible(top)
			member.nodeB.visible(top)
		for member in BOT_MEMBERS:
			member.visible(bottom)
			member.nodeA.visible(bottom)
			member.nodeB.visible(bottom)
		#--Turn all alpha values to 1 for full visibility
		for members in BUILD_MEMBERS:
			members.alpha(1)
		for nodes in PROXY_NODES:
			nodes.alpha(1)


def toggleHighlightables(val=True):
	highlightTool.clear()
	highlightables = BUILD_MEMBERS + PROXY_NODES
	if val is True:
		highlightTool.setItems([])
		highlightTool.setItems(highlightables)
	else:
		highlightTool.removeItems(highlightables)
		highlightTool.setItems([])

def getOrientationHighlightables():
	highlightTool.clear()
	highlightables = []
	
	if ORIENTATION is structures.Orientation.Top:	
		for member in SIDE_CLONES:
			member.visible(True)
			member.nodeA.visible(True)
			member.nodeB.visible(True)
			member.alpha(INACTIVE_ALPHA)
			member.nodeA.alpha(INACTIVE_ALPHA)
			member.nodeB.alpha(INACTIVE_ALPHA)
		for member in SIDE_MEMBERS:
			member.visible(True)
			proxyManager.addSensor(member.sensorNodes[0])
			proxyManager.addSensor(member.sensorNodes[1])
			member.proxyNodes[0].visible(True)
			member.proxyNodes[1].visible(True)
			member.alpha(INACTIVE_ALPHA)
			member.proxyNodes[0].alpha(INACTIVE_ALPHA)
			member.proxyNodes[1].alpha(INACTIVE_ALPHA)			
		for member in BOT_MEMBERS:
			member.visible(False)
			proxyManager.removeSensor(member.sensorNodes[0])
			proxyManager.removeSensor(member.sensorNodes[1])
			member.proxyNodes[0].visible(False)
			member.proxyNodes[1].visible(False)
		for member in TOP_MEMBERS:
			member.visible(True)	
			proxyManager.addSensor(member.sensorNodes[0])
			proxyManager.addSensor(member.sensorNodes[1])
			member.proxyNodes[0].visible(True)
			member.proxyNodes[1].visible(True)
			member.alpha(1)
			member.proxyNodes[0].alpha(1)
			member.proxyNodes[1].alpha(1)			
			#--Add to highlight
			highlightables.append(member)
			highlightables.append(member.proxyNodes[0])
			highlightables.append(member.proxyNodes[1])
	elif ORIENTATION is structures.Orientation.Bottom:
		for member in SIDE_CLONES:
			member.visible(True)
			member.nodeA.visible(True)
			member.nodeB.visible(True)
			member.alpha(INACTIVE_ALPHA)
			member.nodeA.alpha(INACTIVE_ALPHA)
			member.nodeB.alpha(INACTIVE_ALPHA)		
		for member in SIDE_MEMBERS:
			member.visible(True)
			proxyManager.addSensor(member.sensorNodes[0])
			proxyManager.addSensor(member.sensorNodes[1])
			member.proxyNodes[0].visible(True)
			member.proxyNodes[1].visible(True)
			#--Lower opacity of guide truss members
			member.alpha(INACTIVE_ALPHA)
			member.proxyNodes[0].alpha(INACTIVE_ALPHA)
			member.proxyNodes[1].alpha(INACTIVE_ALPHA)				
		for member in TOP_MEMBERS:
			member.visible(False)
			proxyManager.removeSensor(member.sensorNodes[0])
			proxyManager.removeSensor(member.sensorNodes[1])
			member.proxyNodes[0].visible(False)
			member.proxyNodes[1].visible(False)
		for member in BOT_MEMBERS:
			member.visible(True)
			proxyManager.addSensor(member.sensorNodes[0])
			proxyManager.addSensor(member.sensorNodes[1])
			member.proxyNodes[0].visible(True)
			member.proxyNodes[1].visible(True)	
			member.alpha(1)
			member.proxyNodes[0].alpha(1)
			member.proxyNodes[1].alpha(1)			
			#--Add to highlight
			highlightables.append(member)
			highlightables.append(member.proxyNodes[0])
			highlightables.append(member.proxyNodes[1])
	elif ORIENTATION is structures.Orientation.Side:			
		for member in SIDE_CLONES:
			member.visible(False)
			member.nodeA.visible(False)
			member.nodeB.visible(False)			
		for member in SIDE_MEMBERS:
			member.visible(True)
			proxyManager.addSensor(member.sensorNodes[0])
			proxyManager.addSensor(member.sensorNodes[1])
			member.proxyNodes[0].visible(True)
			member.proxyNodes[1].visible(True)	
			#--Set opacity of side truss to 1
			member.alpha(1)
			member.proxyNodes[0].alpha(1)
			member.proxyNodes[1].alpha(1)				
			#--Add to highlight
			highlightables.append(member)
			highlightables.append(member.proxyNodes[0])
			highlightables.append(member.proxyNodes[1])			
		for member in TOP_MEMBERS:
			member.visible(False)
			proxyManager.removeSensor(member.sensorNodes[0])
			proxyManager.removeSensor(member.sensorNodes[1])
			member.proxyNodes[0].visible(False)
			member.proxyNodes[1].visible(False)
		for member in BOT_MEMBERS:
			member.visible(False)
			proxyManager.removeSensor(member.sensorNodes[0])
			proxyManager.removeSensor(member.sensorNodes[1])
			member.proxyNodes[0].visible(False)
			member.proxyNodes[1].visible(False)
	return highlightables
	

def toggleUtility(val=viz.TOGGLE):
	if isgrabbing or isrotating:
		return
	
	if menuCanvas.getVisible() is True:
		menuCanvas.visible(False)
		
	utilityCanvas.visible(val)
	glove.visible(False)

	if utilityCanvas.getVisible() is True:
		inventoryCanvas.setMouseStyle(viz.CANVAS_MOUSE_VISIBLE)
		showMenuSound.play()
	else:
		if MODE == structures.Mode.Build:
			inventoryCanvas.setMouseStyle(viz.CANVAS_MOUSE_VIRTUAL)
		elif MODE == structures.Mode.Edit:
			glove.visible(True)
		hideMenuSound.play()


def clampTrackerScroll(tracker,min=0.2,max=20):
	tracker.distance = viz.clamp(tracker.distance,min,max)


def toggleMenu(val=viz.TOGGLE):
	global SHOW_HIGHLIGHTER
	
	#--If grabbing or rotating truss, exit
	if isgrabbing is True or isrotating is True:
		return
		
	if utilityCanvas.getVisible() is True:
		utilityCanvas.visible(False)
		
	menuCanvas.visible(val)
	if menuCanvas.getVisible() is True:
		pos = viz.MainView.getLineForward().endFromDistance(.75)
		rot = viz.MainView.getLineForward().euler
		menuCanvas.setPosition(pos)
		menuCanvas.setEuler(rot)
		dialogCanvas.setPosition([pos[0],pos[1]-1,pos[2]])
		dialogCanvas.setEuler(rot)
		inventoryCanvas.visible(False)
		glove.visible(False)
		SHOW_HIGHLIGHTER = False
		createConfirmButton()
		showMenuSound.play()
	else:
		hideMenuSound.play()
		if MODE == structures.Mode.Build or MODE is structures.Mode.Edit:
			cycleMode(MODE)


def toggleMenuLink():
#	global menuLink
	if menuLink:
		# If link exists, stop grabbing
		menuLink.remove()
		menuLink = None
	else:
		euler = gloveLink.getEuler()
		menuCanvas.setPosition(gloveLink.getPosition())
		menuCanvas.setEuler(0,0,0)
		menuLink = viz.grab( gloveLink, menuCanvas )
		menuCanvas.visible(True)
		

def toggleStereo(val=viz.TOGGLE):
	if val is True:
		runFeedbackTask('Stereo Horz')
		viz.MainWindow.stereo(STEREOMODE)
	else:
		runFeedbackTask('Stereo Right')
		viz.MainWindow.stereo(viz.STEREO_RIGHT)	
		
		
def toggleCollision(val=viz.TOGGLE):
	viz.collision(val)
	if val == 1:
		viz.phys.enable()
		print 'Physics: ON | Collision: ', val
		
	else:
		viz.phys.disable()
		print 'Physics: OFF | Collision: ', val

def updateScreenText():
    object = viz.MainWindow.pick(info=True)
    if object.valid:
        name = object.name
        if name.startswith('painting_'):
            name = name.replace('painting_','')
            textScreen.message(name)
        else:
            textScreen.message('')
#vizact.ontimer(0.1,updateScreenText)

# Update code for highlight tool
isgrabbing = False
grabbedItem = None
highlightedItem = None
grabbedRotation = []
objToRotate = None
isrotating = False
rotatingItem = None

def updateHighlightTool(highlightTool):	
	if SHOW_HIGHLIGHTER == True:
		highlightTool.highlight()
	else:
		highlightTool.clear()
		return
		
	if highlightTool.getSelection() is None:
		return

# Register a callback function for the highlight event
def onHighlight(e):
	global highlightedItem
	global rotatingItem
	
	#--Force clear
	highlightTool.clear()
	highlightedItem = None
	rotatingItem = None
	inspectMember(None)
	
	if e.new != None:
		highlightedItem = e.new
		if hasattr(e.new,'length'):
			inspectMember(highlightedItem)
		elif hasattr(e.new,'isNode'):
#			print 'onHighlight: Node parent is',e.new.parent
			rotatingItem = e.new
	else:
		#--Force clear highlight
		highlightTool.clear()
		highlightedItem = None
		rotatingItem = None
		inspectMember(None)
#	print 'OnHighlight: Highlighting',highlightedItem
viz.callback(highlighter.HIGHLIGHT_EVENT,onHighlight)


def onHighlightGrab():
	""" Clamp grabbed member to front glove position and grid z """
	global grabbedItem
	global isgrabbing
	if grabbedItem is not None and isgrabbing is True:	
		raycaster = highlightTool.getRayCaster()
		startPos = raycaster.getPosition()
#		print startPos
		dist = mathlite.math.fabs(startPos[2] - GRID_Z)
#		print dist
#		newPoint = raycaster.getLineForward(length=dist).getEnd()
#		print newPoint
		newPos = raycaster.getLineForward().endFromDistance(dist)
		newPos[2] = GRID_Z
		grabbedItem.setPosition(newPos)
vizact.ontimer(0,onHighlightGrab)

def onHighlightGrab2():
	global grabbedItem
	global isgrabbing
	pos = []
	object = viz.MainWindow.pick(info=True,pos=(0.5,0.5))
	if object.valid:
		pos = object.point
	if grabbedItem is not None and isgrabbing is True:	
		grabbedItem.setPosition(pos)
#vizact.ontimer(0,onHighlightGrab2)


def onRelease(e=None):
	global BUILD_MEMBERS
	global grabbedItem
	global isgrabbing
	global highlightedItem
	global proxyManager
	global PRE_SNAP_POS
	global PRE_SNAP_ROT
	global SNAP_TO_POS
	global VALID_SNAP
	global bridge_root
	global GRAB_LINKS
	global SHOW_HIGHLIGHTER
	global PROXY_NODES
	global highlightTool
	
#	print 'OnRelease: VALID_SNAP is',VALID_SNAP
#	print 'OnRelease: SNAP_TO_POS is', SNAP_TO_POS
#	print 'OnRelease: PRE_SNAP_POS is', PRE_SNAP_POS
	
	if VALID_SNAP:
		# If new member, group appropriately
		if grabbedItem.isNewMember == True:
			grabbedItem.orientation = ORIENTATION
			if ORIENTATION == structures.Orientation.Side:		
				SIDE_MEMBERS.append(grabbedItem)
				grabbedItem.clonedTruss = cloneSide(grabbedItem)
			elif ORIENTATION == structures.Orientation.Top:
				TOP_MEMBERS.append(grabbedItem)
			elif ORIENTATION == structures.Orientation.Bottom:
				BOT_MEMBERS.append(grabbedItem)
			grabbedItem.isNewMember = False
			
		# Check facing of truss

		xFacing = 1
		if grabbedItem.getPosition()[0] < SNAP_TO_POS[0]:
			xFacing = -1
		yFacing = 1
		if grabbedItem.getPosition()[1] < SNAP_TO_POS[1]:
			yFacing = -1
			
		# Check if vertical truss
		xOffset = mathlite.math.fabs(grabbedItem.proxyNodes[1].getPosition()[0] - grabbedItem.proxyNodes[0].getPosition()[0]) / 2
		xOffset *= xFacing
		yOffset = mathlite.math.fabs(grabbedItem.proxyNodes[1].getPosition()[1] - grabbedItem.proxyNodes[0].getPosition()[1]) / 2
		yOffset *= yFacing

		clampedX =  viz.clamp(grabbedItem.getPosition()[0],-10 + xOffset,10 - xOffset)
		clampedY =  viz.clamp(grabbedItem.getPosition()[1],2,10)
		grabbedItem.setPosition( [SNAP_TO_POS[0] + xOffset, SNAP_TO_POS[1] + yOffset, SENSOR_NODE.getPosition()[2]] )
		grabbedItem.setEuler( [0,0,grabbedItem.getEuler()[2]] )
		
		# Enable sensor nodes for other members to snap to
		proxyManager.addSensor(grabbedItem.sensorNodes[0])
		proxyManager.addSensor(grabbedItem.sensorNodes[1])
		
		# Play snap MUTE
		clickSound.play()
	else:
		# If invalid position and newly-generated truss, destroy it
		if grabbedItem.isNewMember == True:
			highlightTool.clear()
			BUILD_MEMBERS.remove(grabbedItem)
			proxyManager.removeTarget(grabbedItem.targetNodes[0])
			proxyManager.removeTarget(grabbedItem.targetNodes[1])
			PROXY_NODES.remove(grabbedItem.proxyNodes[0])
			PROXY_NODES.remove(grabbedItem.proxyNodes[1])
			grabbedItem.proxyNodes[0].remove()
			grabbedItem.proxyNodes[1].remove()
			grabbedItem.remove()
			highlightedItem = None
			grabbedItem = None
		else:	
			grabbedItem.setPosition(PRE_SNAP_POS)
			grabbedItem.setEuler(PRE_SNAP_ROT)
			# Enable sensor nodes for other members to snap to
			proxyManager.addSensor(grabbedItem.sensorNodes[0])
			proxyManager.addSensor(grabbedItem.sensorNodes[1])
		
		# Play warning sound
		warningSound.play()
			
	# Re-grab existing Build members
#	for members in BUILD_MEMBERS:
#		link = viz.grab(bridge_root,members)
#		GRAB_LINKS.append(link)
	if grabbedItem is not None:
		link = viz.grab(bridge_root.getGroup(),grabbedItem)
		GRAB_LINKS.append(link)
		grabbedItem.link = link
	
		# Disable truss member target nodes on release
		proxyManager.removeTarget(grabbedItem.targetNodes[0])
		proxyManager.removeTarget(grabbedItem.targetNodes[1])
		
	SNAP_TO_POS = []
	
	# Clear item references
	highlightedItem = None
	grabbedItem = None
	isgrabbing = False
	print 'OnRelease: HighlightedItem is',highlightedItem,'GrabbedItem is',grabbedItem,'IsGrabbing is',isgrabbing
	
	# Change mode back to Build if not editing
	if MODE != structures.Mode.Edit:
		cycleMode(structures.Mode.Build)
	else:
		highlightTool.setItems(getOrientationHighlightables())


def cloneSide(truss):
	pos = truss.getPosition()
	rot = truss.getEuler()
	scale = truss.getScale()
	
	#--Check for truss level
	pos[2] *= -1
		
	clone = truss.clone()
	clone.setScale(scale)
	clone.setPosition(pos)
	clone.setEuler(rot)
	
	truss.clonedSide = clone
	
	#--Create spherical connectors
	posA = truss.proxyNodes[0].getPosition()
	posA[2] = pos[2]
	nodeA = vizshape.addSphere(0.3,pos=posA)
	clone.nodeA = nodeA
	viz.grab(clone,nodeA)
	
	posB = truss.proxyNodes[1].getPosition()
	posB[2] = pos[2]
	nodeB = vizshape.addSphere(0.3,pos=posB)
	clone.nodeB = nodeB
	viz.grab(clone,nodeB)
	
	#--Grab clone with truss
	viz.grab(truss,clone)
	
	#--Add clone to list
	SIDE_CLONES.append(clone)
	
	#--Toggle visibility of side clones
	clone.visible(False)
	nodeA.visible(False)
	nodeB.visible(False)
	
	return clone


def toggleRoad(road):
	if len(BOT_MEMBERS) is not 0:
		message = ''
		if road.getVisible() is True:
			message = 'Road removed'
			road.visible(False)
		else:
			message = 'Road added'
			road.visible(True)
		runFeedbackTask(message)
	else:
		runFeedbackTask('No support for road!')
		road.visible(False)
	
	
def updateQuantity(order,button,orderList,inventory,row):
	if order.quantity > 0:
		order.quantity -= 1
		button.message('{}m(l) x {}mm(d) x {}mm(th) [{}]'.format(order.length, order.diameter, order.thickness, order.quantity))
	if order.quantity <= 0:
		inventory.removeRow(row)
#		orderList.remove(order)
		

def updateAngle(obj,slider,label):
	if obj != None:
		rot = obj.getEuler()
		pos = mathlite.getNewRange(rot[2],180,-180,0,1)
		slider.set(pos)
		string = str(int(rot[2])) + '°'
		label.message(string)
		

def rotateTruss():
	global objToRotate
	global isrotating
	
	if objToRotate is not None and isrotating is True:
		# Clamp glove link z-orientation
		mousePos = viz.mouse.getPosition()
		rotateValue = mathlite.getNewRange(mousePos[1],0,1,180,-180)
		#--Rotate based on index
		if objToRotate.index is 0:
			rotateValue *= -1
		objToRotate.setEuler(0,0,rotateValue)
		#--Check near 90
		rot = objToRotate.getEuler()
		if mathlite.math.fabs(rot[2]+90) <= 5:
			rot[2] = -90
		elif mathlite.math.fabs(rot[2]-90) <= 5:
			rot[2] = 90
		elif mathlite.math.fabs(rot[2]) <= 5:
			rot[2] = 0
		objToRotate.setEuler(rot)
		
		updateAngle(objToRotate,rotationSlider,rotationLabel)
	else:
		#--Hide rotation GUI
		rotationCanvas.visible(False)
vizact.ontimer(0,rotateTruss)

global isSpinning
isSpinning = False
def spinTruss(truss):
	global isSpinning
	if not isSpinning:
		isSpinning = True
		rot = truss.getEuler()
		z = rot[2] + 45
		spin = vizact.spinTo(euler=[0,0,z],time=0.1,interpolate=vizact.easeInOutCubic)
		truss.addAction(spin)
		isSpinning = False
	
	
def resetSensors():
	proxyManager.clearSensors()
	proxyManager.addSensor(pinAnchorSensor)
	proxyManager.addSensor(rollerAnchorSensor)

	
def cycleOrientation(val):
	global ORIENTATION
	global grabbedItem
	global grid_root
	
	#--Force clear highlight
	highlightTool.clear()

	if MODE is structures.Mode.View or MODE is structures.Mode.Walk:
		return
	
	if grabbedItem is not None or isrotating is True:
		return
		
	pos = []
	rot = []

	resetSensors()
	highlightables = []	#--Define highlightables
	highlightTool.setItems([])
	
	for model in supports:
		model.alpha(SUPPORT_ALPHA)	
		
	ORIENTATION = val
	if val == structures.Orientation.Top:
		rot = TOP_VIEW_ROT
		pos = TOP_VIEW_POS
		pos[2] = TOP_CACHED_Z
		
		for member in SIDE_CLONES:
			member.visible(True)
			member.nodeA.visible(True)
			member.nodeB.visible(True)
			member.alpha(INACTIVE_ALPHA)
			member.nodeA.alpha(INACTIVE_ALPHA)
			member.nodeB.alpha(INACTIVE_ALPHA)
		for member in SIDE_MEMBERS:
			member.visible(True)
			proxyManager.addSensor(member.sensorNodes[0])
			proxyManager.addSensor(member.sensorNodes[1])
			member.proxyNodes[0].visible(True)
			member.proxyNodes[1].visible(True)
			member.alpha(INACTIVE_ALPHA)
			member.proxyNodes[0].alpha(INACTIVE_ALPHA)
			member.proxyNodes[1].alpha(INACTIVE_ALPHA)			
		for member in BOT_MEMBERS:
			member.visible(False)
			proxyManager.removeSensor(member.sensorNodes[0])
			proxyManager.removeSensor(member.sensorNodes[1])
			member.proxyNodes[0].visible(False)
			member.proxyNodes[1].visible(False)
		for member in TOP_MEMBERS:
			member.visible(True)	
			proxyManager.addSensor(member.sensorNodes[0])
			proxyManager.addSensor(member.sensorNodes[1])
			member.proxyNodes[0].visible(True)
			member.proxyNodes[1].visible(True)
			member.alpha(1)
			member.proxyNodes[0].alpha(1)
			member.proxyNodes[1].alpha(1)			
			#--Add to highlight
			highlightables.append(member)
			highlightables.append(member.proxyNodes[0])
			highlightables.append(member.proxyNodes[1])
		grid_root.setInfoMessage(VIEW_MESSAGE)
	elif val == structures.Orientation.Bottom:
		rot = BOT_VIEW_ROT
		pos = BOT_VIEW_POS
		pos[2] = BOT_CACHED_Z
		
		for member in SIDE_CLONES:
			member.visible(True)
			member.nodeA.visible(True)
			member.nodeB.visible(True)
			member.alpha(INACTIVE_ALPHA)
			member.nodeA.alpha(INACTIVE_ALPHA)
			member.nodeB.alpha(INACTIVE_ALPHA)		
		for member in SIDE_MEMBERS:
			member.visible(True)
			proxyManager.addSensor(member.sensorNodes[0])
			proxyManager.addSensor(member.sensorNodes[1])
			member.proxyNodes[0].visible(True)
			member.proxyNodes[1].visible(True)
			#--Lower opacity of guide truss members
			member.alpha(INACTIVE_ALPHA)
			member.proxyNodes[0].alpha(INACTIVE_ALPHA)
			member.proxyNodes[1].alpha(INACTIVE_ALPHA)				
		for member in TOP_MEMBERS:
			member.visible(False)
			proxyManager.removeSensor(member.sensorNodes[0])
			proxyManager.removeSensor(member.sensorNodes[1])
			member.proxyNodes[0].visible(False)
			member.proxyNodes[1].visible(False)
		for member in BOT_MEMBERS:
			member.visible(True)
			proxyManager.addSensor(member.sensorNodes[0])
			proxyManager.addSensor(member.sensorNodes[1])
			member.proxyNodes[0].visible(True)
			member.proxyNodes[1].visible(True)	
			member.alpha(1)
			member.proxyNodes[0].alpha(1)
			member.proxyNodes[1].alpha(1)			
			#--Add to highlight
			highlightables.append(member)
			highlightables.append(member.proxyNodes[0])
			highlightables.append(member.proxyNodes[1])
		grid_root.setInfoMessage(VIEW_MESSAGE)
	else:
		rot = SIDE_VIEW_ROT
		pos = BRIDGE_ROOT_POS
		
		for member in SIDE_CLONES:
			member.visible(False)
			member.nodeA.visible(False)
			member.nodeB.visible(False)			
		for member in SIDE_MEMBERS:
			member.visible(True)
			proxyManager.addSensor(member.sensorNodes[0])
			proxyManager.addSensor(member.sensorNodes[1])
			member.proxyNodes[0].visible(True)
			member.proxyNodes[1].visible(True)	
			#--Set opacity of side truss to 1
			member.alpha(1)
			member.proxyNodes[0].alpha(1)
			member.proxyNodes[1].alpha(1)				
			#--Add to highlight
			highlightables.append(member)
			highlightables.append(member.proxyNodes[0])
			highlightables.append(member.proxyNodes[1])			
		for member in TOP_MEMBERS:
			member.visible(False)
			proxyManager.removeSensor(member.sensorNodes[0])
			proxyManager.removeSensor(member.sensorNodes[1])
			member.proxyNodes[0].visible(False)
			member.proxyNodes[1].visible(False)
		for member in BOT_MEMBERS:
			member.visible(False)
			proxyManager.removeSensor(member.sensorNodes[0])
			proxyManager.removeSensor(member.sensorNodes[1])
			member.proxyNodes[0].visible(False)
			member.proxyNodes[1].visible(False)
		grid_root.setInfoMessage(SIDE_VIEW_MESSAGE)
	
	#--Set new position and rotation
	bridge_root.getGroup().setEuler(rot)
	bridge_root.getGroup().setPosition(pos)
	
	#--Set new highlights
	highlightTool.setItems(highlightables)
	
	# Show feedback
	runFeedbackTask(str(ORIENTATION.name) + ' View')
	clickSound.play()
	grid_root.setOrientationMessage(str(ORIENTATION.name) + ' View')
	
CACHED_MODE = None
CACHED_BUILD_MODE = structures.Mode.Build
def cycleMode(mode=structures.Mode.Add):
	global SHOW_HIGHLIGHTER
	global MODE
	global CACHED_MODE
	global CACHED_BUILD_MODE
	global highlightTool
	global highlightedItem
	
	#--Force clear highlight
	highlightTool.clear()
	
	if isrotating: 
		return
	if MODE == structures.Mode.Add and grabbedItem is not None:
		return
	if MODE == structures.Mode.Edit and grabbedItem is not None:
		return
	
	toggleUtility(False)
	
	MODE = mode
	
	toggleEnvironment(False)
	toggleGrid(True)
	glove.visible(False)
	proxyManager.setDebug(True)
	inventoryCanvas.visible(True)
	
	if MODE == structures.Mode.Build:
		CACHED_BUILD_MODE = MODE
		
		inventoryCanvas.setMouseStyle(viz.CANVAS_MOUSE_VIRTUAL)

		#--Hide menu and inspector
		menuCanvas.visible(False)
		inspectorCanvas.visible(False)
		if info_root.getVisible() is True:
			info_root.visible(False)
			
		# Clear highlighter
		SHOW_HIGHLIGHTER = False
		highlightedItem = None
		highlightTool.clear()
		highlightTool.removeItems(BUILD_MEMBERS)
		highlightTool.removeItems(PROXY_NODES)
		highlightTool.setItems([])
		
		#--If cached mode is View or Walk, reset to build position
		if CACHED_MODE is structures.Mode.View or CACHED_MODE is structures.Mode.Walk:
			navigator.setPosition(START_POS)
			navigator.setEuler([0,0,0])
		
		navigator.setNavAbility()
		
		cycleOrientation(ORIENTATION)
		
	elif MODE == structures.Mode.Edit:
		CACHED_BUILD_MODE = MODE
		inventoryCanvas.setMouseStyle(viz.CANVAS_MOUSE_VISIBLE)
		
		menuCanvas.visible(False)	
		glove.visible(True)
		if info_root.getVisible() is True:
			info_root.visible(False)
			
		# Clear highlighter
		highlightTool.clear()
		highlightTool.removeItems(BUILD_MEMBERS)
		highlightTool.setItems([])
		highlightables = BUILD_MEMBERS + PROXY_NODES
		highlightTool.setItems(highlightables)
		SHOW_HIGHLIGHTER = True
		
		#--If cached mode is View or Walk, reset to build position
		if CACHED_MODE is structures.Mode.View or CACHED_MODE is structures.Mode.Walk:
			navigator.setPosition(START_POS)
			navigator.setEuler([0,0,0])		
		
		navigator.setNavAbility()
		
		cycleOrientation(ORIENTATION)
		
	elif MODE == structures.Mode.Add:
		inventoryCanvas.setMouseStyle(viz.CANVAS_MOUSE_VISIBLE)
		inventoryCanvas.visible(False)
		
		glove.visible(True)
		
		# Show highlighter
		SHOW_HIGHLIGHTER = True
		
	elif MODE == structures.Mode.View:
		inventoryCanvas.visible(viz.OFF)
		toggleGrid(False)
		toggleEnvironment(True)
		proxyManager.setDebug(False)
		bridge_root.getGroup().setPosition(BRIDGE_ROOT_POS)
		bridge_root.getGroup().setEuler(SIDE_VIEW_ROT)
		navigator.setNavAbility()
		
		# Show all truss members
		toggleMembers()
		
		# Clear highlighter
		SHOW_HIGHLIGHTER = False
		highlightedItem = None
		highlightTool.clear()
		highlightTool.removeItems(BUILD_MEMBERS)
		highlightTool.removeItems(PROXY_NODES)
		highlightTool.setItems([])
		
		# Hide supports
		for model in supports:
			model.alpha(0)
			
	elif MODE == structures.Mode.Walk:
		inventoryCanvas.visible(viz.OFF)
		toggleEnvironment(True)
		toggleGrid(False)
		proxyManager.setDebug(False)
		mouseTracker.distance = HAND_DISTANCE
		bridge_root.getGroup().setPosition(BRIDGE_ROOT_POS)
		bridge_root.getGroup().setEuler(SIDE_VIEW_ROT)
		navigator.setPosition(WALK_POS)
		navigator.setEuler(WALK_ROT)
		navigator.setNavAbility(elevate=False)
		
		# Show all truss members
		toggleMembers()
	
		# Clear highlighter
		SHOW_HIGHLIGHTER = False
		highlightedItem = None
		highlightTool.clear()
		highlightTool.removeItems(BUILD_MEMBERS)
		highlightTool.removeItems(PROXY_NODES)
		highlightTool.setItems([])
		
		# Hide supports
		for model in supports:
			model.alpha(0)
	
	#--Store new mode in cache
	CACHED_MODE = MODE
	
	# UI/Sound feedback
	runFeedbackTask(str(MODE.name) + ' Mode')
	
	
def cycleView(index):
	global MODE
	if MODE is structures.Mode.Build or MODE is structures.Mode.Add or MODE is structures.Mode.Edit:
		runFeedbackTask('Switch to View Mode!')
		warningSound.play()
		return
	try:
		targetPos = VIEW_SPOTS[index][0]
		targetRot = VIEW_SPOTS[index][1]
	except:
		# Feedback
		runFeedbackTask('Out of range!')
		warningSound.play()
		return
		
	navigator.setPosition(targetPos)
	navigator.setEuler(targetRot)
	navigator.setNavAbility(False,False)
	
	# Feedback
	runFeedbackTask('View ' + str(index))
	viewChangeSound.play()


# Setup Callbacks and Events
def onKeyUp(key):
	if key == KEYS['esc']:
		if utilityCanvas.getVisible() is True:
			toggleUtility(False)
		elif menuCanvas.getVisible() is True:
			toggleMenu(False)
		else:
			quitGame()
	elif key == KEYS['home']:
#		viewport.reset()
#		hmd.reset()
		navigator.reset()
		mouseTracker.distance = HAND_DISTANCE
		runFeedbackTask('View reset!')
		viewChangeSound.play()
	elif key == ',':
		getAvatarOrientation(navigator)
	elif key == KEYS['env'] or key == KEYS['env'].upper():
		toggleEnvironment()	
	elif key == KEYS['reset'] or key == KEYS['reset'].upper():
		try:
			runFeedbackTask('Orientation reset!')
			clickSound.play()
		except:
			runFeedbackTask('No headset!')
			warningSound.play()
			print 'Reset orientation failed: Unable to get Oculus Rift sensor!'
	elif key == KEYS['hand'] or key == KEYS['hand'].upper():
		mouseTracker.distance = HAND_DISTANCE
		clickSound.play()
	elif key == KEYS['builder'] or key == KEYS['builder'].upper():
		cycleMode(structures.Mode.Edit)
		mouseTracker.distance = HAND_DISTANCE
		clickSound.play()
	elif key == KEYS['viewer'] or key == KEYS['viewer'].upper():
		cycleMode(structures.Mode.View)
		mouseTracker.distance = HAND_DISTANCE
		clickSound.play()
	elif key == KEYS['walk'] or key == KEYS['walk'].upper():
		cycleMode(structures.Mode.Walk)
		clickSound.play()
	elif key == KEYS['grid'] or key == KEYS['grid'].upper():
		toggleGrid(viz.TOGGLE)
	elif key == KEYS['showMenu']:
		toggleMenu()
	elif key == KEYS['road']:
		toggleRoad(road)
		clickSound.play()
	elif key == KEYS['angles']:
		pass
	elif key == KEYS['proxi'] or key == KEYS['proxi'].upper():
		proxyManager.setDebug(viz.TOGGLE)
		clickSound.play()
	elif key == KEYS['capslock']:
		runFeedbackTask('Caps Lock')
		warningSound.play()


def onKeyDown(key):
	if key == KEYS['snapMenu']:
#		toggleMenuLink()
		pass


def onJoyButton(e):
	KEYS = navigator.KEYS
	
	if e.button == KEYS['esc']:
		if utilityCanvas.getVisible() is True:
			toggleUtility(False)
		elif menuCanvas.getVisible() is True:
			toggleMenu(False)
#		else:
#			quitGame()
	elif e.button == ',':
		print navigator.getPosition()
	elif e.button == KEYS['env']:
		toggleEnvironment()	
	elif e.button == KEYS['reset']:
		navigator.reset()
		if MODE == structures.Mode.Walk:
			cycleMode(structures.Mode.View)
		navigator.setNavAbility()
		mouseTracker.distance = HAND_DISTANCE
		runFeedbackTask('View reset!')
		viewChangeSound.play()
	elif e.button == KEYS['hand']:
		mouseTracker.distance = HAND_DISTANCE
		clickSound.play()
	elif e.button == KEYS['builder']:
		if MODE == structures.Mode.Build or MODE == structures.Mode.Edit:
			cycleMode(structures.Mode.View)
		elif MODE == structures.Mode.View or MODE == structures.Mode.Walk:
			mouseTracker.distance = HAND_DISTANCE
			cycleMode(CACHED_BUILD_MODE)
		clickSound.play()
	elif e.button == KEYS['viewer']:
		cycleMode(structures.Mode.View)
		mouseTracker.distance = HAND_DISTANCE
		clickSound.play()
	elif e.button == KEYS['walk']:
		cycleMode(structures.Mode.Walk)
		clickSound.play()
	elif e.button == KEYS['grid']:
		toggleGrid(viz.TOGGLE)
	elif e.button == KEYS['showMenu']:
		toggleMenu()
	elif e.button == KEYS['utility']:
		toggleUtility()
	elif e.button == KEYS['proxi']:
		proxyManager.setDebug(viz.TOGGLE)
		clickSound.play()

		
def onMouseWheel(dir):
#	global ORIENTATION
#	global bridge_root
#	
#	if ORIENTATION == Orientation.Top or ORIENTATION == Orientation.Bottom:
#		pos = bridge_root.getPosition()
#		if dir > 0:
#			pos[2] += 0.5	
#		else:
#			pos[2] -= 0.5
#		bridge_root.setPosition(pos)
	pass
		
def slideRoot(val):
	global TOP_CACHED_Z
	global BOT_CACHED_Z
	global bridge_root
	
	if ORIENTATION == structures.Orientation.Top or ORIENTATION == structures.Orientation.Bottom:
		pos = bridge_root.getGroup().getPosition()
		pos[2] += val
		if ORIENTATION == structures.Orientation.Top:
			clampedZ = viz.clamp(pos[2],TOP_Z_MIN,SLIDE_MAX)
			pos[2] = clampedZ
			TOP_CACHED_Z = pos[2]
		elif ORIENTATION == structures.Orientation.Bottom:
			clampedZ = viz.clamp(pos[2],BOT_Z_MIN,SLIDE_MAX)
			pos[2] = clampedZ
			BOT_CACHED_Z = pos[2]
		bridge_root.getGroup().setPosition(pos)	
	
global SLIDE_VAL
SLIDE_VAL = -1
def slideRootHat():
	global SLIDE_VAL
	global TOP_CACHED_Z
	global BOT_CACHED_Z
	global bridge_root
	
	if MODE is structures.Mode.View or MODE is structures.Mode.Walk:
		return
	
	if ORIENTATION == structures.Orientation.Top or ORIENTATION == structures.Orientation.Bottom:
		pos = bridge_root.getGroup().getPosition()
		if SLIDE_VAL == 0:
			pos[2] += SLIDE_INTERVAL
		elif SLIDE_VAL == 180:
			pos[2] -= SLIDE_INTERVAL
			
		if ORIENTATION == structures.Orientation.Top:
			clampedZ = viz.clamp(pos[2],TOP_Z_MIN,SLIDE_MAX)
			pos[2] = clampedZ
			TOP_CACHED_Z = pos[2]
		elif ORIENTATION == structures.Orientation.Bottom:
			clampedZ = viz.clamp(pos[2],BOT_Z_MIN,SLIDE_MAX)
			pos[2] = clampedZ
			BOT_CACHED_Z = pos[2]
		bridge_root.getGroup().setPosition(pos)
		bridge_root.getGroup().setPosition(pos)
	
def onHatChange(e):
	global SLIDE_VAL
	SLIDE_VAL = e.value
	
	if e.value == 90:	# Right
		if menuCanvas.getVisible() is True:
			index = menuTabPanel.panels.index(menuTabPanel.getSelectedPanel())
			try:
				menuTabPanel.selectPanel(index+1)
			except:
				menuTabPanel.selectPanel(0)
			clickSound.play()
		if inventoryCanvas.getVisible() is True:
			index = inventoryTabPanel.panels.index(inventoryTabPanel.getSelectedPanel())
			try:
				inventoryTabPanel.selectPanel(index+1)
			except:
				inventoryTabPanel.selectPanel(0)
			clickSound.play()
	elif e.value == 270:	# Left
		if menuCanvas.getVisible() is True:		
			index = menuTabPanel.panels.index(menuTabPanel.getSelectedPanel())	
			try:
				menuTabPanel.selectPanel(index-1)
			except:
				menuTabPanel.selectPanel(menuTabPanel.panels.count-1)
			clickSound.play()
		if inventoryCanvas.getVisible() is True:
			index = inventoryTabPanel.panels.index(inventoryTabPanel.getSelectedPanel())
			try:
				inventoryTabPanel.selectPanel(index-1)
			except:
				inventoryTabPanel.selectPanel(inventoryTabPanel.panels.count-1)
			clickSound.play()

def onMouseDown(button):
	global GRAB_LINKS
	global proxyManager
	global PRE_SNAP_POS
	global PRE_SNAP_ROT
	global SNAP_TO_POS
	global grabbedRotation
	global isgrabbing
	global isrotating 
	global highlightTool
	global highlightedItem
	global rotatingItem
	global rotateLinkA
	global rotateLinkB
	global objToRotate
	
	if button == KEYS['interact']:
#		print 'MouseDown: IsGrabbing is',isgrabbing
		#--Translation
		global isgrabbing
		if highlightedItem is not None and isgrabbing is False:
			isgrabbing = True
			
		#--Rotation
		if rotatingItem is not None:
			#--Show rotation GUI
			rotationCanvas.visible(True)
			
			newParentNode = None
			#--Break links
			try:
				GRAB_LINKS.remove(rotatingItem.parent.link)
				rotatingItem.parent.link.remove()
				rotatingItem.parent.link = None
			except:
				print 'No link'
			#--Link with opposing node as main
			if rotatingItem == rotatingItem.parent.proxyNodes[0]:
				newParentNode = rotatingItem.parent.proxyNodes[1]
			else:
				newParentNode = rotatingItem.parent.proxyNodes[0]
			#--New grab chain
			rotateLinkA = viz.grab(newParentNode,rotatingItem.parent)
			rotateLinkB = viz.grab(rotatingItem.parent,rotatingItem)
			objToRotate = newParentNode
			isrotating = True
			print 'onMouseDown: objToRotate is',objToRotate,'and isrotating is',isrotating


def onMouseUp(button):	
	global isgrabbing
	global grabbedItem
	global highlightedItem
	global PRE_SNAP_POS
	global PRE_SNAP_ROT
	global grabbedRotation
	global GRAB_LINKS
	global bridge_root
	global SNAP_TO_POS
	global objToRotate
	global isrotating
	global rotateLinkA
	global rotateLinkB
	
	if button == KEYS['interact']:	
		#--Release truss member to stop translation
		if isgrabbing is True and grabbedItem is not None:
			print 'MouseUp: Releasing',grabbedItem
			onRelease()
		#--Grab onto rotation node
		elif isrotating is True and objToRotate is not None:
			rotateLinkA.remove()
			rotateLinkA = None
			rotateLinkB.remove()
			rotateLinkB = None
			
			truss = objToRotate.parent
			otherNode = objToRotate.otherNode
			print 'Node', objToRotate, 'Other', otherNode
			viz.grab(truss,objToRotate)
			viz.grab(truss,otherNode)
			link = viz.grab(bridge_root.getGroup(),truss)			
			GRAB_LINKS.append(link)
			truss.link = link
			isgrabbing = False
			print 'MouseUp: Regrabbing '
		#--Check if still highlighting before attempting to grab truss
		elif highlightedItem is None:
			print 'MouseUp: Highlighted item is none, grabbing set to false'
			isgrabbing = False
		#--If highlighted truss is still valid, grab highlighted truss member
		elif isgrabbing is True and highlightedItem is not None and isrotating is False:
			grabbedItem = highlightedItem
			print 'MouseUp: Grabbing onto', grabbedItem.length,'m truss'
			try:
				GRAB_LINKS.remove(grabbedItem.link)
				grabbedItem.link.remove()
				grabbedItem.link = None
			except:
				print 'No link'
			
			#--Disable highlighting
			toggleHighlightables(False)
			
			# Enable truss member target nodes
			proxyManager.addTarget(grabbedItem.targetNodes[0])
			proxyManager.addTarget(grabbedItem.targetNodes[1])
			
			# Disable truss member sensor nodes
			proxyManager.removeSensor(grabbedItem.sensorNodes[0])
			proxyManager.removeSensor(grabbedItem.sensorNodes[1])
			
			PRE_SNAP_POS = grabbedItem.getPosition()
			PRE_SNAP_ROT = grabbedItem.getEuler()
			SNAP_TO_POS = PRE_SNAP_POS	# Wrong value to snap to
			grabbedRotation = PRE_SNAP_ROT
			print 'MouseUp: PRE_SNAP_POS',PRE_SNAP_POS,' | SNAP_TO_POS',SNAP_TO_POS
			
		#--Release objects
		objToRotate = None
		isrotating = False

		print 'MouseUp: IsGrabbing is',isgrabbing,' | GrabbedItem is',grabbedItem
	
	if button == KEYS['utility']:
		#--If mode is Mode.Add, flip truss; else toggle utils
		if grabbedItem is None:
			toggleUtility()
		elif MODE is structures.Mode.Add or MODE is structures.Mode.Edit:
			spinTruss(grabbedItem)
			
	if button == KEYS['rotate']:
		if grabbedItem is not None:			
			deleteTruss()


def onSlider(obj,pos):
	global objToRotate
	if obj == rotationSlider:
		if objToRotate != None:
			rotateTo = mathlite.getNewRange(pos,0,1,180,-180)
			highlightedItem.setEuler(0,0,int(rotateTo))
			rotation = highlightedItem.getEuler()
			string = str(int(rotation[2]))
			rotationLabel.message(string)
	if obj == quantitySlider:
		quantitySlider.set(pos)
		displayedQty = int(mathlite.getNewRange(pos,0.0,1.0,QTY_MIN,QTY_MAX))
		quantitySlider.message(str(displayedQty))
		

def onList(e):
	if e.object == diameterDropList:
		thicknesses = []
		index = e.object.getSelection()
		for thickness in catalogue_root[int(index)]:
			thicknesses.append(thickness.text)
		thicknessDropList.clearItems()
		thicknessDropList.addItems(thicknesses)
		
	if e.object == inventoryTabPanel.tabGroup:
		if e.newSel == 0:
			ORIENTATION = structures.Orientation.Side
		if e.newSel == 1:
			ORIENTATION = structures.Orientation.Top
		if e.newSel == 2:
			ORIENTATION = structures.Orientation.Bottom
		
	clickSound.play()
	
		
# Saves current Build members' truss dimensions, position, rotation to './data/bridge#.csv'
def SaveData():
	global BUILD_MEMBERS
		
	# Play MUTE
	clickSound.play()
	
	filePath = vizinput.fileSave(file='Bridge',filter=[('CSV Files','*.csv')],directory='./data/saves')		
	if filePath == '':
		return
		
	if not '.csv' in filePath:
		filePath += '.csv'
	
	cachedOrientation = ORIENTATION
	cycleOrientation(structures.Orientation.Side)
	
	with open(filePath,'wb') as f:
		writer = csv.writer(f)
		for truss in BUILD_MEMBERS:
			writer.writerow([str(truss.order.diameter),str(truss.order.thickness),str(truss.order.length),str(truss.order.quantity),
							str(truss.getPosition()[0]), str(truss.getPosition()[1]),str(truss.getPosition()[2]),
							str(truss.getEuler()[0]),str(truss.getEuler()[1]),str(truss.getEuler()[2]),
							int(truss.orientation.value)])
	
	cycleOrientation(cachedOrientation)
	
	# Save successful feedback
	runFeedbackTask('Save success!')
		
# Loads Build members' truss dimensions, position, rotation from './data/bridge#.csv'					
def LoadData():
	global BUILD_MEMBERS
	global SIDE_MEMBERS
	global TOP_MEMBERS
	global BOT_MEMBERS
	global SIDE_CLONES
	global ORDERS
	global GRAB_LINKS
	
	# Play MUTE
	clickSound.play()
	
	filePath = vizinput.fileOpen(filter=[('CSV Files','*.csv')],directory='./data/saves')		
	if filePath == '':
		return	

	clearMembers()
	
	cachedOrientation = ORIENTATION
	cycleOrientation(structures.Orientation.Side)
	cachedMode = MODE
	
	ORDERS = []
	with open(filePath,'rb') as f:
		reader = csv.reader(f)
		for row in reader:
			 order = Order(diameter=float(row[0]),thickness=float(row[1]),length=float(row[2]),quantity=int(row[3]))
			 order.pos = ( [float(row[4]), float(row[5]), float(row[6])] )
			 order.euler = ( [float(row[7]), float(row[8]), float(row[9])] )
			 order.orientation = structures.Orientation(int(row[10]))
			 ORDERS.append(order)
	
	generateMembers(loading=True)

	for truss in BUILD_MEMBERS:
		truss.isNewMember = False
		truss.orientation = truss.order.orientation
		truss.setPosition(truss.order.pos)
		if truss.orientation == structures.Orientation.Side:
			SIDE_MEMBERS.append(truss)
			truss.clonedSide = cloneSide(truss)
		elif truss.orientation == structures.Orientation.Top:
			TOP_MEMBERS.append(truss)
		elif truss.orientation == structures.Orientation.Bottom:
			BOT_MEMBERS.append(truss)
		truss.setEuler(truss.order.euler)
		link = viz.grab(bridge_root.getGroup(),truss)
		truss.link = link
		GRAB_LINKS.append(link)
		
	cycleOrientation(cachedOrientation)
	cycleMode(cachedMode)
	
	# Show load feedback
	runFeedbackTask('Load success!')

# Events
viz.callback ( viz.SLIDER_EVENT, onSlider )
viz.callback ( viz.LIST_EVENT, onList )

# Button callbacks
vizact.onbuttonup ( orderSideButton, addOrder, ORDERS_SIDE_GRID, ORDERS_SIDE, ORDERS_SIDE_ROWS, ORDERS_SIDE_FLAG )
vizact.onbuttonup ( orderSideButton, clickSound.play )
vizact.onbuttonup ( orderTopButton, addOrder, ORDERS_TOP_GRID, ORDERS_TOP, ORDERS_TOP_ROWS, ORDERS_TOP_FLAG )
vizact.onbuttonup ( orderTopButton, clickSound.play )
vizact.onbuttonup ( orderBottomButton, addOrder, ORDERS_BOT_GRID, ORDERS_BOT, ORDERS_BOT_ROWS, ORDERS_BOT_FLAG )
vizact.onbuttonup ( orderBottomButton, clickSound.play )
vizact.onbuttonup ( doneButton, populateInventory )
vizact.onbuttonup ( doneButton, clickSound.play )
#vizact.onbuttonup ( resetButton, clearBridge )
#vizact.onbuttonup ( resetButton, clickSound.play )
vizact.onbuttonup ( quitButton, quitGame )
vizact.onbuttonup ( quitButton, clickSound.play )
vizact.onbuttonup ( menuButton, onKeyUp, KEYS['showMenu'], )
vizact.onbuttonup ( homeButton, onKeyUp, KEYS['home'] )
vizact.onbuttonup ( buildModeButton, onKeyUp, KEYS['builder'] )
vizact.onbuttonup ( viewerModeButton, onKeyUp, KEYS['viewer'] )
vizact.onbuttonup ( walkModeButton, onKeyUp, KEYS['walk'] )
vizact.onbuttonup ( resetOriButton, onKeyUp, KEYS['reset'] )
vizact.onbuttonup ( toggleEnvButton, onKeyUp, KEYS['env'] )
vizact.onbuttonup ( toggleGridButton, onKeyUp, KEYS['grid'] )
#vizact.onbuttonup ( saveButton, SaveData )	#--Moved to after initialize
#vizact.onbuttonup ( loadButton, loadBridge )
vizact.onbuttonup ( soundButton, toggleAudio )

FLASH_TIME = 3.0			# Time to flash screen

def CreateFlashQuad():
	""" Create flash screen quad """
	flash_quad = viz.addTexQuad(parent=viz.ORTHO)
	flash_quad.color(viz.WHITE)
	flash_quad.drawOrder(-10)
	flash_quad.blendFunc(viz.GL_ONE,viz.GL_ONE)
	flash_quad.visible(False)
	flash_quad.setBoxTransform(viz.BOX_ENABLED)
	return flash_quad
flash_quad = CreateFlashQuad()


def FlashScreen():
	"""Flash screen and fade out"""
	flash_quad.visible(True)
	flash_quad.color(viz.WHITE)
	fade_out = vizact.fadeTo(viz.BLACK,time=FLASH_TIME,interpolate=vizact.easeOutStrong)
	flash_quad.runAction(vizact.sequence(fade_out,vizact.method.visible(False)))


def GrayEffect():
	# Create post process effect for blending to gray scale
	gray_effect = BlendEffect(None,GrayscaleEffect(),blend=0.0)
	gray_effect.setEnabled(False)
	vizfx.postprocess.addEffect(gray_effect)
	return gray_effect
gray_effect = GrayEffect()


def createConfirmButton():
	global doneButton
	bottomRow.removeItem(doneButton)
	doneButton = bottomRow.addItem(viz.addButtonLabel('Confirm order'),align=viz.ALIGN_CENTER_TOP)
	doneButton.length(2)
	vizact.onbuttonup ( doneButton, populateInventory )
	vizact.onbuttonup ( doneButton, clickSound.play )
	vizact.onbuttonup ( doneButton, cycleMode, structures.Mode.Build )
	vizact.onbuttonup ( doneButton, menuCanvas.visible, viz.OFF )


# Schedule tasks
def MainTask():
	global INITIALIZED
	viewChangeSound.play()	

	global glove
	glove = viz.addChild('glove.cfg')
	glove.disable(viz.INTERSECT_INFO_OBJECT)
	
#	viz.MainView.setPosition(START_POS)
	
	while True:		
		FlashScreen()
		
		yield viztask.waitButtonUp(doneButton)
		
		createConfirmButton()
		vizact.onbuttonup(orderSideButton,createConfirmButton)
		vizact.onbuttonup(orderTopButton,createConfirmButton)
		vizact.onbuttonup(orderBottomButton,createConfirmButton)
		
#		menuCanvas.visible(viz.OFF)
#		menuCanvas.setRenderWorldOverlay(RESOLUTION, fov=START_FOV, distance=3.0)
		bb = menuTabPanel.getBoundingBox()
		menuCanvas.setRenderWorld([bb.width * .8, bb.height + 55],[1,viz.AUTO_COMPUTE])
		menuTabPanel.selectPanel(0)
		
		bb = dialog.getBoundingBox()
		dialogCanvas.setRenderWorld([bb.width,bb.height],[1,viz.AUTO_COMPUTE])

#		dialogCanvas.setParent(menuCanvas)
#		dialogCanvas.setPosition(0,-2,2)
		feedbackCanvas.setPosition(0,-2,2)
		
		viz.clearcolor(CLEAR_COLOR)
		
		# Define globals
		global mouseTracker
		global gloveLink
		global highlightTool
		global playerNode
		global navigator
		
		# Setup callbacks
		viz.callback ( viz.KEYUP_EVENT, onKeyUp )
#		viz.callback ( viz.KEYDOWN_EVENT, onKeyDown )
		viz.callback ( viz.MOUSEUP_EVENT, onMouseUp )
		viz.callback ( viz.MOUSEDOWN_EVENT, onMouseDown )
#		viz.callback ( viz.MOUSEWHEEL_EVENT, onMouseWheel )
		viz.callback ( viz.SENSOR_UP_EVENT, onJoyButton )
		
		# Setup navigation
		import navigation
		joystickConnected = navigation.checkJoystick()
		oculusConnected = navigation.checkOculus()
		navigator = None
		
		if oculusConnected and joystickConnected:
			navigator = navigation.Joyculus()
			vizact.onsensorup( navigator.getSensor(), navigator.KEYS['mode'],cycleMode,vizact.choice([structures.Mode.Build,structures.Mode.Edit]))
			vizact.onsensorup( navigator.getSensor(), navigator.KEYS['orient'],cycleOrientation,vizact.choice([structures.Orientation.Top,structures.Orientation.Bottom,structures.Orientation.Side]))
			vizact.onsensorup( navigator.getSensor(), navigator.KEYS['angles'],cycleView,vizact.choice([0,1,2,3]))	
			vizact.onsensorup( navigator.getSensor(), navigator.KEYS['road'],toggleRoad,road)
			vizact.onsensorup( navigator.getSensor(), navigator.KEYS['stereo'],toggleStereo,vizact.choice([False,True]))		
			viz.callback( navigation.getExtension().HAT_EVENT, onHatChange )
			vizact.ontimer( 0,slideRootHat )	
			navigator.setAsMain()
		elif joystickConnected:
			navigator = navigation.Joystick()
			vizact.onsensorup( navigator.getSensor(), navigator.KEYS['mode'],cycleMode,vizact.choice([structures.Mode.Build,structures.Mode.Edit]))
			vizact.onsensorup( navigator.getSensor(), navigator.KEYS['orient'],cycleOrientation,vizact.choice([structures.Orientation.Top,structures.Orientation.Bottom,structures.Orientation.Side]))
			vizact.onsensorup( navigator.getSensor(), navigator.KEYS['angles'],cycleView,vizact.choice([0,1,2,3]))			
			vizact.onsensorup( navigator.getSensor(), navigator.KEYS['road'],toggleRoad,road)			
			vizact.onsensorup( navigator.getSensor(), navigator.KEYS['stereo'],toggleStereo,vizact.choice([False,True]))		
			viz.callback( navigation.getExtension().HAT_EVENT, onHatChange )
			vizact.ontimer( 0,slideRootHat )				
			navigator.setAsMain()
		elif oculusConnected:
			navigator = navigation.Oculus()
			vizact.onkeyup( navigator.KEYS['mode'],cycleMode,vizact.choice([structures.Mode.Build,structures.Mode.Edit]))
			vizact.onkeyup( navigator.KEYS['orient'],cycleOrientation,vizact.choice([structures.Orientation.Top,structures.Orientation.Bottom,structures.Orientation.Side]))
			vizact.onkeyup( navigator.KEYS['stereo'],toggleStereo,vizact.choice([False,True]))
			vizact.onkeyup( navigator.KEYS['angles'],cycleView,vizact.choice([0,1,2,3]))
			vizact.whilekeydown( navigator.KEYS['slideNear'],slideRoot,-SLIDE_INTERVAL )		
			vizact.whilekeydown( navigator.KEYS['slideFar'],slideRoot,SLIDE_INTERVAL )	
			navigator.setAsMain()
		else:
			navigator = navigation.KeyboardMouse()
			vizact.onkeyup( navigator.KEYS['mode'],cycleMode,vizact.choice([structures.Mode.Build,structures.Mode.Edit]))
			vizact.onkeyup( navigator.KEYS['orient'],cycleOrientation,vizact.choice([structures.Orientation.Top,structures.Orientation.Bottom,structures.Orientation.Side]))
			vizact.onkeyup( navigator.KEYS['angles'],cycleView,vizact.choice([0,1,2,3]) )
			vizact.onkeyup( navigator.KEYS['stereo'],toggleStereo,vizact.choice([False,True]))
			vizact.whilekeydown( navigator.KEYS['slideNear'],slideRoot,-SLIDE_INTERVAL)		
			vizact.whilekeydown( navigator.KEYS['slideFar'],slideRoot,SLIDE_INTERVAL)
			navigator.setAsMain()
		
		navigator.setOrigin(START_POS,[0,0,0])
		navigator.reset()
		
		initMouse()
		highlightTool.setUpdateFunction(updateHighlightTool)
		mouseTracker = initTracker(HAND_DISTANCE)
		gloveLink = viz.link(mouseTracker,glove)
		gloveLink.postMultLinkable(navigator.VIEW)
		viz.link(gloveLink,highlightTool)	
		
		#--Link inspector label to glove
		inspectorLink = viz.link(gloveLink,inspectorCanvas)
		inspectorLink.postTrans([0,-.2,0])
		inspectorCanvas.visible(False)
		
		vizact.ontimer(0,clampTrackerScroll,mouseTracker,SCROLL_MIN,SCROLL_MAX)
		
		rotationCanvas.setEuler( [0,30,0] )
		
		inventoryLink = viz.link(navigator.VIEW,inventoryCanvas)
		inventoryLink.postTrans([0,-0.5,0.75])
		inventoryLink.preEuler([0,30,0])		

		global CACHED_MODE
		CACHED_MODE = structures.Mode.View
		cycleMode(CACHED_MODE)		

		#--Show initial info message
		info_root.showInfoMessage(INITIAL_MESSAGE)
		
		#--Button callbacks
		vizact.onbuttonup ( saveButton, SaveData )
		vizact.onbuttonup ( loadButton, loadBridge )
		vizact.onbuttonup ( resetButton, clearBridge )
		vizact.onbuttonup ( resetButton, clickSound.play )
		
		#--Show menu
#		toggleMenu(True)
		
		INITIALIZED = True
viztask.schedule( MainTask() )

		
# Pre-load sounds
viz.playSound('./resources/sounds/return_to_holodeck.wav',viz.SOUND_PRELOAD)
viz.playSound('./resources/sounds/button_highlight.wav',viz.SOUND_PRELOAD) 
viz.playSound('./resources/sounds/click.wav',viz.SOUND_PRELOAD)
viz.playSound('./resources/sounds/show_menu.wav',viz.SOUND_PRELOAD)
viz.playSound('./resources/sounds/hide_menu.wav',viz.SOUND_PRELOAD)
viz.playSound('./resources/sounds/page_advance.wav',viz.SOUND_PRELOAD)
viz.playSound('./resources/sounds/out_of_bounds_warning.wav',viz.SOUND_PRELOAD)


def getAvatarOrientation(obj):
	print 'Pos:',obj.getPosition(),'Rot:',obj.getEuler()