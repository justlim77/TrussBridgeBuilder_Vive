﻿"""
This script demonstrates how to connect to 
a joystick device and handle state changes. 
The axes control the view position/rotation 
and the trigger button resets the view. 
""" 
import sys
import viz
import vizact
import vizconfig
#import oculus_08 as oculus
import oculus
import steamvr
import mathlite

# Navigator Base Class
class Navigator(object):
	def __init__(self):		
		# --Key commands
		self.KEYS = { 'forward'	: 'w'
					,'back' 	: 's'
					,'left' 	: 'a'
					,'right'	: 'd'
					,'down'		: 'z'
					,'up'		: 'x'
					,'reset'	: 'r'
					,'camera'	: 'c'
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
					,'proxi'	: 'p'
					,'collide'	: 'c'
					,'walk'		: ','
					,'angles'	: '.'
					,'road'		: 'n'
					,'esc'		: viz.KEY_ESCAPE
					,'stereo' 	: '='
					,'capslock'	: viz.KEY_CAPS_LOCK
					,'slideFar'	: '2'
					,'slideNear': '1'
		}
		self.MOVE_SPEED = 1.4
		self.MIN_SPEED = 0.7
		self.MAX_SPEED = 2.8
		self.STRAFE_SPEED = 2.0
		self.TURN_SPEED = 90
		self.ORIGIN_POS = [0,0,0]
		self.ORIGIN_ROT = [0,0,0]
		self.EYE_HEIGHT = 1.8
		self.FOV = 100
		self.CAN_ELEVATE = True
		self.CAN_STRAFE = True
		
		self.NODE = viz.addGroup()
		self.VIEW = viz.MainView

		self.VIEW_LINK = viz.link(self.NODE,self.VIEW)	
		
	# Setup functions		
	def getPosition(self):
#		return self.navigationNode.getPosition(viz.REL_PARENT)
		return self.NODE.getPosition()
		
	def setPosition(self,position):
#		self.navigationNode.setPosition(position, viz.REL_PARENT)
		self.NODE.setPosition(position)
					
	def getEuler(self):
		return self.NODE.getEuler()
		
	def setEuler(self,euler):
#		self.navigationNode.setEuler(euler, viz.REL_PARENT)
		self.NODE.setEuler(euler)	
	
	def getNode(self):
		return self.NODE
		
	def getView(self):
		return self.VIEW
	
	def getLink(self):		
		return self.VIEW_LINK
		
	def getKeys(self):
		return self.KEYS
	
	def getEyeHeight(self):
		return self.EYE_HEIGHT
	
	def setEyeHeight(self,height):
		self.EYE_HEIGHT = height

	def getMoveSpeed(self):
		return self.MOVE_SPEED
	
	def setMoveSpeed(self,speed):
		self.MOVE_SPEED = speed
		
	def getStrafeSpeed(self):
		return self.STRAFE_SPEED
	
	def setStrafeSpeed(self,speed):
		self.STRAFE_SPEED = speed	
		
	def getTurnSpeed(self):
		return self.TURN_SPEED
	
	def setTurnSpeed(self,speed):
		self.TURN_SPEED = speed
	
	def setNavAbility(self,strafe=True,elevate=True):
		self.CAN_STRAFE = strafe
		self.CAN_ELEVATE = elevate
		
	def setOrigin(self,pos,euler):
		self.ORIGIN_POS = pos
		self.ORIGIN_ROT = euler	
	
	def valid(self):
		return True
		
	def reset(self):
		self.NODE.setPosition(self.ORIGIN_POS)
		self.NODE.setEuler(self.ORIGIN_ROT)
	
	def resetOrientation(self):
		"""Implement if using HMD"""
		pass

	def updateView(self):
		pass
		
	def setAsMain(self):		
		pass
		
	def getLeftController(self):
		pass
		
	def getRightController(self):
		pass
		

class KeyboardMouse(Navigator):
	def __init__(self):
		super(self.__class__,self).__init__()
		
		#Override parameters
		self.ORIGIN_POS = [0,self.EYE_HEIGHT,0]
		
		#Override view link
		self.VIEW_LINK.remove()
		self.VIEW_LINK = viz.link(self.VIEW, self.NODE)
		
	def getPosition(self):
#		return self.navigationNode.getPosition(viz.REL_PARENT)
		return self.VIEW.getPosition()
		
	def setPosition(self,position):
#		self.navigationNode.setPosition(position, viz.REL_PARENT)
		self.VIEW.setPosition(position)
					
	def getEuler(self):
		return self.VIEW.getEuler()
		
	def setEuler(self,euler):
#		self.navigationNode.setEuler(euler, viz.REL_PARENT)
		self.VIEW.setEuler(euler)	
		
	# Setup functions				
	def updateView(self):
		yaw,pitch,roll = self.VIEW.getEuler()
		m = viz.Matrix.euler(yaw,0,0)
		dm = viz.getFrameElapsed() * self.MOVE_SPEED
		if viz.key.isDown(self.KEYS['forward']) and self.CAN_STRAFE:
			m.preTrans([0,0,dm])
		if viz.key.isDown(self.KEYS['back']) and self.CAN_STRAFE:
			m.preTrans([0,0,-dm])
		if viz.key.isDown(self.KEYS['left']) and self.CAN_STRAFE:
			m.preTrans([-dm,0,0])
		if viz.key.isDown(self.KEYS['right']) and self.CAN_STRAFE:
			m.preTrans([dm,0,0])
		if viz.key.isDown(self.KEYS['up']) and self.CAN_ELEVATE:
			m.preTrans([0,dm,0])
		if viz.key.isDown(self.KEYS['down']) and self.CAN_ELEVATE:
			m.preTrans([0,-dm,0])
		self.VIEW.setPosition(m.getPosition(), viz.REL_PARENT)
#		viz.logNotice('Node position:', self.getPosition())
		
	def reset(self):
		self.VIEW.setPosition(self.ORIGIN_POS)
		self.VIEW.setEuler(self.ORIGIN_ROT)
	
	def setAsMain(self):
		viz.logStatus("""Setting KeyboardMouse as main""")
		
		self.VIEW_LINK.preTrans([0,-self.EYE_HEIGHT,0])
		
		viz.mouse.setOverride(viz.ON) 
		viz.fov(self.FOV)

#		self.MOVE_SPEED = 2
		
		vizact.ontimer(0,self.updateView)
		vizact.onkeyup(self.KEYS['reset'],self.reset)
		
		def onMouseMove(e):
			euler = self.VIEW.getEuler(viz.HEAD_ORI)
			euler[0] += e.dx*0.05
			euler[1] += -e.dy*0.05
			euler[1] = viz.clamp(euler[1],-85.0,85.0)
			self.VIEW.setEuler(euler,viz.HEAD_ORI)
		viz.callback(viz.MOUSE_MOVE_EVENT, onMouseMove)	
		
# Joystick
_extension = None
def getExtension():
	"""Get Joystick extension object"""
	global _extension
	if _extension is None:
		_extension = viz.addExtension('DirectInput.dle')
	return _extension
	
def getDevices():
	"""Returns a list of all Joystick device objects"""
	return getExtension().getJoystickDevices()
	
class Joystick(Navigator):
	def __init__(self):
		super(self.__class__,self).__init__()
		
		# --Override Key commands
		self.KEYS = { 'forward'	: 'w'
					,'back' 	: 's'
					,'left' 	: 'a'
					,'right'	: 'd'
					,'camera'	: 'c'
					,'restart'	: viz.KEY_END
					,'home'		: viz.KEY_HOME
					,'utility'	: ' '
					,'reset'	: 0
					,'showMenu' : 1
					,'down'		: 2
					,'orient'	: 3
					,'up'		: 4
					,'mode'		: 5
					,'builder'	: 6
					,'walk'		: 7
					,'angles'	: 8
					,'road'		: 10
					,'esc'		: 999
					,'slideFar'	: 0
					,'slideNear': 180
					,'env'		: '-'
					,'grid'		: '-'
					,'snapMenu'	: viz.KEY_CONTROL_L
					,'interact' : viz.MOUSEBUTTON_LEFT
					,'rotate'	: viz.MOUSEBUTTON_RIGHT
					,'proxi'	: 'p'
					,'viewer'	: 'o'
					,'collide'	: 'c'
					,'stereo' 	: 'm'
					,'hand'		: 'h'
					,'capslock'	: viz.KEY_CAPS_LOCK
		}
		
		# Get device from extension if not specified
		self.device = None
		if self.device is None:
			allDevices = getDevices()
			if allDevices:
				self.device = allDevices[0]	
			else:
				viz.logError('** ERROR: Failed to detect Joystick')

		# Connect to selected device
		self.joy = getExtension().addJoystick(self.device)
		if not self.joy:
			viz.logError('** ERROR: Failed to connect to Joystick')
			return None

		# Set dead zone threshold so small movements of joystick are ignored
		self.joy.setDeadZone(0.2)
		
		#Override parameters
		self.ORIGIN_POS = [0,self.EYE_HEIGHT,0]
		self.VIEW_LINK.remove()
		self.VIEW_LINK = viz.link(self.VIEW,self.NODE)
			
	def onSliderChange(self,e):
		val = mathlite.getNewRange(e.value,1,-1,self.MIN_SPEED,self.MAX_SPEED)
		self.MOVE_SPEED = val
	
	def getPosition(self):
		return self.VIEW_LINK.getPosition()
		
	def setPosition(self,position):
#		self.navigationNode.setPosition(position, viz.REL_PARENT)
		self.VIEW_LINK.setPosition(position)

	def getEuler(self):
		return self.VIEW.getEuler()
		
	def setEuler(self,euler):
#		self.navigationNode.setEuler(euler, viz.REL_PARENT)
		self.VIEW.setEuler(euler)	
		
	def reset(self):
		self.VIEW.setPosition(self.ORIGIN_POS)
		self.VIEW.setEuler(self.ORIGIN_ROT)	
		
	# Horizontal (X) axis controls yaw
	# Vertical (Y) axis controls position
	def updateView(self):
		""" Use joystick axes to move joystick node"""
		elapsed = viz.elapsed()
		x,y,z = self.joy.getPosition()
		twist = self.joy.getTwist()
		elevation_amount = 0
		if self.joy.isButtonDown(self.KEYS['up'])  and self.CAN_ELEVATE:
			elevation_amount = self.MOVE_SPEED * elapsed
		if self.joy.isButtonDown(self.KEYS['down']) and self.CAN_ELEVATE:
			elevation_amount = -self.MOVE_SPEED * elapsed
		move_amount = 0
		if self.CAN_STRAFE:
			self.MOVE_SPEED * elapsed
		self.VIEW.setPosition([x*move_amount,elevation_amount,y*move_amount], viz.REL_LOCAL)

	def getSensor(self):
		return self.joy
	
	def valid(self):
		if not self.joy.valid():
			return False
		else:
			return True
	
	def setAsMain(self):
#		self.VIEW_LINK.setOffset([0,self.EYE_HEIGHT,0])
		self.VIEW_LINK.preTrans([0,-self.EYE_HEIGHT,0])
		
		viz.mouse.setOverride(viz.ON) 
		viz.fov(self.FOV)
		
		val = mathlite.getNewRange(self.joy.getSlider(),1,-1,self.MIN_SPEED,self.MAX_SPEED)
		self.MOVE_SPEED = val
		
		vizact.ontimer(0, self.updateView)
		vizact.onsensorup(self.joy, self.KEYS['reset'], self.reset)
		viz.callback(getExtension().SLIDER_EVENT,self.onSliderChange)
		
		def onMouseMove(e):
			euler = self.VIEW.getEuler()
			euler[0] += e.dx*0.05
			euler[1] += -e.dy*0.05
			euler[1] = viz.clamp(euler[1],-85.0,85.0)
			self.VIEW.setEuler(euler)
		viz.callback(viz.MOUSE_MOVE_EVENT, onMouseMove)	

class Oculus(Navigator):
	def __init__(self):		
		super(self.__class__,self).__init__()
		
		# Link navigation node to main view
#		self.NODE = viz.addGroup()
#		self.VIEW_LINK = viz.link(self.NODE, self.VIEW)
		
		# --add oculus as HMD
		self.hmd = oculus.Rift()
		
		if not self.hmd.getSensor():
			viz.logError('** ERROR: Failed to detect Oculus Rift')
		else:
			# Reset HMD orientation
			self.hmd.getSensor().reset()

			# Setup navigation node and link to main view
#			self.NODE = viz.addGroup()
#			self.VIEW_LINK = viz.link(self.NODE, viz.VIEW)
			self.VIEW_LINK.preMultLinkable(self.hmd.getSensor())

			# --Apply user profile eye height to view
			profile = self.hmd.getProfile()
			if profile:
				self.VIEW_LINK.setOffset([0,profile.eyeHeight,0])
				viz.logNotice('Oculus profile name:', profile.name)
				viz.logNotice('Oculus IPD:', profile.ipd)
				viz.logNotice('Oculus player height:', profile.playerHeight)
				viz.logNotice('Oculus eye height:', profile.eyeHeight)
			else: 
				self.VIEW_LINK.setOffset([0,self.EYE_HEIGHT,0])
				
			# Check if HMD supports position tracking
			supportPositionTracking = self.hmd.getSensor().getSrcMask() & viz.LINK_POS
			if supportPositionTracking:
				
				# Add camera bounds model
				self.camera_bounds = self.hmd.addCameraBounds()
				self.camera_bounds.visible(False)

				# Change color of bounds to reflect whether position was tracked
				def checkPositionTracked():
					if self.hmd.getSensor().getStatus() & oculus.STATUS_POSITION_TRACKED:
						self.camera_bounds.color(viz.GREEN)
					else:
						self.camera_bounds.color(viz.RED)
				vizact.onupdate(0, checkPositionTracked)

				# Setup camera bounds toggle key
				def toggleBounds():
					self.camera_bounds.visible(viz.TOGGLE)
				vizact.onkeydown(self.KEYS['camera'], toggleBounds)

	def valid(self):
		if not self.hmd.getSensor().valid:
			return False
		else: 
			return True
		
	# Setup functions				
	def reset(self):
		super(self.__class__,self).reset()
		self.hmd.getSensor().reset()
		
	def updateView(self):
		yaw,pitch,roll = self.VIEW_LINK.getEuler()
		m = viz.Matrix.euler(yaw,0,0)
		dm = viz.getFrameElapsed() * self.MOVE_SPEED
		if viz.key.isDown(self.KEYS['forward']) and self.CAN_STRAFE:
			m.preTrans([0,0,dm])
		if viz.key.isDown(self.KEYS['back']) and self.CAN_STRAFE:
			m.preTrans([0,0,-dm])
		if viz.key.isDown(self.KEYS['left']) and self.CAN_STRAFE:
			m.preTrans([-dm * self.STRAFE_SPEED,0,0])
		if viz.key.isDown(self.KEYS['right']) and self.CAN_STRAFE:
			m.preTrans([dm * self.STRAFE_SPEED,0,0])
		if viz.key.isDown(self.KEYS['up']) and self.CAN_ELEVATE:
			m.preTrans([0,dm,0])
		if viz.key.isDown(self.KEYS['down']) and self.CAN_ELEVATE:
			m.preTrans([0,-dm,0])
		self.NODE.setPosition(m.getPosition(), viz.REL_PARENT)

	def setAsMain(self):
		self.MOVE_SPEED = 2.0	

		vizact.ontimer(0,self.updateView)
		vizact.onkeyup(self.KEYS['reset'], self.reset)
		
class SteamVR(Navigator):
	def __init__(self):		
		super(self.__class__,self).__init__()
		
	# --Override Key commands
		self.KEYS = { 'forward'	: 'w'
					,'back' 	: 's'
					,'left' 	: 'a'
					,'right'	: 'd'
					,'camera'	: 'c'
					,'elevate'	: steamvr.BUTTON_TRACKPAD	#4	
					,'restart'	: viz.KEY_HOME
					,'home'		: steamvr.BUTTON_GRIP
					,'utility'	: steamvr.BUTTON_MENU		#0
					,'reset'	: steamvr.BUTTON_GRIP		#1
					,'reorient'	: steamvr.BUTTON_GRIP
					,'showMenu' : ' '
					,'down'		: 2
					,'orient'	: 3
					,'up'		: 4
					,'mode'		: 5
					,'builder'	: 6
					,'walk'		: 7
					,'angles'	: 8
					,'road'		: 10
					,'esc'		: viz.KEY_ESCAPE
					,'slideFar'	: 0
					,'slideNear': 180
					,'env'		: 't'
					,'grid'		: 'g'
					,'snapMenu'	: viz.KEY_CONTROL_L
					,'interact' : steamvr.BUTTON_TRIGGER
					,'rotate'	: viz.MOUSEBUTTON_RIGHT
					,'proxi'	: 'p'
					,'viewer'	: 'o'
					,'collide'	: 'c'
					,'stereo' 	: 'm'
		}		
		
		# Link navigation node to main view
#		self.NODE = viz.addGroup()
#		self.VIEW_LINK = viz.link(self.NODE, self.VIEW)
		
		# --add oculus as HMD
		self.hmd = steamvr.HMD()
		
		if not self.hmd.getSensor():
			viz.logError('** ERROR: Failed to detect SteamVR HMD')
		else:
			# Reset HMD orientation
			self.hmd.getSensor().reset()

			# Setup navigation node and link to main view
#			self.NODE = viz.addGroup()
#			self.VIEW_LINK = viz.link(self.NODE, viz.VIEW)
			self.VIEW_LINK.preMultLinkable(self.hmd.getSensor())

#			# --Apply user profile eye height to view

			viz.logNotice('SteamVR IPD:', self.hmd.getIPD())
			viz.logNotice('SteamVR hidden area mesh visible:', self.hmd.getHiddenAreaMeshVisible())
			
			controllerList = steamvr.getControllerList()
			self.LEFT_CONTROLLER = controllerList[0]
			self.RIGHT_CONTROLLER = controllerList[1]
			
			# Add controllers
			for controller in controllerList:

				# Create model for controller
				controller.model = controller.addModel(parent=self.getNode())
				controller.model.disable(viz.INTERSECTION)
				controller.link = viz.link(controller, controller.model)

				# Create pointer line for controller
				viz.startLayer(viz.LINES)
				viz.vertexColor(viz.CYAN)
				viz.vertex([0,0,0])
				viz.vertex([0,0,100])
				controller.line = viz.endLayer(parent=controller.model)
				controller.line.disable([viz.INTERSECTION, viz.SHADOW_CASTING])
				controller.line.visible(True)
																		
				# Log controller name
				viz.logNotice(controller.getName())
				
				# Display joystick information in config window
				vizconfig.register(controller)
				
			# Create highlighter tool for right ontroller
			from tools import highlighter
			from tools import ray_caster
			ray = ray_caster.Simple3DRay(0.001)
			ray.setColor(viz.CYAN)
			rayCaster = ray_caster.RayCaster()
			rayCaster.setIntersectAll(False)
			rayCaster.setStartingOffset([0,0,0])
			rayCaster.setRay(ray)
			self.HIGHLIGHTER = highlighter.Highlighter()
			self.HIGHLIGHTER.setRayCaster(rayCaster)
			self.HIGHLIGHTER.setParent(self.RIGHT_CONTROLLER.model)
#				link.preTrans([0, -0.3, 1.0])
			self.HIGHLIGHTER.getHighlight().setColor(viz.CYAN)
			
			# Disable left controller line
			self.LEFT_CONTROLLER.line.visible(False)
			
#				highlightLink = viz.link(self.getRightController().link,self.highlightTool)
#			def updateHighlightTool(tool):
#				tool.highlight()
#			self.HIGHLIGHTER.setUpdateFunction(updateHighlightTool)						
				# Setup task for triggering jumps using controller
#				viztask.schedule(JumpTask(controller))

	def getHighlighter(self):
		return self.HIGHLIGHTER
			
	def getLeftController(self):
		return self.LEFT_CONTROLLER
		
	def getRightController(self):
		return self.RIGHT_CONTROLLER
	
	def resetOrientation(self):
		self.hmd.getSensor().reset()
		
	def valid(self):
		if not self.hmd.getSensor().valid:
			return False
		else: 
			return True
		
	# Setup functions				
	def reset(self):
		super(self.__class__,self).reset()
		self.hmd.getSensor().reset()
		self.CAN_ELEVATE = False
		
	def updateView(self):
		yaw,pitch,roll = self.VIEW_LINK.getEuler()
		m = viz.Matrix.euler(yaw,0,0)
		dm = viz.getFrameElapsed() * self.MOVE_SPEED
		x,y,z = [0,0,0]
		if self.CAN_ELEVATE is True:
			y = self.getLeftController().getTrackpad()[1]
		else:
			x,z = self.getLeftController().getTrackpad()
			
#		self.NODE.setPosition([x * dm, y * dm, z * dm], viz.REL_PARENT)
		if self.CAN_ELEVATE is True:
			m.preTrans([0, dm * self.getLeftController().getTrackpad()[1], 0])
		else:
			m.preTrans([dm * self.getLeftController().getTrackpad()[0] * 1.5,
						0,
						dm * self.getLeftController().getTrackpad()[1]])
		
		self.NODE.setPosition(m.getPosition(), viz.REL_PARENT)
		
	def setAsMain(self):
		self.MOVE_SPEED = 2.0	
		self.CAN_ELEVATE = False
		
		vizact.ontimer(0,self.updateView)
#		vizact.onsensordown(self.getLeftController(), self.KEYS['reset'], self.reset) 
#		vizact.onsensordown(self.getRightController(), self.KEYS['reset'], self.reset) 
		def ToggleElevation(val):
			self.CAN_ELEVATE = val
			print self.CAN_ELEVATE
			
		vizact.onsensordown(self.getLeftController(), self.KEYS['elevate'], ToggleElevation, True)
		vizact.onsensorup(self.getLeftController(), self.KEYS['elevate'], ToggleElevation, False)
		
				
	def IntersectController(self, controller):
		"""Perform intersection using controller"""
		line = controller.model.getLineForward(viz.ABS_GLOBAL, length=100.0)
		return viz.intersect(line.begin, line.end)


class Joyculus(Navigator):
	def __init__(self):		
		super(self.__class__,self).__init__()
	
		# --Override Key commands
		self.KEYS = { 'forward'	: 'w'
					,'back' 	: 's'
					,'left' 	: 'a'
					,'right'	: 'd'
					,'camera'	: 'c'
					,'restart'	: viz.KEY_END
					,'home'		: viz.KEY_HOME
					,'utility'	: ' '
					,'reset'	: 0
					,'showMenu' : 1
					,'down'		: 2
					,'orient'	: 3
					,'up'		: 4
					,'mode'		: 5
					,'builder'	: 6
					,'walk'		: 7
					,'angles'	: 8
					,'road'		: 10
					,'esc'		: 999
					,'slideFar'	: 0
					,'slideNear': 180
					,'env'		: '-'
					,'grid'		: '-'
					,'snapMenu'	: viz.KEY_CONTROL_L
					,'interact' : viz.MOUSEBUTTON_LEFT
					,'rotate'	: viz.MOUSEBUTTON_RIGHT
					,'proxi'	: 'p'
					,'viewer'	: 'o'
					,'collide'	: 'c'
					,'stereo' 	: 'm'
					,'hand'		: 'h'
					,'capslock'	: viz.KEY_CAPS_LOCK
		}
		
		self.TURN_SPEED = 45
		
		# Get device from extension if not specified
		self.device = None
		if self.device is None:
			allDevices = getDevices()
			if allDevices:
				self.device = allDevices[0]	
			else:
				viz.logError('** ERROR: Failed to detect Joystick')

		# Connect to selected device
		self.joy = getExtension().addJoystick(self.device)
		if not self.joy:
			viz.logError('** ERROR: Failed to connect to Joystick')

		# Set dead zone threshold so small movements of joystick are ignored
		self.joy.setDeadZone(0.2)

		# Display joystick information in config window
#		vizconfig.register(self.joy)
#		vizconfig.getConfigWindow().setWindowVisible(True)
		
		# --add oculus as HMD
		self.hmd = oculus.Rift()
		
		if not self.hmd.getSensor():
			viz.logError('** ERROR: Failed to detect Oculus')
		else:
			# Reset HMD orientation
			self.hmd.getSensor().reset()

			# Setup navigation node and link to main view
			self.VIEW_LINK.preMultLinkable(self.hmd.getSensor())

			# --Apply user profile eye height to view
			profile = self.hmd.getProfile()
			if profile:
				self.VIEW_LINK.setOffset([0,profile.eyeHeight,0])
				viz.logNotice('Oculus profile name:', profile.name)
				viz.logNotice('Oculus IPD:', profile.ipd)
				viz.logNotice('Oculus player height:', profile.playerHeight)
				viz.logNotice('Oculus eye height:', profile.eyeHeight)
			else: 
				self.VIEW_LINK.setOffset([0,self.EYE_HEIGHT,0])
				
			# Check if HMD supports position tracking
			supportPositionTracking = self.hmd.getSensor().getSrcMask() & viz.LINK_POS
			if supportPositionTracking:
				
				# Add camera bounds model
				self.camera_bounds = self.hmd.addCameraBounds()
				self.camera_bounds.visible(False)

				# Change color of bounds to reflect whether position was tracked
				def checkPositionTracked():
					if self.hmd.getSensor().getStatus() & oculus.STATUS_POSITION_TRACKED:
						self.camera_bounds.color(viz.GREEN)
					else:
						self.camera_bounds.color(viz.RED)
				vizact.onupdate(0, checkPositionTracked)

				# Setup camera bounds toggle key
				def toggleBounds():
					self.camera_bounds.visible(viz.TOGGLE)
				vizact.onkeydown(self.KEYS['camera'], toggleBounds)
				
	# Setup functions
	def getSensor(self):
		return self.joy
		
	def getHMD(self):
		return self.hmd
	
	def onSliderChange(self,e):
		val = mathlite.getNewRange(e.value,1,-1,self.MIN_SPEED,self.MAX_SPEED)
		self.MOVE_SPEED = val
	
	def resetOrientation(self):
		self.hmd.getSensor().reset()
	
	def reset(self):
		super(self.__class__,self).reset()
		self.hmd.getSensor().reset()
		
	def updateView(self):
		elapsed = viz.elapsed()
		x,y,z = self.joy.getPosition()
		twist = self.joy.getTwist()
		elevation_amount = 0
		if self.joy.isButtonDown(self.KEYS['up']) and self.CAN_ELEVATE:
			elevation_amount = self.MOVE_SPEED * elapsed
		if self.joy.isButtonDown(self.KEYS['down']) and self.CAN_ELEVATE:
			elevation_amount = -self.MOVE_SPEED * elapsed
		move_amount = 0
		if self.CAN_STRAFE:
			move_amount = self.MOVE_SPEED * elapsed
#		self.NODE.setPosition([0, 0, y * self.MOVE_SPEED * viz.getFrameElapsed()], viz.REL_LOCAL)
		self.NODE.setPosition([x*move_amount,elevation_amount,y*move_amount], viz.REL_LOCAL)
		turn_amount = self.TURN_SPEED * elapsed
		self.NODE.setEuler([twist*turn_amount,0,0], viz.REL_LOCAL)
#		self.NODE.setEuler([x * self.TURN_SPEED * , 0, 0], viz.REL_LOCAL)

	def setAsMain(self):
		viz.logStatus('Setting Joyculus as main')

		val = mathlite.getNewRange(self.joy.getSlider(),1,-1,self.MIN_SPEED,self.MAX_SPEED)
		self.MOVE_SPEED = val
		
		vizact.onsensordown(self.joy,self.KEYS['reset'],self.reset)
		vizact.ontimer(0,self.updateView)
		viz.callback(getExtension().SLIDER_EVENT,self.onSliderChange)
		
# Check for devices
def checkOculus():
	hmd = oculus.Rift()
	if not hmd.getSensor():
		return False
	return True

def checkJoystick():
	allDevices = getDevices()
	if allDevices:
		device = allDevices[0]	
		return True
	else:
		return False
		
def checkSteamVR():
	hmd = steamvr.HMD()
	if not hmd.getSensor():
		return False
	return True

def getNavigator():
	steamVRConnected = checkSteamVR()
	joystickConnected = checkJoystick()
	oculusConnected = checkOculus()
	
	if steamVRConnected:
		nav = SteamVR()	
		nav.getRightController().line.visible(False)
	elif oculusConnected and joystickConnected:
		nav = Joyculus()
	elif joystickConnected:
		nav = Joystick()
		# Display joystick information in config window
		vizconfig.register(nav.getSensor())
		vizconfig.getConfigWindow().setWindowVisible(True)
	elif oculusConnected:
		nav = Oculus()
	else:
		nav = KeyboardMouse()
	nav.setAsMain()
	return nav

if __name__ == '__main__':		
	# Run scene
	viz.setMultiSample(8)
	viz.setOption('viz.dwm_composition',viz.OFF)
	viz.go()	
	
	nav = getNavigator()
 
	nav.setPosition([0,0,0])
	def printPos():
		print nav.getPosition()
	vizact.onkeyup(' ',printPos)
	
	viz.MainView.getHeadLight().disable()
	sky_light = viz.addDirectionalLight(euler=(0,90,0), color=viz.WHITE)
	sky_light.setShadowMode(viz.SHADOW_DEPTH_MAP)
	
#	viz.mouse(viz.OFF)
#	viz.mouse.setVisible(False)
	viz.mouse.setTrap()

	# Add environment
	maze = viz.addChild('maze.osgb')
	maze.hint(viz.OPTIMIZE_INTERSECT_HINT)
	maze.disable(viz.SHADOW_CASTING)
	
	vizconfig.getConfigWindow().setWindowVisible(True)
	
	# Add directions to canvas
	canvas = viz.addGUICanvas(pos=[0, 3.0, 6.0])
	canvas.setMouseStyle(0)
	canvas.alignment(viz.ALIGN_CENTER)
	canvas.setRenderWorld([400,400], [5.0,5.0])

	import vizshape
	plane = vizshape.addPlane(size=(20,10))
	plane.setPosition(0,5,5)
	plane.setEuler(0,-90,0)
	def getIntersectInfo():
		info = nav.IntersectController(nav.getRightController())
		print info.intersectPoint
	vizact.ontimer(0,getIntersectInfo)
