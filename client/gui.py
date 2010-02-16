# -*- coding: utf-8 -*-
'''
Classes and functions for the user interface
'''
from pandac.PandaModules import *
from direct.showbase import DirectObject
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *

import sys
#import yaml
import glob
import random

#from direct.fsm import FSM
from direct.task import Task
from direct.gui.OnscreenText import OnscreenText
#from panda3d.core import TextNode

import pixelwindow as pw
sys.path.append("../..")
import CityMania.common.protocol_pb2 as proto
import access

class Picker(DirectObject.DirectObject):
    '''
    Mouse controller. 
    '''
    def __init__(self, show=False):
        self.accept('makePickable', self.makePickable)
        #self.accept('mouse1', self.castRay)
        #create traverser
        #base.cTrav = CollisionTraverser()
        self.cTrav = CollisionTraverser()
        #create collision ray
        self.createRay(self,base.camera,name="mouseRay",show=show)
    
    def castRay(self):
        self.cTrav.traverse(render)

    def getMouseCell(self):
        """mouse pick""" 
        #get mouse coords
        if base.mouseWatcherNode.hasMouse()==False: return
        mpos=base.mouseWatcherNode.getMouse()
        #locate ray from camera lens to mouse coords
        self.ray.setFromLens(base.camNode, mpos.getX(),mpos.getY())
        #get collision: picked obj and point
        pickedObj,pickedPoint=self.getCollision(self.queue)
        #call appropiate mouse function (left or right)
        if pickedObj==None:  return
        cell=(int(math.floor(pickedPoint[0])),int(math.floor(pickedPoint[1])))
        return cell  
    
    def getCenterCoords(self):
        self.ray.setFromLens(base.camNode, 0, 0)
        #get collision: picked obj and point
        pickedObj,pickedPoint=self.getCollision(self.queue)
        return pickedPoint
    
    def getCoords(self):
        #get mouse coords
        if base.mouseWatcherNode.hasMouse()==False: return
        mpos=base.mouseWatcherNode.getMouse()
        #locate ray from camera lens to mouse coords
        self.ray.setFromLens(base.camNode, mpos.getX(),mpos.getY())
        #get collision: picked obj and point
        pickedObj,pickedPoint=self.getCollision(self.queue)
        return pickedPoint
    
    def getMiddle(self):
        '''Returns middle point between center of screen and mouse.
        Only used for strategic zooming
        '''
        if base.mouseWatcherNode.hasMouse()==False: return
        mpos=base.mouseWatcherNode.getMouse()
        self.ray.setFromLens(base.camNode, mpos.getX()/2,mpos.getY()/2)
        #get collision: picked obj and point
        pickedObj,pickedPoint=self.getCollision(self.queue)
        return pickedPoint       
    
    def getCollision(self, queue):
        """Returns the picked nodepath and the picked 3d point"""
        #do the traverse
        #base.cTrav.traverse(render)
        self.cTrav.traverse(render)
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
        #base.cTrav.addCollider(obj.rayNP, obj.queue)
        self.cTrav.addCollider(obj.rayNP, obj.queue) 
        if show: obj.rayNP.show()
        

class Script(object):
    '''
    Imports external language yaml docs into internal dict
    '''
    def __init__(self):
        #self.database = {}
        self.database = {'TXT_UI_ONLINE': {'english': 'Online'}, 'TXT_UI_QUIT': {'english': 'Quit'}, 'TXT_BUTTON_CLOSE': {'english': 'Close'}, 'TXT_UI_MAINMENUTITLE': {'english': 'City Mania'}, 'TXT_UI_LOGINMP': {'english': 'Multiplayer'}, 'TXT_TITLE_COFIRM_UNFOUND': {'english': 'Confirm City Unfounding'}, 'TXT_BUTTON_CONFIRM_UNFOUND': {'english': 'Confirm Unfounding'}, 'TXT_DELETE_CITY': {'english': 'Delete City'}, 'TXT_MAYOR_NAME': {'english': 'Mayor Name'}, 'TXT_UI_LOGINTITLE': {'english': 'Multiplayer'}, 'TXT_UI_NEWGAME': {'english': 'New Game'}, 'TXT_UI_OFFLINE': {'english': 'Offline'}, 'TXT_UI_OK': {'english': 'Ok'}, 'TXT_UNFOUND_CITY': {'english': 'Unfound City'}, 'TXT_ENTER_CITY': {'english': 'Enter City'}}
                
        #self.loadText()
    
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
        self.accept("showRegionCityWindow", self.regionCityWindow)
        self.accept("showRegionGUI", self.regionGUI)
        self.accept("disconnected", self.disconnected)
        self.cityLabels = NodePath("cityLabels")
        self.cityLabels.reparentTo(render)
        self.text = OnscreenText()
        self.debug()
    
    def getText(self, text):
        return self.script.getText(text, self.language)
        
    def makeMainMenu(self):
        """
        Creates main menu
        """
        print "Generating main menu"
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
        userNameEntry = DirectEntry(initialText = self.script.getText('TXT_MAYOR_NAME', self.language))
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
        
    def regionGUI(self, size=[0,0]):
        '''Generates GUI for region view interface'''
        self.text.destroy()
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
            self.text = OnscreenText(text = "Left click to found city.\nEsc to cancel", pos=(0, 0.75), scale=0.07)
            self.regionWindow.destroy()
            messenger.send("regionView_owners")
            messenger.send("regionView_foundNew")
    
    def foundCityName(self, position):
        self.text.destroy()
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
    
    def makeChatWindow(self):
        pass
    
    def cityLabels(self, citylabels, terrain):
        children = self.cityLabels.getChildren()
        for child in children:
            child.removeNode()
        for ident, city in citylabels.items():
            text = city['name'] + "\n" + city["mayor"] + "\n" + "Population: " + str(city['population'])
            label = TextNode(str(ident) + " label")
            label.setText(text)
            label.setTextColor(1, 1, 1, 1)
            label.setShadowColor(0, 0, 0, 1)
            label.setCardDecal(True)
            textNodePath = self.cityLabels.attachNewNode(label)
            textNodePath.setPos(city['position'][1], city["position"][0], city['position'][2])
            textNodePath.setLightOff()
            textNodePath.setBillboardPointEye()
    
    def debug(self):
        '''Generates on screen text for debug functions.'''
        text = "w: toggles wireframe\nt: toggles texture\ns: take snapshot\nh: switch water"
        OnscreenText(text = text, pos = (-1.0, 0.9), scale = 0.07)
    
    def regionCityWindow(self, ident, city):
        '''Generates window displaying city stats and options.'''
        #print "Access username and level", access.username, access.level
        #TODO: Once the city view is created we need to inform the client if they even have viewing rights
        cityInfoWindow = pw.StandardWindow(title = city['name'], center = True)
        buttons =[]
        enterButton = DirectButton(text = self.script.getText('TXT_ENTER_CITY', self.language), command = self.enterCity, extraArgs=[ident])
        buttons.append(enterButton)
        if access.level is 4 or access.username == city['mayor']:
            unfoundButton = DirectButton(text = self.script.getText('TXT_UNFOUND_CITY', self.language), command = self.confirmUnfoundCity, extraArgs=[ident, cityInfoWindow])
            buttons.append(unfoundButton)
            #deleteButton = DirectButton(text = self.script.getText('TXT_DELETE_CITY', self.language), command = self.confirmDeleteCity, extraArgs=[ident])
            #buttons.append(deleteButton)
        cityInfoWindow.addHorizontal(buttons)
        closeButton = DirectButton(text = self.script.getText('TXT_BUTTON_CLOSE', self.language), command = self.closeWindow, extraArgs=[cityInfoWindow])
        cityInfoWindow.addVertical([closeButton])
    
    def enterCity(self, ident):
        print "Request to enter city", ident
        
    def confirmUnfoundCity(self, ident, cityWindow):
        window = pw.StandardWindow(title = self.getText("TXT_TITLE_COFIRM_UNFOUND"), center=True)
        okButton = DirectButton(text = self.getText("TXT_BUTTON_CONFIRM_UNFOUND"), command = self.unfoundCity, extraArgs = [ident, window, cityWindow])
        closeButton = DirectButton(text = self.getText('TXT_BUTTON_CLOSE'), command = self.closeWindow, extraArgs=[window])
        window.addHorizontal([okButton, closeButton])
    
    def unfoundCity(self, ident, window, cityWindow):
        self.closeWindow(window)
        self.closeWindow(cityWindow)
        container = proto.Container()
        container.requestUnfoundCity = ident
        messenger.send("sendData", [container])
    
    def confirmDeleteCity(self, ident):
        print "Request to delete city", ident
    
    def closeWindow(self, window):
        window.destroy()
    
    def disconnected(self, reason):
        render.removeChildren()
        base.aspect2d.removeChildren()
        message = pw.MessageWindow(title="You have been disconnected :(", text="Reason: %s" %reason)
        self.makeMainMenu()
        

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
    def __init__(self, size, terrain, isometric = False):
        '''
        '''
        self.dz=.5
        #center=(len(self.ancestor.terrain.data)/2,len(self.ancestor.terrain.data[0])/2,self.dz)
        base.disableMouse()
        #base.camLens.setFov(50)
        #base.camera.setPos(-center[0]*2,-center[1]*2,5)
        base.camera.setPos(size[0]/2, size[1]/2, 100)
        base.camera.setHpr(30,-45,0)
        self.isometric = isometric
        self.terrain = terrain
        
        if isometric:
            lens = OrthographicLens()
            lens.setFilmSize(6)
            base.cam.node().setLens(lens)
            
        self.camDist = 40
        # A variable that will determine how far the camera is from it's target focus
        # TODO: Panlimit based on map size
        self.panLimitsX = Vec2(-20, size[0] + 20)
        self.panLimitsY = Vec2(-20, size[1] + 20)
        # These two variables will serve as limits for how far the camera can pan, so you don't scroll away from the map.
        
        self.target=Vec3()
        self.setTarget()
        self.isPanning = False
        self.isOrbiting = False
        self.accept('mouse2', self.middleMouseDown, [])
        self.accept('mouse2-up', self.middleMouseUp, [])
        self.accept('mouse3', self.rightMouseDown, [])
        self.accept('mouse3-up', self.rightMouseUp, [])
        self.accept("wheel_up",lambda : self.adjustCamDist(0.9))
        self.accept("wheel_down",lambda : self.adjustCamDist(1.1))
        
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
        self.camDist=self.camDist*distFactor
        point = picker.getMiddle()
        # In case we zoom out too far we prevent odd behavior 
        if point is None: return
        # Strategic zoom in for now
        if distFactor < 1:
            self.target.setX(point[0])
            self.target.setY(point[1])
        self.turnCameraAroundPoint(0,0)
        # Calls turnCameraAroundPoint with 0s for the rotation to reset the camera to the new position.
    
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
            # Old code
            #mousePosition1 = [base.win.getPointer(0).getX(),base.win.getPointer(0).getY()]
            #delta = [(mousePosition1[0]- self.mousePosition0[0])*0.005, (mousePosition1[1] - self.mousePosition0[1]) * 0.005]
            #base.camera.setPos(base.camera.getPos()[0] + delta[0], base.camera.getPos()[1] - delta[1], base.camera.getPos()[2])
            # New code
            mousePosition1 = [base.win.getPointer(0).getX(),base.win.getPointer(0).getY()]
            moveX = False
            moveY = False
            delta = [0,0]
            if mousePosition1[0] < self.mousePosition0[0]:
                #print "Left"
                angleradiansX2 = base.camera.getH() * (math.pi / 180.0)-math.pi*0.5
                delta[0] = (mousePosition1[0]- self.mousePosition0[0])*0.0005
                moveX = True
            if mousePosition1[0] > self.mousePosition0[0]:
                #print "Right"
                angleradiansX2 = base.camera.getH() * (math.pi / 180.0)+math.pi*0.5
                delta[0] = -(mousePosition1[0]- self.mousePosition0[0])*0.0005
                moveX = True
            if mousePosition1[1] > self.mousePosition0[1]:
                #print "Down"
                angleradiansX1 = base.camera.getH() * (math.pi / 180.0)-math.pi
                delta[1] = -(mousePosition1[1] - self.mousePosition0[1]) * 0.0005
                moveY = True
            if mousePosition1[1] < self.mousePosition0[1]:
                #print "Up"
                angleradiansX1 = base.camera.getH() * (math.pi / 180.0)+math.pi
                delta[1] = (mousePosition1[1] + self.mousePosition0[1]) * 0.0005
                moveY = True
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
        elevation = self.terrain.getElevation(pos[0], pos[1]) * root.getSz()
        # Factor is height we want above terrain
        factor = 1
        if elevation < 22 + factor:
            newCamPos.setZ(61 + factor)
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
        target = picker.getCenterCoords()
        if target:
            x, y, z = target
            #This function is used to give the camera a new target position.
            x = self.clamp(x, self.panLimitsX.getX(), self.panLimitsX.getY())
            self.target.setX(x)
            y = self.clamp(y, self.panLimitsY.getX(), self.panLimitsY.getY())
            self.target.setY(y)
            self.target.setZ(z*100)
            # Stores the new target position values in the target variable. The x and y values are clamped to the pan limits.


picker = Picker()
def getPicker():
    return picker
