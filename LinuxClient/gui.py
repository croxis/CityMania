# -*- coding: utf-8 -*-
'''
Classes and functions for the user interface
'''

from pandac.PandaModules import CollisionTraverser,CollisionHandlerQueue,CollisionNode,CollisionRay,GeomNode, Texture, PNMImage, StringStream
from direct.showbase import DirectObject
from direct.gui.DirectGui import *

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

from direct.task import Task

#import math
#import Meshes
#import Menu
import pixelwindow as pw
import protocol_pb2 as proto
#import layout
#import treegui
#from treegui.core import Gui
#import rtheme

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
        self.accept('mouse3', self.mousePick, [3,self.queue])

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
        #print cell  
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


class ContextMenu(DirectObject.DirectObject):
    def __init__(self, parent, structureDatabase, terrainManager, world):
        self.parent = parent
        self.accept('generateContextMenu', self.generateContextMenu)
        self.structures = structureDatabase
        self.terrainManager = terrainManager
        self.world = world
    
    def buildBuildableList(self, cell):
        '''
        Generates the list of buildabel buildings in the right click menu.
        Returns ()
        '''
        structureCache = []
        for structure in self.structures:
            if self.structures[structure]['build']:
                structureCache.append((self.structures[structure]['english']['name'], None, self.buildStructure, structure, cell))
        return tuple(structureCache)
    
    def buildLandersList(self, landers, cell):
        '''
        Generates the list of buildabel buildings in the right click menu.
        Returns ()
        '''
        landersCache = []
        #print landers
        for lander in landers:
            if landers[lander]:
                landersCache.append((lander, None, self.landLander, lander, cell))
        #print landersCache
        return tuple(landersCache)
    def buildLevelList(self):
        currentLevel = self.terrainManager.ancestor.level
        numLevels = len(self.terrainManager.terrains)
        levelsList = []
        for x in range(numLevels):
            name = ''
            if x == 0: name = 'Surface'
            else: name = 'SubLevel '+str(x)
            if x == currentLevel: levelsList.append((name,None,0))
            else: levelsList.append((name,None, self.switchLevelRequest, [x]))
        return tuple(levelsList)
    
    def switchLevelRequest(self, level):
        messenger.send('switchLevelRequest', level)
    
    def endTurnRequest(self):
        #print 'Requesting End of Turn'
        messenger.send("sendData", ['endTurnRequest'])
    def buildStructure(self, structureID, cell):
        messenger.send("sendData", ['buildRequest', [structureID, cell]])
    
    def exit(self):
        messenger.send('exit')
    def generateContextMenu(self, contextDict):
        '''
        New generates right click menu function. More MVC compliant. 
        Receives data by message from ClientGame
        '''
        # Dynamic menu generator
        menu = []
        #print 'ContextDict', contextDict
        if 'turn' in contextDict:
            menu.append(('Turn ' + str(contextDict['turn']), False, False))
            menu.append(0)
        if 'landers' in contextDict:
            menu.append(('Land...', False, self.buildLandersList(contextDict['landers'], contextDict['cell'])))
            menu.append(0)
        if 'build' in contextDict:
            menu.append(('Build...', False, self.buildBuildableList(contextDict['cell'])))
            menu.append(0)
        if self.world.gameState.getCurrentOrNextState() == 'Main':
            menu.append(('Level...', False, self.buildLevelList()))
            menu.append(('End Turn', False, self.endTurnRequest))
        menu.append(('Save Game', False, self.save))
        menu.append(('Load Game', False, self.load))
        menu.append(('Exit Game', False, self.exit))
        
        myPopupMenu=Menu.PopupMenu(
            items = tuple(menu),
            #parent = self.parent,
            baselineOffset=-.35,
            scale=.045, itemHeight=1.2, leftPad=.2,
            separatorHeight=.3,
            underscoreThickness=1,

            BGColor=(.9,.9,.8,.94),
            BGBorderColor=(.8,.3,0,1),
            separatorColor=(0,0,0,1),
            frameColorHover=(.3,.3,.3,1),
            frameColorPress=(0,1,0,.85),
            textColorReady=(0,0,0,1),
            textColorHover=(1,.7,.2,1),
            textColorPress=(0,0,0,1),
            textColorDisabled=(.65,.65,.65,1)
        )
    
    def landLander(self, landerKey, cell):
        #print 'Lander Request', landerKey, cell
        if cell[2] != 0:
            messenger.send('say', ['Landers can not be landed on subterranean surfaces.'])
            return
        messenger.send("sendData", ['requestLander', [landerKey, cell]])
    
    def save(self):
        messenger.send('requestSave')
    def load(self):
        pass


class StructureWindow(pw.StandardWindow):
    '''
    Base class for structure info widgets.  Modified widgets, such as the command center, will inherient from here.
    structureObject is passed as non-enforced read only.  Changes will send a message that is recieved by Network Server View.
        server will then impliment the change on the structure object in its end.  
        client phony structure is then updated through network.
    '''
    def __init__(self, structure):
        #pw.StandardWindow.__init__(self, title = structure.name, center=True, size = (300,300))
        pw.StandardWindow.__init__(self, title = structure.name, center=True)
        self.structure = structure
        name = DirectLabel(text = self.structure.name)
        self.pack(name)
        if self.structure.underConstruction:
            self.generateConstructionBox()
        else:
            self.generateInfo()
        closeButton = DirectButton(text='Close', parent=self, command=self.destroy)

        if self.structure.online:  onlineButtonText = 'Online'
        else: onlineButtonText = 'Offline'
        onlineButton = DirectButton(text = onlineButtonText, parent= self, scale=.2, pos =(-.6,0,-.7), command=self.toggleOnline)
        onlineButton['extraArgs'] = [onlineButton]
        
        self.addHorizontal([onlineButton, closeButton])
        self.draw()
    
    def generateInfo(self):
        """
        Overideable for custom structure windows
        """
    
    def toggleOnline(self, button):
        messenger.send("sendData", ['structureOnlineRequest', [self.structure.coords]])
        if self.structure.online: 
            #structureObject.online = False
            button['text'] = 'Offline'
        else: 
            #structureObject.online = True
            button['text'] = 'Online'
    
    def genrateInfoBox(self):
        pass
    
    def generateConstructionBox(self):
        label = DirectLabel(text = "Turns remaining: " + str(self.structure.buildTimer))        
        self.pack(label)
    
class CommandStructureWindow(StructureWindow):
    '''
    Structure widget with additional info 
    '''
    def generateInfo(self):
        pass


class Script(object):
    '''
    Imports external language yaml docs into internal dict
    '''
    def __init__(self):
        self.database = {}
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
        
        messenger.send('makePickable', [base.a2dBottomLeft])
        
        self.language = language
        self.accept("onGetMaps", self.mapSelection)
        
    def mainMenu(self):
        """
        Creates main menu
        """
        #self.mainMenu = pw.StandardWindow(title = "Open Outpost", size=(100, 100), center = True)
        self.mainMenu = pw.StandardWindow(title = self.script.getText("TXT_UI_MAINMENUTITLE"), center = True)
        #newGame = DirectButton(text= self.script.getText('TXT_UI_NEWGAME', self.language), command=self.newGame)
        login = DirectButton(text= self.script.getText('TXT_UI_LOGINMP', self.language), command=self.loginMP)
        #loadMod = DirectButton(text = "Load Mod", command = self.loadModScreen)
        closeButton = DirectButton( text='Quit',  command=self.quit)
        #self.mainMenu.addVertical([newGame, loadMod, closeButton])
        self.mainMenu.addVertical([login, closeButton])
        #self.mainMenu.box["frameColor"] = (0,0,0,1)
        #self.mainMenu.box["borderWidth"] = (1,1)

    def newGame(self):
        self.mainMenu.destroy()
        messenger.send('newSPGame')
    
    def loginMP(self):
        self.mainMenu.destroy()
        self.loginDialog = pw.StandardWindow(title = self.script.getText("TXT_UI_LOGINTITLE"), center = True)
        hostEntry = DirectEntry(initialText="localhost")
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
        #mapDialog = pw.StandardWindow(title = "Select Map", center = True)
        mapList = {}
        #mapScrollList  = DirectScrolledList(
                #decButton_pos= (0.35, 0, 0.53),
                #decButton_text = "Dec",
                #decButton_text_scale = 0.04,
                #decButton_borderWidth = (0.005, 0.005),
                #incButton_pos= (0.35, 0, -0.02),
                #incButton_text = "Inc",
                #incButton_text_scale = 0.04,
                #incButton_borderWidth = (0.005, 0.005),
                #frameSize = (0.0, 0.7, -0.05, 0.59),
                #frameColor = (1,0,0,0.5),
                #pos = (-1, 0, 0),
                #itemFrame_frameSize = (-0.2, 0.2, -0.37, 0.11),
                #itemFrame_pos = (0.35, 0, 0.4),
                #)
        
        for mapName in maps:
            
            #mapScrollList.addItem(mapName)
            # This is how Panda converts the string contents of an image file into a texture
            heightmap = maps[mapName][0]
            image = PNMImage()
            image.read(StringStream(heightmap))
            heightTexture = Texture()
            #heightTexture.load(image)
            
            #bitmap = maps[mapName][1]
            #image = PNMImage()
            #image.read(StringStream(bitmap))
            #bitmapTexture = Texture()
            #bitmapTexture.load(image)
            
        #mapDialoge.addHorizontal([mapScrollList])
        # TODO: Impliment map selection. For now we are just going to skip this
        # and use the TestRegion, load it, and see how much memory the map consumes.
        container = proto.Container()
        container.mapRequest = "TestRegion"
        messenger.send("sendData", [container])


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
        
        self.isPanning = False
        
        self.accept('mouse2', self.middleMouseDown, [])
        self.accept('mouse2-up', self.middleMouseUp, [])
        self.accept('=', self.zoomIn, [])
        self.accept('-', self.zoomOut, [])
        
        taskMgr.add(self.update,"updateCameraTask")
        
        # Zoom level. 0 is closest
        # VBase2(1.0, 0.75) is default
        self.zoom = 5
        
        #lens = base.cam.node().getLens()
        #print "Lens:", lens.getFilmSize()
    
    def middleMouseDown(self):
        #print "middleMouseDown"
        self.mousePosition0=[base.win.getPointer(0).getX(),base.win.getPointer(0).getY()]
        self.isPanning = True
        
    def middleMouseUp(self):
        #print "middleMouseUp"
        self.isPanning = False
    
    def update(self, task):
        if self.isPanning:
            mousePosition1 = [base.win.getPointer(0).getX(),base.win.getPointer(0).getY()]
            delta = [(mousePosition1[0]- self.mousePosition0[0])*0.005, (mousePosition1[1] - self.mousePosition0[1]) * 0.005]
            #print delta
            base.camera.setPos(base.camera.getPos()[0] + delta[0], base.camera.getPos()[1] - delta[1], base.camera.getPos()[2])
            
        return Task.cont
    
    def zoomIn(self):
        # We don't want to zoom in tooooo far!
        print "Zooming"
        if self.zoom < 0:
            return
        self.zoom -= 1
        lens = base.cam.node().getLens()
        print "Lens pre:", lens.getFilmSize()
        print "Lens pre:", lens.getFilmSize()[0]
        #lens.setFov(lens.getFov()/2)
        lens.setFilmSize(lens.getFilmSize()[0]/2)
        #print "Lens post:", lens.getFilmSize()
        base.cam.node().setLens(lens)
        print "Zoomed!"
    
    def zoomOut(self):
        # We don't want to zoom out tooooo far!
        print "Zooming"
        if self.zoom > 9:
            return
        self.zoom += 1
        lens = base.cam.node().getLens()
        #lens.setFilmSize(lens.getFilmSize()*2)
        #lens.setFov(lens.getFov()*2)
        base.cam.node().setLens(lens)
        print "Zoomed!"