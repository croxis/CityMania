from panda3d.core import Vec3,Vec2
from direct.showbase import DirectObject
from direct.task import Task
import math

import gui
picker = gui.getPicker()

class Camera(DirectObject.DirectObject):
    '''
    Camera Object which will be used.
    Desired Function (for "2.5D" engine):
        Camera always oriented to the isometric North
        No camera rotation
        No camera zoom (wont be important when in orthographic mode)
        Edge screen panning
        Middle mouse panning
    '''
    def __init__(self, size, terrain, isometric = False):
        '''
        '''
        self.dz=.5
        #center=(len(self.ancestor.terrain.data)/2,len(self.ancestor.terrain.data[0])/2,self.dz)
        base.disableMouse()
        #base.camLens.setFov(50)
        #base.camera.setPos(-center[0]*2,-center[1]*2,5)
        base.camera.setPos(size[0]/2.0, size[1]/2.0, 130)
        base.camera.setHpr(30,-45,0)
        self.isometric = isometric
        self.terrain = terrain
        
        if isometric:
            lens = OrthographicLens()
            lens.setFilmSize(6)
            base.cam.node().setLens(lens)
            
        self.camDist = 40
        # A variable that will determine how far the camera is from it's target focus
        #self.panLimitsX = Vec2(-20, size[0] + 20)
        #self.panLimitsY = Vec2(-20, size[1] + 20)
        self.panLimitsX = Vec2(0, size[0])
        self.panLimitsY = Vec2(0, size[1])
        # These two variables will serve as limits for how far the camera can pan, so you don't scroll away from the map.
        self.panRateDivisor = 20
        # This variable is used as a divisor when calculating how far to move the camera when panning. 
        # Higher numbers will yield slower panning
        # and lower numbers will yield faster panning. This must not be set to 0.

        self.panZoneSize = .15
        # This variable controls how close the mouse cursor needs to be to the edge of the screen to start panning the camera.
        # It must be less than 1,
        # and I recommend keeping it less than .2 
        
        self.target=Vec3()
        self.setTarget()
        self.isPanning = False
        self.isOrbiting = False
        self.accept('enterCityView', self.enterCity)
        self.accept('mouse2', self.middleMouseDown, [])
        self.accept('mouse2-up', self.middleMouseUp, [])
        # TODO: Consider using mouse 3 to focus on location
        #self.accept('mouse3', self.rightMouseDown, [])
        #self.accept('mouse3-up', self.rightMouseUp, [])
        self.accept("wheel_up",lambda : self.adjustCamDist(0.9))
        self.accept("wheel_down",lambda : self.adjustCamDist(1.1))
        self.accept('camera-up', self.panY, ['up'])
        self.accept('camera-down', self.panY, ['down'])
        self.accept('camera-left', self.panX, ['left'])
        self.accept('camera-right', self.panX, ['right'])
        
        taskMgr.add(self.update,"updateCameraTask")
    
    def middleMouseDown(self):
        # This function puts the camera into orbiting mode.
        self.mousePosition0=[base.win.getPointer(0).getX(),base.win.getPointer(0).getY()]
        self.setTarget()
        self.isOrbiting=True
        # Sets the orbiting variable to true to designate orbiting mode as on.
        
    def middleMouseUp(self):
        # This function takes the camera out of orbiting mode.
        self.isOrbiting=False
        # Sets the orbiting variable to false to designate orbiting mode as off.
    
    def rightMouseDown(self):
        self.mousePosition0=[base.win.getPointer(0).getX(),base.win.getPointer(0).getY()]
        self.isPanning = True
        
    def rightMouseUp(self):
        self.setTarget()
        self.isPanning = False
    
    def adjustCamDist(self,distFactor):
        '''This function increases or decreases the distance between the camera and the target position to simulate zooming in and out.
        The distFactor input controls the amount of camera movement.
        For example, inputing 0.9 will set the camera to 90% of it's previous distance.
        '''
        terrainCoords = picker.getCoords()
        if not terrainCoords: return
        terrainCoords.setZ(terrainCoords[2]*self.terrain.getRoot().getSz())
        vector = base.camera.getPos() - terrainCoords
        # Make sure we don't zoom out too far for a performance hit
        # TODO: Make this user defined in performance settings
        if (vector*distFactor)[2] > 200: return
        newPos = terrainCoords + (vector*distFactor)
        base.camera.setPos(newPos)
        self.setTarget()
        #self.turnCameraAroundPoint(0,0)
    
    def update(self, task):
        if self.isOrbiting:
            # Checks to see if the camera is in orbiting mode. Orbiting mode overrides panning, because it would be problematic if, while
            # orbiting the camera the mouse came close to the screen edge and started panning the camera at the same time.
            mousePosition1=[base.win.getPointer(0).getX(),base.win.getPointer(0).getY()]
            delta = [(mousePosition1[0]- self.mousePosition0[0])*0.005, (mousePosition1[1] - self.mousePosition0[1]) * 0.005]
            self.turnCameraAroundPoint(delta[0], delta[1])
        elif base.mouseWatcherNode.hasMouse():
            # If the mouse is outside the window, we skip
            mousePosition1 = [base.win.getPointer(0).getX(),base.win.getPointer(0).getY()]
            mpos = base.mouseWatcherNode.getMouse() 
            moveX = False
            moveY = False
            delta = [0,0]
            if mpos[0] < (-1 + self.panZoneSize):
                #print "Left"
                angleradiansX2 = base.camera.getH() * (math.pi / 180.0)-math.pi*0.5 
                delta[0] = (1 + mpos[0] - self.panZoneSize) * (self.camDist / self.panRateDivisor) 
                moveX = True
            if mpos[0] > (1 - self.panZoneSize):
                #print "Right"
                angleradiansX2 = base.camera.getH() * (math.pi / 180.0)+math.pi*0.5 
                delta[0] = (1 - mpos[0] - self.panZoneSize) * (self.camDist / self.panRateDivisor) 
                moveX = True
            if mpos[1] < (-1 + self.panZoneSize):
                #print "Down"
                angleradiansX1 = base.camera.getH() * (math.pi / 180.0)+math.pi 
                delta[1] = (1 + mpos[1] - self.panZoneSize) * (self.camDist / self.panRateDivisor) 
                moveY = True
            if mpos[1] > (1 - self.panZoneSize):
                #print "Up"
                angleradiansX1 = base.camera.getH() * (math.pi / 180.0) 
                delta[1] = (1 - mpos[1] - self.panZoneSize) * (self.camDist / self.panRateDivisor) 
                moveY = True
            if moveX or moveY:
                self.setTarget()
            if moveY:
                tempX = self.target.getX()+math.sin(angleradiansX1)*delta[1]
                tempX = self.clamp(tempX, self.panLimitsX.getX(), self.panLimitsX.getY())
                self.target.setX(tempX)
                tempY = self.target.getY()-math.cos(angleradiansX1)*delta[1]
                tempY = self.clamp(tempY, self.panLimitsY.getX(), self.panLimitsY.getY())
                self.target.setY(tempY)
                self.turnCameraAroundPoint(0,0)
            if moveX:
                tempX = self.target.getX()-math.sin(angleradiansX2)*delta[0]
                tempX = self.clamp(tempX, self.panLimitsX.getX(), self.panLimitsX.getY())
                self.target.setX(tempX)
                tempY = self.target.getY()+math.cos(angleradiansX2)*delta[0]
                tempY = self.clamp(tempY, self.panLimitsY.getX(), self.panLimitsY.getY())
                self.target.setY(tempY)
                self.turnCameraAroundPoint(0,0)
        return Task.cont
    
    def panX(self, direction):
        delta = 0
        if direction == 'left':
            angleradiansX2 = base.camera.getH() * (math.pi / 180.0)-math.pi*0.5 
            delta =  -self.panZoneSize * (self.camDist / self.panRateDivisor) 
        if direction == 'right':
            angleradiansX2 = base.camera.getH() * (math.pi / 180.0)+math.pi*0.5 
            delta = -self.panZoneSize * (self.camDist / self.panRateDivisor) 
        tempX = self.target.getX()-math.sin(angleradiansX2)*delta
        tempX = self.clamp(tempX, self.panLimitsX.getX(), self.panLimitsX.getY())
        self.target.setX(tempX)
        tempY = self.target.getY()+math.cos(angleradiansX2)*delta
        tempY = self.clamp(tempY, self.panLimitsY.getX(), self.panLimitsY.getY())
        self.target.setY(tempY)
        self.turnCameraAroundPoint(0,0)
    
    def panY(self, direction):
        delta = 0
        if direction == 'down':
            angleradiansX1 = base.camera.getH() * (math.pi / 180.0)+math.pi 
            delta = -self.panZoneSize * (self.camDist / self.panRateDivisor) 
        if direction == 'up':
            angleradiansX1 = base.camera.getH() * (math.pi / 180.0) 
            delta = -self.panZoneSize * (self.camDist / self.panRateDivisor) 
        tempX = self.target.getX()+math.sin(angleradiansX1)*delta
        tempX = self.clamp(tempX, self.panLimitsX.getX(), self.panLimitsX.getY())
        self.target.setX(tempX)
        tempY = self.target.getY()-math.cos(angleradiansX1)*delta
        tempY = self.clamp(tempY, self.panLimitsY.getX(), self.panLimitsY.getY())
        self.target.setY(tempY)
        self.turnCameraAroundPoint(0,0)
    
    def turnCameraAroundPoint(self,deltaX,deltaY):
        # This function performs two important tasks. First, it is used for the camera orbital movement.
        # It is also called with 0s for the rotation inputs to reposition the camera during the
        # panning and zooming movements.
        # The delta inputs represent the change in rotation of the camera, which is also used to determine how far the camera
        # actually moves along the orbit.
        newCamHpr = Vec3()
        newCamPos = Vec3()
        # Creates temporary containers for the new rotation and position values of the camera.
        
        camHpr=base.camera.getHpr()
        # Creates a container for the current HPR of the camera and stores those values.
        newCamHpr.setX(camHpr.getX()+deltaX)
        newCamHpr.setY(self.clamp(camHpr.getY()-deltaY, -85, 20))
        newCamHpr.setZ(camHpr.getZ())
        # Adjusts the newCamHpr values according to the inputs given to the function. The Y value is clamped to prevent
        # the camera from orbiting beneath the ground plane and to prevent it from reaching the apex of the orbit, which
        # can cause a disturbing fast-rotation glitch.
        
        base.camera.setHpr(newCamHpr)
        # Sets the camera's rotation to the new values.
        
        angleradiansX = newCamHpr.getX() * (math.pi / 180.0)
        angleradiansY = newCamHpr.getY() * (math.pi / 180.0)
        # Generates values to be used in the math that will calculate the new position of the camera.
        newCamPos.setX(self.camDist*math.sin(angleradiansX)*math.cos(angleradiansY)+self.target.getX())
        newCamPos.setY(-self.camDist*math.cos(angleradiansX)*math.cos(angleradiansY)+self.target.getY())
        newCamPos.setZ(-self.camDist*math.sin(angleradiansY)+self.target.getZ())
        # Check elevation and make sure we are not below terrain or water line
        pos = base.camera.getPos()
        root = self.terrain.getRoot()
        #elevation = self.terrain.getElevation(pos[0], pos[1]) * root.getSz()
        elevation = self.terrain.getElevation(pos[0]/5, pos[1]/5) * self.terrain.getSz()
        # Factor is height we want above terrain
        factor = 2
        if base.camera.getPos().getZ() < 22 + factor:
            newCamPos.setZ(22 + factor)
        elif newCamPos.getZ() < elevation + factor:
            newCamPos.setZ(elevation + factor)            
        
        base.camera.setPos(newCamPos.getX(),newCamPos.getY(),newCamPos.getZ())
        # Performs the actual math to calculate the camera's new position and sets the camera to that position.
        #Unfortunately, this math is over my head, so I can't fully explain it.
        
        base.camera.lookAt(self.target.getX(),self.target.getY(),self.target.getZ() )
        # Points the camera at the target location.
        
    def clamp(self, val, minVal, maxVal):
        # This function constrains a value such that it is always within or equal to the minimum and maximum bounds.
        
        val = min( max(val, minVal), maxVal)
        # This line first finds the larger of the val or the minVal, and then compares that to the maxVal, taking the smaller. This ensures
        # that the result you get will be the maxVal if val is higher than it, the minVal if val is lower than it, or the val itself if it's
        # between the two.
        
        return val
        # returns the clamped value
    
    def setTarget(self):
        '''Sets target'''
        target = picker.getCenterCoords()
        if target:
            x, y, z = target
            #This function is used to give the camera a new target position.
            x = self.clamp(x, self.panLimitsX.getX(), self.panLimitsX.getY())
            self.target.setX(x)
            y = self.clamp(y, self.panLimitsY.getX(), self.panLimitsY.getY())
            self.target.setY(y)
            self.target.setZ(z)
            # Stores the new target position values in the target variable. The x and y values are clamped to the pan limits.
            self.setDist()
    
    def setDist(self):
        '''Sets the camDist variable'''
        diff = base.camera.getPos() - self.target
        self.camDist = math.sqrt(diff.getX()**2 + diff.getY()**2 + diff.getZ()**2)
    
    def enterCity(self, ident, city, position, tiles):
        '''Adjust camera parameters to city view.'''
        # Quick calculation for min and max values
        minX = 0
        minY = 0
        maxX = 0
        maxY = 0
        minX, minY = tiles[0].coords
        for tile in tiles:
            if tile.coords[0] < minX:
                minX = tile.coords[0]
            if tile.coords[1] < minY:
                minY = tile.coords[1]
            if tile.coords[0] > maxX:
                maxX = tile.coords[0]
            if tile.coords[1] > maxY:
                maxY = tile.coords[1]
        self.panLimitsX = Vec2(minX, maxX)
        self.panLimitsY = Vec2(minY, maxY)
        base.camera.setPos((minX+maxX)/2-10, (minY+maxY)/2-10, 200)
        base.camera.setHpr(30,-45,0)
        self.setTarget()
