# -*- coding: utf-8 -*-
'''
Classes and functions for the user interface
'''
#from pandac.PandaModules import *
from panda3d.core import CollisionTraverser, CollisionHandlerQueue, CollisionNode, CollisionRay, GeomNode
from panda3d.core import NodePath, TextNode, PNMImage, StringStream, Texture
from direct.gui.OnscreenText import OnscreenText
from direct.showbase import DirectObject
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from direct.stdpy.file import *

from panda3d.core import VirtualFileSystem

import sys
#import yaml
import glob
import random
import math

#from direct.fsm import FSM
#from panda3d.core import TextNode

from directWindow import DirectWindow, MessageWindow
sys.path.append("../..")
import CityMania.common.protocol_pb2 as proto
import CityMania.common.yaml as yaml
import access

class Picker(DirectObject.DirectObject):
    '''
    Mouse controller. 
    '''
    def __init__(self, show=False):
        self.accept('makePickable', self.makePickable)
        #create traverser
        #base.cTrav = CollisionTraverser()
        self.cTrav = CollisionTraverser()
        #create collision ray
        self.createRay(self,base.camera,name="mouseRay",show=show)

    def getMouseCell(self):
        """Returns terrain cell coordinates (x,y) at mouse pointer""" 
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
    
    def getCenterCoords(self, nodePath = render):
        '''Returns terrain cell coordinates (x,y) that is at center of camera'''
        self.ray.setFromLens(base.camNode, 0, 0)
        #get collision: picked obj and point
        pickedObj,pickedPoint=self.getCollision(self.queue, nodePath)
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
    
    def getCollision(self, queue, nodePath = render):
        """Returns the picked nodepath and the picked 3d point.
        This function not inteded to be called directly, use a get*() function instead.
        """
        #do the traverse
        #base.cTrav.traverse(render)
        self.cTrav.traverse(nodePath)
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
        self.database = {}
        self.loadText()
    
    def loadText(self):
        # Load database
        vfs = VirtualFileSystem.getGlobalPtr()
        #print "Virtual fs" ,vfs.lsAll('/mf')
        path = vfs.findFile('TXT_UI_Common.yaml', '.')
        if not path:
            path = vfs.findFile('TXT_UI_Common.yaml', '/mf')
        stream = vfs.readFile(path.getFilename(), True)
        textDictionary = yaml.load(stream)
        for key in textDictionary:
            self.database[key] = textDictionary[key]
        #a = vfs.lsAll('.')
        #print a
        #print type(a)
        #print vfs.findAllFiles('.','TXT_*.yaml', results)
        #print results
#        pathList = glob.glob('TXT_*.yaml')
#        for path in pathList:
#            path = path.replace('\\','/')
#            configFile = open(path, 'r')
#            stream = configFile.read()
#            configFile.close()
#            textDictionary = yaml.load(stream)
#            for key in textDictionary:
#                self.database[key] = textDictionary[key]
    
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
        self.window = None
        self.language = language
        self.accept("onGetMaps", self.mapSelection)
        self.accept("finishedTerrainGen", self.regionGUI)
        self.accept("found_city_name", self.foundCityName)
        self.accept("newCityResponse", self.newCityResponse)
        self.accept("updateCityLabels", self.cityLabels)
        self.accept("showRegionCityWindow", self.regionCityWindow)
        self.accept("showRegionGUI", self.regionGUI)
        self.accept("disconnected", self.disconnected)
        self.accept("enterCityView", self.cityGUI)
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
        if self.window:
            self.window.destroy()
            self.window = None
        self.mainMenu = DirectWindow(title = self.getText("TXT_UI_MAINMENUTITLE"))
        login = DirectButton(text= self.getText('TXT_UI_LOGINMP'), command=self.loginMP)
        closeButton = DirectButton( text='Quit',  command=lambda : messenger.send('exit'))
        self.mainMenu.addVertical([login, closeButton])
        self.mainMenu.reset()
        self.mainMenu.center()

    def newGame(self):
        self.mainMenu.destroy()
        messenger.send('newSPGame')
    
    def loginMP(self):
        self.mainMenu.destroy()
        self.window = DirectWindow(title = self.getText("TXT_UI_LOGINTITLE"))
        hostEntry = DirectEntry(initialText="croxis.dyndns.org", suppressKeys = True)
        userNameEntry = DirectEntry(initialText = self.getText('TXT_MAYOR_NAME'),suppressKeys = True)
        userPasswordEntry = DirectEntry(initialText="Password", obscured=True,suppressKeys = True)
        okButton = DirectButton(text = self.getText('TXT_UI_OK'), command = self.login)
        closeButton = DirectButton(text='Back', command=self.makeMainMenu)
        self.window.addVertical([hostEntry,userNameEntry,userPasswordEntry])
        self.window.addHorizontal([okButton, closeButton])
    
    def login(self):
        """
        Collects login information from gui and fires message to login
        """
        info = self.window.getEntries()
        self.window.destroy()
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
        self.mapDialog = DirectWindow(title = "Select Map")
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
        for button in mapList:
            button.setOthers(mapList)
        self.mapDialog.addScrolledList(mapList)
        okButton = DirectButton(text = self.getText('TXT_UI_OK'), command = self.selectMap, extraArgs=m)
        self.mapDialog.addVertical([okButton])
    
    def selectMap(self, map_name):
        '''Sends selected map to server for loading'''
        self.mapDialog.destroy()
        container = proto.Container()
        container.mapRequest = map_name
        messenger.send("sendData", [container])
    
    def cityGUI(self, ident, city, position, tiles):
        self.regionWindow.destroy()
        self.cityInfoWindow.destroy()
        children = self.cityLabels.getChildren()
        for child in children:
            child.removeNode()
        text = OnscreenText(text = "Welcome to " + city['name'], pos=(0, 0.75), scale=0.07)
        
    def regionGUI(self, size=[0,0]):
        '''Generates GUI for region view interface'''
        self.text.destroy()
        #self.loginDialog = pw.StandardWindow(title = self.script.getText("TXT_UI_REGIONTITLE"), center = True)
        self.regionWindow = DirectWindow(title = "Region_Name")
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
        self.name_city_window = DirectWindow(title = "name_city")
        cityNameEntry = DirectEntry(initialText = "city_name", suppressKeys = True)
        okButton = DirectButton(text = self.getText('TXT_UI_OK'), command = self.foundCity, extraArgs=[position])
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
            message = MessageWindow(text="City can not be founded. "+ info.message, title="Oh noes!")
            messenger.send("regionView_foundNew")
        else:
            message = MessageWindow(text="Your city has been founded! Awesome!")
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
            textNodePath.setPos(city['position'][0], city["position"][1], city['position'][2])
            textNodePath.setLightOff()
            textNodePath.setBillboardPointEye()
    
    def debug(self):
        '''Generates on screen text for debug functions.'''
        text = "f: toggles wireframe\nt: toggles texture\nh: switch water"
        OnscreenText(text = text, pos = (-1.0, 0.9), scale = 0.07)
    
    def regionCityWindow(self, ident, city):
        '''Generates window displaying city stats and options.'''
        #print "Access username and level", access.username, access.level
        #TODO: Once the city view is created we need to inform the client if they even have viewing rights
        self.cityInfoWindow = DirectWindow(title = city['name'])
        buttons =[]
        enterButton = DirectButton(text = self.script.getText('TXT_ENTER_CITY', self.language), command = self.enterCity, extraArgs=[ident])
        buttons.append(enterButton)
        if access.level is 4 or access.username == city['mayor']:
            unfoundButton = DirectButton(text = self.script.getText('TXT_UNFOUND_CITY', self.language), command = self.confirmUnfoundCity, extraArgs=[ident, self.cityInfoWindow])
            buttons.append(unfoundButton)
            #deleteButton = DirectButton(text = self.script.getText('TXT_DELETE_CITY', self.language), command = self.confirmDeleteCity, extraArgs=[ident])
            #buttons.append(deleteButton)
        self.cityInfoWindow.addHorizontal(buttons)
        closeButton = DirectButton(text = self.script.getText('TXT_BUTTON_CLOSE', self.language), command = self.closeWindow, extraArgs=[self.cityInfoWindow])
        self.cityInfoWindow.addVertical([closeButton])
    
    def enterCity(self, ident):
        container = proto.Container()
        container.requestEnterCity = ident
        messenger.send("sendData", [container])
        
    def confirmUnfoundCity(self, ident, cityWindow):
        window = DirectWindow(title = self.getText("TXT_TITLE_COFIRM_UNFOUND"))
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
        self.makeMainMenu()
        message = MessageWindow(title="You have been disconnected :(", text="Reason: %s" %reason)
        


picker = Picker()
def getPicker():
    return picker
