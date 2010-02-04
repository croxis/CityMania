# -*- coding: utf-8 -*-
'''
Classes and functions for the user interface
'''
from pandac.PandaModules import CollisionTraverser,CollisionHandlerQueue,CollisionNode,CollisionRay,GeomNode, Texture, PNMImage, StringStream
from direct.showbase import DirectObject
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *

import sys
import yaml
import glob
import random

from pandac.PandaModules import Vec2,Vec3,Vec3D,VBase4
from pandac.PandaModules import Spotlight,PerspectiveLens,Fog,OrthographicLens
from pandac.PandaModules import PointLight, AmbientLight, DirectionalLight
#from pandac.PandaModules import TextNode, LineSegs, NodePath
from pandac.PandaModules import LineSegs, NodePath
from pandac.PandaModules import WindowProperties
from pandac.PandaModules import VBase3, GeomVertexReader

#from direct.fsm import FSM
from direct.task import Task
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode

import pixelwindow as pw
sys.path.append("../..")
import CityMania.common.protocol_pb2 as proto

class Picker(DirectObject.DirectObject):
    '''
    Mouse controller. 
    '''
    def __init__(self,ancestor=None):
        self.accept('makePickable', self.makePickable)
        self.ancestor=ancestor
        #create traverser
        base.cTrav = CollisionTraverser()
        #create collision ray
        self.createRay(self,base.camera,name="mouseRay",show=True)
        #initialize mousePick
        #self.accept('mouse1-up', self.mousePick, [1,self.queue])
        self.accept('mouse1', self.mousePick, [1,self.queue])
        #initialize mouseRightPick
        #self.accept('mouse3', self.mousePick, [3,self.queue])

    def mouseRight(self,pickedObj,pickedPoint):
        contextDict = {}
        if pickedObj==None: 
            pass
        else:
            #get cell from pickedpoint
            cell=(int(math.floor(pickedPoint[0])),int(math.floor(pickedPoint[1])), self.ancestor.level)
            contextDict['cell'] = cell
        messenger.send('buildContextMenu', [contextDict])

    def mouseLeft(self,pickedObj,pickedPoint):
        if pickedObj==None:  return
        #print "mouseLeft", pickedObj, pickedPoint
        cell=(int(math.floor(pickedPoint[0])),int(math.floor(pickedPoint[1])), self.ancestor.level)
        #messenger.send('cellCoords', [cell,])
        print cell  
        if self.ancestor.terrainManager.terrains[cell[2]][0].data[cell[0]][cell[1]]['structure']:
            messenger.send('structureClick', [cell,])

    def mousePick(self, but, queue):
        """mouse pick""" 
        #print "Mousepick"
        #get mouse coords
        if base.mouseWatcherNode.hasMouse()==False: return
        mpos=base.mouseWatcherNode.getMouse()
        #locate ray from camera lens to mouse coords
        self.ray.setFromLens(base.camNode, mpos.getX(),mpos.getY())
        #get collision: picked obj and point
        pickedObj,pickedPoint=self.getCollision(queue)
        #call appropiate mouse function (left or right)
        if but==1:self.mouseLeft(pickedObj,pickedPoint)
        if but==3:self.mouseRight(pickedObj,pickedPoint)

    """Returns the picked nodepath and the picked 3d point"""
    def getCollision(self, queue):
        #do the traverse
        base.cTrav.traverse(render)
        #process collision entries in queue
        if queue.getNumEntries() > 0:
            queue.sortEntries()
            for i in range(queue.getNumEntries()):
                collisionEntry=queue.getEntry(i)
                pickedObj=collisionEntry.getIntoNodePath()
                #iterate up in model hierarchy to found a pickable tag
                parent=pickedObj.getParent()
                for n in range(1):
                    if parent.getTag('pickable')!="" or parent==render: break
                    parent=parent.getParent()
                #return appropiate picked object
                if parent.getTag('pickable')!="":
                    pickedObj=parent
                    pickedPoint = collisionEntry.getSurfacePoint(pickedObj)
                    #pickedNormal = collisionEntry.getSurfaceNormal(self.ancestor.worldNode)
                    #pickedDistance=pickedPoint.lengthSquared()#distance between your object and the collision
                    return pickedObj,pickedPoint         
        return None,None

    def makePickable(self,newObj,tag='true'):
        """sets nodepath pickable state"""
        newObj.setTag('pickable',tag)
        #print "Pickable: ",newObj,"as",tag
    
    """creates a ray for detecting collisions"""
    def createRay(self,obj,ent,name,show=False,x=0,y=0,z=0,dx=0,dy=0,dz=-1):
        #create queue
        obj.queue=CollisionHandlerQueue()
        #create ray  
        obj.rayNP=ent.attachNewNode(CollisionNode(name))
        obj.ray=CollisionRay(x,y,z,dx,dy,dz)
        obj.rayNP.node().addSolid(obj.ray)
        obj.rayNP.node().setFromCollideMask(GeomNode.getDefaultCollideMask())
        base.cTrav.addCollider(obj.rayNP, obj.queue) 
        if show: obj.rayNP.show()


class Script(object):
    '''
    Imports external language yaml docs into internal dict
    '''
    def __init__(self):
        self.database = {}
        #self.database = {'TXT_UI_ONLINE': {'english': 'Online'}, 'TXT_UI_QUIT': {'english': 'Quit'}, 'TXT_UI_LOGINMP': {'english': 'Multiplayer'}, 'TXT_UI_LOGINTITLE': {'english': 'Multiplayer'}, 'TXT_UI_NEWGAME': {'english': 'New Game'}, 'TXT_UI_OFFLINE': {'english': 'Offline'}, 'TXT_UI_OK': {'english': 'Ok'}, 'TXT_UI_MAINMENUTITLE': {'english': 'City Mania'}}
        
        self.loadText()
    
    def loadText(self):
        # Load database
        pathList = glob.glob('TXT_*.yaml')
        for path in pathList:
            path = path.replace('\\','/')
            configFile = open(path, 'r')
            stream = configFile.read()
            configFile.close()
            textDictionary = yaml.load(stream)
            for key in textDictionary:
                self.database[key] = textDictionary[key]
    
    def getText(self, key, language="english"):
        # If the entry doesn't exist then the key name is returned as the text.
        if key not in self.database: return key
        # If the language key does not exist, the english version will be returned
        if language not in self.database[key]: language = 'english'
        return self.database[key][language]


class GUIController(DirectObject.DirectObject):
    '''
    Manages subwindows. Use this to make common windows to prevent import hell
    '''
    def __init__(self, script, language = "english"):
        """
        Script be the language database
        """
        self.script = script
        #messenger.send('makePickable', [base.a2dBottomLeft])
        
        self.language = language
        self.accept("onGetMaps", self.mapSelection)
        self.accept("finishedTerrainGen", self.regionGUI)
        self.accept("found_city_name", self.foundCityName)
        self.accept("newCityResponse", self.newCityResponse)
        self.accept("updateCityLabels", self.cityLabels)
        self.cityLabels = []
        
    def mainMenu(self):
        """
        Creates main menu
        """
        self.mainMenu = pw.StandardWindow(title = self.script.getText("TXT_UI_MAINMENUTITLE"), center = True)
        login = DirectButton(text= self.script.getText('TXT_UI_LOGINMP', self.language), command=self.loginMP)
        closeButton = DirectButton( text='Quit',  command=self.quit)
        self.mainMenu.addVertical([login, closeButton])

    def newGame(self):
        self.mainMenu.destroy()
        messenger.send('newSPGame')
    
    def loginMP(self):
        self.mainMenu.destroy()
        self.loginDialog = pw.StandardWindow(title = self.script.getText("TXT_UI_LOGINTITLE"), center = True)
        hostEntry = DirectEntry(initialText="croxis.dyndns.org")
        userNameEntry = DirectEntry(initialText = "Name")
        userPasswordEntry = DirectEntry(initialText="Password", obscured=True)
        okButton = DirectButton(text = self.script.getText('TXT_UI_OK', self.language), command = self.login)
        closeButton = DirectButton(text='Back', command=self.loginDialog.destroy)
        self.loginDialog.addVertical([hostEntry,userNameEntry,userPasswordEntry])
        self.loginDialog.addHorizontal([okButton, closeButton])
        
    def quit(self):
        self.mainMenu.destroy()
        messenger.send('exit')
    
    def login(self):
        """
        Collects login information from gui and fires message to login
        """
        info = self.loginDialog.getEntries()
        self.loginDialog.destroy()
        # Password will never make it out of here unscrambled!
        import hashlib
        password = info.pop(-1)
        cypher = hashlib.md5(password).hexdigest()
        info.append(cypher)
        messenger.send("connect", info)
    
    def mapSelection(self, maps):
        """
        Generate a window with list and thumbnails of region maps availiable.
        Provide two options, load map or, if there is no local version, save local version
        """
        self.mapDialog = pw.StandardWindow(title = "Select Map", center = True)
        mapList = []
        m = [""]
        import base64
        for mapName in maps:
            heightmap = maps[mapName]
            image = PNMImage()
            image.read(StringStream(heightmap))      
            thumbnail = PNMImage(64, 64)
            thumbnail.gaussianFilterFrom(1, image)
            heightTexture = Texture()
            heightTexture.load(image)
            label = DirectRadioButton(text=mapName, image=heightTexture, variable=m, value=[mapName])
            mapList.append(label)
        print "Label", mapList
        for button in mapList:
            button.setOthers(mapList)
        self.mapDialog.addScrolledList(mapList)
        okButton = DirectButton(text = self.script.getText('TXT_UI_OK', self.language), command = self.selectMap, extraArgs=m)
        self.mapDialog.addVertical([okButton])
    
    def selectMap(self, map_name):
        '''Sends selected map to server for loading'''
        self.mapDialog.destroy()
        container = proto.Container()
        container.mapRequest = map_name
        messenger.send("sendData", [container])
        
    def regionGUI(self):
        '''Generates GUI for region view interface'''
        #self.loginDialog = pw.StandardWindow(title = self.script.getText("TXT_UI_REGIONTITLE"), center = True)
        self.regionWindow = pw.StandardWindow(title = "Region_Name", center = True)
        self.v = [0]
        #buttons = [
        #    DirectRadioButton(text = "Normal View", variable=self.v, value=[0], command=self.sendRegionMessage),
        #    DirectRadioButton(text = "Ownership View", variable=self.v, value=[1], command=self.sendRegionMessage)]
        buttons = [DirectButton(text = "Normal View", command=self.n),
            DirectButton(text = "Ownership View", command=self.o)]
        #for button in buttons:
        #    button.setOthers(buttons)
        newCityButton = closeButton = DirectButton(text='Incorperate New City', command=self.sendRegionMessage, extraArgs=[True])
        self.regionWindow.addVertical(buttons + [newCityButton])
    
    def n(self):
        messenger.send("regionView_normal")
    def o(self):
        messenger.send("regionView_owners")

    def sendRegionMessage(self, status=None):
        '''Send messages for region view'''
        print "Status", status
        if self.v == [0]:
            messenger.send("regionView_normal")
        elif self.v == [1]:
            messenger.send("regionView_owners")
        if status:
            self.text = OnscreenText(text = "Left click to found city.", pos=(0, 0.75), scale=0.07)
            self.regionWindow.destroy()
            messenger.send("regionView_owners")
            messenger.send("regionView_foundNew")
    
    def foundCityName(self, position):
        self.name_city_window = pw.StandardWindow(title = "name_city", center = True)
        cityNameEntry = DirectEntry(initialText = "city_name")
        okButton = DirectButton(text = self.script.getText('TXT_UI_OK', self.language), command = self.foundCity, extraArgs=[position])
        self.name_city_window.addVertical([cityNameEntry, okButton])
    
    def foundCity(self, position):
        '''Sends message to server that we want to found a new city at this location'''
        container = proto.Container()
        info = self.name_city_window.getEntries()
        self.name_city_window.destroy()
        container.newCityRequest.name = info[0]
        container.newCityRequest.positionx = position[0]
        container.newCityRequest.positiony = position[1]
        messenger.send("sendData", [container])
    
    def newCityResponse(self, info):
        if not info.type:
            message = pw.MessageWindow(text="City can not be founded. "+ info.message, title="Oh noes!")
            messenger.send("regionView_foundNew")
        else:
            message = pw.MessageWindow(text="Your city has been founded! Awesome!")
            messenger.send("regionView_normal")
            self.regionGUI()
    
    def makeChatWindow(self):
        pass
    
    def cityLabels(self, citylabels, terrain):
        #for item in self.cityLabels:
        #    item.destroy()
        for ident, city in citylabels.items():
            
            text = city['name'] + "\n" + city["mayor"] + "\n" + "Population: " + str(city['population'])
            label = TextNode(str(ident) + " label")
            label.setText(text)
            label.setTextColor(1, 1, 0.75, 1)
            label.setCardColor(0.5,1,1,1)
            label.setCardDecal(True)
            textNodePath = render.attachNewNode(label)
            textNodePath.setPos(city['position'][1], city["position"][0], 70)
            #textNodePath.setLightOff()
            textNodePath.setBillboardPointEye()
            self.cityLabels.append(label)
            

class Lights:
    def __init__(self,ancestor,lightsOn=True,showLights=False):
        self.ancestor=ancestor
        
        #Initialize bg colour
        colour = (0,0,0)
        base.setBackgroundColor(*colour)
        
        if lightsOn==False: return
        
        # Initialise lighting
        self.alight = AmbientLight('alight')
        self.alight.setColor(VBase4(0.25, 0.25, 0.25, 1))
        self.alnp = render.attachNewNode(self.alight)
        render.setLight(self.alnp)
        
        self.dlight = DirectionalLight('dlight')
        self.dlight.setColor(VBase4(1.0, 1.0, 1.0, 1))
        self.dlnp = render.attachNewNode(self.dlight)
        self.dlnp.setHpr(45, -45, 32)
        render.setLight(self.dlnp)

from pandac.PandaModules import Vec3,Vec2
import math    
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
    def __init__(self, isometric = False):
        '''
        '''
        self.dz=.5
        #center=(len(self.ancestor.terrain.data)/2,len(self.ancestor.terrain.data[0])/2,self.dz)
        base.disableMouse()
        #base.camLens.setFov(50)
        #base.camera.setPos(-center[0]*2,-center[1]*2,5)
        base.camera.setPos(200, 0, 100)
        base.camera.setHpr(30,-45,0)
        self.isometric = isometric
        
        if isometric:
            lens = OrthographicLens()
            lens.setFilmSize(6)
            base.cam.node().setLens(lens)
            
        self.camDist = 40
        # A variable that will determine how far the camera is from it's target focus
        # TODO: Panlimit based on map size
        self.panLimitsX = Vec2(-20, 520)
        self.panLimitsY = Vec2(-20, 520)
        # These two vairables will serve as limits for how far the camera can pan, so you don't scroll away from the map.
        
        self.target=Vec3()
        
        self.isPanning = False
        self.isOrbiting = False
        self.accept('mouse2', self.middleMouseDown, [])
        self.accept('mouse2-up', self.middleMouseUp, [])
        self.accept('mouse3', self.rightMouseDown, [])
        self.accept('mouse3-up', self.rightMouseUp, [])
        
        self.createRay(self,base.camera,name="mouseRay",show=True)
        
        taskMgr.add(self.update,"updateCameraTask")
    
    def middleMouseDown(self):
        # This function puts the camera into orbiting mode.
        # test
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
        self.isPanning = False
    
    def update(self, task):
        #print "Old Camera:", base.win.getPointer(0).getX(), base.win.getPointer(0).getY()
        #print "New camera:", base.mouseWatcherNode.getMouse()
        if self.isOrbiting:
            # Checks to see if the camera is in orbiting mode. Orbiting mode overrides panning, because it would be problematic if, while
            # orbiting the camera the mouse came close to the screen edge and started panning the camera at the same time.
            #mpos = base.mouseWatcherNode.getMouse()
            #self.turnCameraAroundPoint((self.mx-mpos.getX())*100,(self.my-mpos.getY())*100)  
            mousePosition1=[base.win.getPointer(0).getX(),base.win.getPointer(0).getY()]
            delta = [(mousePosition1[0]- self.mousePosition0[0])*0.005, (mousePosition1[1] - self.mousePosition0[1]) * 0.005]
            self.turnCameraAroundPoint(delta[0], delta[1])
        elif self.isPanning:
            mousePosition1 = [base.win.getPointer(0).getX(),base.win.getPointer(0).getY()]
            delta = [(mousePosition1[0]- self.mousePosition0[0])*0.005, (mousePosition1[1] - self.mousePosition0[1]) * 0.005]
            #print delta
            base.camera.setPos(base.camera.getPos()[0] + delta[0], base.camera.getPos()[1] - delta[1], base.camera.getPos()[2])
        return Task.cont
    
    def turnCameraAroundPoint(self,deltaX,deltaY):
        # This function performs two important tasks. First, it is used for the camera orbital movement that occurs when the
        # right mouse button is held down. It is also called with 0s for the rotation inputs to reposition the camera during the
        # panning and zooming movements.
        # The delta inputs represent the change in rotation of the camera, which is also used to determine how far the camera
        # actually moves along the orbit.
        newCamHpr = Vec3()
        newCamPos = Vec3()
        # Creates temporary containers for the new rotation and position values of the camera.
        
        camHpr=base.camera.getHpr()
        # Creates a container for the current HPR of the camera and stores those values.
        
        newCamHpr.setX(camHpr.getX()+deltaX)
        newCamHpr.setY(self.clamp(camHpr.getY()-deltaY, -85, -10))
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
        target = self.centerPick(self.queue)
        if target:
            x, y, z = target
            #This function is used to give the camera a new target position.
            x = self.clamp(x, self.panLimitsX.getX(), self.panLimitsX.getY())
            self.target.setX(x)
            y = self.clamp(y, self.panLimitsY.getX(), self.panLimitsY.getY())
            self.target.setY(y)
            self.target.setZ(z*100)
            # Stores the new target position values in the target variable. The x and y values are clamped to the pan limits.
    
    def createRay(self,obj,ent,name,show=False,x=0,y=0,z=0,dx=0,dy=0,dz=-1):
        #create queue
        obj.queue=CollisionHandlerQueue()
        #create ray  
        obj.rayNP=ent.attachNewNode(CollisionNode(name))
        obj.ray=CollisionRay(x,y,z,dx,dy,dz)
        obj.rayNP.node().addSolid(obj.ray)
        obj.rayNP.node().setFromCollideMask(GeomNode.getDefaultCollideMask())
        base.cTrav.addCollider(obj.rayNP, obj.queue) 
        if show: obj.rayNP.show()
    
    def centerPick(self, queue):
        #print "Mousepick"
        #get mouse coords
        if base.mouseWatcherNode.hasMouse()==False: return
        #mpos=base.mouseWatcherNode.getMouse()
        #locate ray from camera lens to mouse coords
        self.ray.setFromLens(base.camNode, 0, 0)
        #get collision: picked obj and point
        pickedObj,pickedPoint=self.getCollision(queue)
        return pickedPoint
    
    def getCollision(self, queue):
        #do the traverse
        base.cTrav.traverse(render)
        #process collision entries in queue
        if queue.getNumEntries() > 0:
            queue.sortEntries()
            for i in range(queue.getNumEntries()):
                collisionEntry=queue.getEntry(i)
                pickedObj=collisionEntry.getIntoNodePath()
                #iterate up in model hierarchy to found a pickable tag
                parent=pickedObj.getParent()
                for n in range(1):
                    if parent.getTag('pickable')!="" or parent==render: break
                    parent=parent.getParent()
                #return appropiate picked object
                if parent.getTag('pickable')!="":
                    pickedObj=parent
                    pickedPoint = collisionEntry.getSurfacePoint(pickedObj)
                    #pickedNormal = collisionEntry.getSurfaceNormal(self.ancestor.worldNode)
                    #pickedDistance=pickedPoint.lengthSquared()#distance between your object and the collision
                    return pickedObj,pickedPoint         
        return None,None


# Last modified: 10/2/2009
# This class takes over control of the camera and sets up a Real Time Strategy game type camera control system. The user can move the camera three
# ways. If the mouse cursor is moved to the edge of the screen, the camera will pan in that direction. If the right mouse button is held down, the
# camera will orbit around it's target point in accordance with the mouse movement, maintaining a fixed distance. The mouse wheel will move the
# camera closer to or further from it's target point.

# This code was originally developed by Ninth from the Panda3D forums, and has been modified by piratePanda to achieve a few effects.
   # First mod: Comments. I've gone through the code and added comments to explain what is doing what, and the reason for each line of code.
   # Second mod: Name changes. I changed some names of variables and functions to make the code a bit more readable (in my opinion).
   # Third mod: Variable pan rate. I have changed the camera panning when the mouse is moved to the edge of the screen so that the panning
      # rate is dependant on the distance the camera has been zoomed out. This prevents the panning from appearing faster when
      # zoomed in than when zoomed out. I have also added a pan rate variable, which could be modified by an options menu, so it is
      # easier to give the player control over how fast the camera pans.
   # Fourth mod: Variable pan zones. I added a variable to control the size of the zones at the edge of the screen where the camera starts
      # panning.
   # Fifth mod: Orbit limits: I put in a system to limit how far the camera can move along it's Y orbit to prevent it from moving below the ground
      # plane or so high that you get a fast rotation glitch.
   # Sixth mod: Pan limits: I put in variables to use for limiting how far the camera can pan, so the camera can't pan away from the map. These
      # values will need to be customized to the map, so I added a function for setting them.
   

class CameraHandler(DirectObject.DirectObject):
    def __init__(self):
    
    
        base.disableMouse()
        # This disables the default mouse based camera control used by panda. This default control is awkward, and won't be used.
        
        #base.camera.setPos(0,20,20)
        base.camera.setPos(200, 100, 100)
        base.camera.lookAt(100,100,45)
        # Gives the camera an initial position and rotation.
        
        self.mx,self.my=0,0
        # Sets up variables for storing the mouse coordinates
        
        self.orbiting=False
        # A boolean variable for specifying whether the camera is in orbiting mode. Orbiting mode refers to when the camera is being moved
        # because the user is holding down the right mouse button.
        
        self.target=Vec3()
        # sets up a vector variable for the camera's target. The target will be the coordinates that the camera is currently focusing on.
        
        self.camDist = 40
        # A variable that will determine how far the camera is from it's target focus
        
        self.panRateDivisor = 20
        # This variable is used as a divisor when calculating how far to move the camera when panning. Higher numbers will yield slower panning
        # and lower numbers will yield faster panning. This must not be set to 0.
        
        self.panZoneSize = .15
        # This variable controls how close the mouse cursor needs to be to the edge of the screen to start panning the camera. It must be less than 1,
        # and I recommend keeping it less than .2
        
        self.panLimitsX = Vec2(-20, 20)
        self.panLimitsY = Vec2(-20, 20)
        # These two vairables will serve as limits for how far the camera can pan, so you don't scroll away from the map.

        self.setTarget(100,100,0)
        # calls the setTarget function to set the current target position to the origin.
        
        self.turnCameraAroundPoint(0,0)
        # calls the turnCameraAroundPoint function with a turn amount of 0 to set the camera position based on the target and camera distance
        
        self.accept("mouse3",self.startOrbit)
        # sets up the camrea handler to accept a right mouse click and start the "drag" mode.
        
        self.accept("mouse3-up",self.stopOrbit)
        # sets up the camrea handler to understand when the right mouse button has been released, and ends the "drag" mode when
        # the release is detected.
        
        # The next pair of lines use lambda, which creates an on-the-spot one-shot function.
        
        self.accept("wheel_up",lambda : self.adjustCamDist(0.9))
        # sets up the camera handler to detet when the mouse wheel is rolled upwards and uses a lambda function to call the
        # adjustCamDist function  with the argument 0.9
        
        self.accept("wheel_down",lambda : self.adjustCamDist(1.1))
        # sets up the camera handler to detet when the mouse wheel is rolled upwards and uses a lambda function to call the
        # adjustCamDist function  with the argument 1.1
        
        self.createRay(self,base.camera,name="mouseRay",show=True)
        self.accept('mouse1', self.mouse_pick, [self.queue])
        self.accept('makePickable', self.makePickable)
        
        taskMgr.add(self.camMoveTask,'camMoveTask')
        # sets the camMoveTask to be run every frame
        
    def setPanLimits(self,xMin, xMax, yMin, yMax):
        # This function is used to set the limitations of the panning movement.
        
        self.panLimitsX = Vec2(xMin, xMax)
        self.panLimitsY = Vec2(yMin, yMax)
        # Sets the inputs into the limit variables.
        
    def adjustCamDist(self,distFactor):
        # This function increases or decreases the distance between the camera and the target position to simulate zooming in and out.
        # The distFactor input controls the amount of camera movement.
        # For example, inputing 0.9 will set the camera to 90% of it's previous distance.
        coords = self.getCoords()
        
        self.camDist=self.camDist*distFactor
        # Sets the new distance into self.camDist.
        
        self.turnCameraAroundPoint(0,0)
        #self.turnCameraAroundPoint(coords.getX(),coords.getY())
        # Calls turnCameraAroundPoint with 0s for the rotation to reset the camera to the new position.
        
    def camMoveTask(self,task):
        # This task is the camera handler's work house. It's set to be called every frame and will control both orbiting and panning the camera.
        print base.camera.getPos()
        if base.mouseWatcherNode.hasMouse():
            # We're going to use the mouse, so we have to make sure it's in the game window. If it's not and we try to use it, we'll get
            # a crash error.
            
            mpos = base.mouseWatcherNode.getMouse()
            # Gets the mouse position
            
            if self.orbiting:
            # Checks to see if the camera is in orbiting mode. Orbiting mode overrides panning, because it would be problematic if, while
            # orbiting the camera the mouse came close to the screen edge and started panning the camera at the same time.
            
                self.turnCameraAroundPoint((self.mx-mpos.getX())*100,(self.my-mpos.getY())*100)       
                # calculates new values for camera rotation based on the change in mouse position. mx and my are used here as the old
                # mouse position.
                
            else:
            # If the camera isn't in orbiting mode, we check to see if the mouse is close enough to the edge of the screen to start panning
            
                moveY=False
                moveX=False
                # these two booleans are used to denote if the camera needs to pan. X and Y refer to the mouse position that causes the
                # panning. X is the left or right edge of the screen, Y is the top or bottom.
                
                if self.my > (1 - self.panZoneSize):
                    angleradiansX1 = base.camera.getH() * (math.pi / 180.0)
                    panRate1 = (1 - self.my - self.panZoneSize) * (self.camDist / self.panRateDivisor)
                    moveY = True
                if self.my < (-1 + self.panZoneSize):
                    angleradiansX1 = base.camera.getH() * (math.pi / 180.0)+math.pi
                    panRate1 = (1 + self.my - self.panZoneSize)*(self.camDist / self.panRateDivisor)
                    moveY = True
                if self.mx > (1 - self.panZoneSize):
                    angleradiansX2 = base.camera.getH() * (math.pi / 180.0)+math.pi*0.5
                    panRate2 = (1 - self.mx - self.panZoneSize) * (self.camDist / self.panRateDivisor)
                    moveX = True
                if self.mx < (-1 + self.panZoneSize):
                    angleradiansX2 = base.camera.getH() * (math.pi / 180.0)-math.pi*0.5
                    panRate2 = (1 + self.mx - self.panZoneSize) * (self.camDist / self.panRateDivisor)
                    moveX = True
                # These four blocks check to see if the mouse cursor is close enough to the edge of the screen to start panning and then
                # perform part of the math necessary to find the new camera position. Once again, the math is a bit above my head, so
                # I can't properly explain it. These blocks also set the move booleans to true so that the next lines will move the camera.
                
                if moveY:
                    tempX = self.target.getX()+math.sin(angleradiansX1)*panRate1
                    tempX = self.clamp(tempX, self.panLimitsX.getX(), self.panLimitsX.getY())
                    self.target.setX(tempX)
                    tempY = self.target.getY()-math.cos(angleradiansX1)*panRate1
                    tempY = self.clamp(tempY, self.panLimitsY.getX(), self.panLimitsY.getY())
                    self.target.setY(tempY)
                    self.turnCameraAroundPoint(0,0)
                if moveX:
                    tempX = self.target.getX()-math.sin(angleradiansX2)*panRate2
                    tempX = self.clamp(tempX, self.panLimitsX.getX(), self.panLimitsX.getY())
                    self.target.setX(tempX)
                    tempY = self.target.getY()+math.cos(angleradiansX2)*panRate2
                    tempY = self.clamp(tempY, self.panLimitsY.getX(), self.panLimitsY.getY())
                    self.target.setY(tempY)
                    self.turnCameraAroundPoint(0,0)
                # These two blocks finalize the math necessary to find the new camera position and apply the transformation to the
                # camera's TARGET. Then turnCameraAroundPoint is called with 0s for rotation, and it resets the camera position based
                # on the position of the target. The x and y values are clamped to the pan limits before they are applied.
            #print(self.target)
            self.mx=mpos.getX()
            self.my=mpos.getY()
            # The old mouse positions are updated to the current mouse position as the final step.
            
        return task.cont 