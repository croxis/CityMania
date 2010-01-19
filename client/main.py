# -*- coding: utf-8 -*-
title="City Mania"
"""
Here it is!
"""
#setup config file
from pandac.PandaModules import loadPrcFileData
#import os

loadPrcFileData( '', 'fullscreen 0')
loadPrcFileData( '', 'win-size 800 600' )
loadPrcFileData( '', 'win-origin 450 90' )
loadPrcFileData( '', 'frame-rate-meter-scale 0.035' )
loadPrcFileData( '', 'frame-rate-meter-side-margin 0.1' )
loadPrcFileData( '', 'show-frame-rate-meter 1' )

loadPrcFileData( '', 'notify-level-util error' )
loadPrcFileData( '', 'window-title '+title )

loadPrcFileData( '', 'want-pstats 1')
loadPrcFileData( '', 'task-timer-verbose 1')
loadPrcFileData( '', 'pstats-tasks 1')

loadPrcFileData("", "interpolate-frames 1")
loadPrcFileData("", "clock-mode limited")
loadPrcFileData("", "clock-frame-rate 25")

loadPrcFileData("", "audio-library-name p3openal_audio")

#import panda modules
import direct.directbase.DirectStart
from direct.showbase import DirectObject
from pandac.PandaModules import OrthographicLens, VBase3, GeomVertexReader, Texture, Vec4
from direct.gui.OnscreenText import OnscreenText,TextNode
from direct.interval.IntervalGlobal import *
from direct.fsm import FSM
from direct.gui.DirectGui import *

#import python modules
import sys, subprocess, math
#import logging

#import custom modules
import gui
#from Structure import Structure, loadStructures, StructureGraphic
#import Game
#import Map
#import Audio
import network
#import filesystem


#define constants
#SIZE=65 # has to be a 2 exponent number plus one
#ALT=1.0
#RETRO=True
#SUBDIVIDE=3

# From Camera.py
from pandac.PandaModules import NodePath,Vec3,Point3, GeoMipTerrain, PNMImage, StringStream, TextureStage
from direct.task.Task import Task    

#This below belongs here
from direct.gui.DirectGui import *
from pandac.PandaModules import CollisionTraverser,CollisionHandlerQueue,CollisionNode,CollisionRay,GeomNode
class World(DirectObject.DirectObject):
    def __init__(self):
        """initialize"""
        self.server = None
        self.language = 'english'
        self.singlePlayer = False
        self.accept('exit', self.exit)
        
        base.disableMouse()
        
        base.setFrameRateMeter(True)
        render.setShaderAuto()
        self.keys()
        
        # Initialize classes
        #base.camera.node().clearEffects()
        #self.camera = gui.Camera()
        self.lights = gui.Lights(self, lightsOn = True, showLights = True)
        
        self.root = NodePath('rootMain')
        self.root.reparentTo(render)
        
        #self.picker = Picker(self)
        
        self.terrainManager = TerrainManager()
        
        
        # Load the structure database
        #self.structuresDatabase = loadStructures()
        # GUI
        #self.contextMenu = ContextMenu(None, self.structuresDatabase, #self.terrainManager, self)
        #self.structureWidget = StructureWidget()
        #self.script = Script(self)
        #self.guiController = GUIController(self.script)
        #self.level = 0
        #self.guiController.mainMenu()
        #self.gameState = PhonyGameState(self)
        #self.game = Game.ClientGame()
        #create traverser
        #base.cTrav = CollisionTraverser()
        #create collision ray
        #self.createRay(self,base.camera,name="mouseRay",show=True)
        #self.accept('mouse1', self.mouse_pick, [self.queue])
        self.accept('makePickable', self.makePickable)
    
    def mouseLeft(self,pickedObj,pickedPoint):
        if pickedObj==None:  return
        #print "mouseLeft", pickedObj, pickedPoint
        cell=(int(math.floor(pickedPoint[0])),int(math.floor(pickedPoint[1])))
        #messenger.send('cellCoords', [cell,])
        print cell  
    
    def mouse_pick(self, queue):
        #print "Mousepick"
        #get mouse coords
        if base.mouseWatcherNode.hasMouse()==False: return
        mpos=base.mouseWatcherNode.getMouse()
        #locate ray from camera lens to mouse coords
        self.ray.setFromLens(base.camNode, mpos.getX(),mpos.getY())
        #get collision: picked obj and point
        pickedObj,pickedPoint=self.getCollision(queue)
        self.mouseLeft(pickedObj,pickedPoint)
        
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
    
        
    def keys(self):
        """keys"""
        base.accept("w", base.toggleWireframe)
        self.accept('t',self.toggleTexture)
        self.accept('s',self.snapShot)
    def snapShot(self):
        base.screenshot("Snapshot")
    
    def toggleTexture(self):
        base.toggleTexture()

    def exit(self):
        print "Exit"
        messenger.send("sendData", ['killServerRequest'])
        #base.closeWindow(base.win)
        sys.exit()
        

class TerrainManager(DirectObject.DirectObject):
    '''
    Manages the creation and display of terrain levels
    '''
    def __init__(self):
        self.accept('generateRegion', self.generateWorld)
        self.accept("regionView_normal", self.regionViewNormal)
        self.accept("regionView_owners", self.regionViewOwners)
        self.accept("regionView_foundNew", self.regionViewFound)
        self.terrains=[]   
        base.cTrav = CollisionTraverser()
        self.createRay(self,base.camera,name="mouseRay",show=True)
    
    def generateWorld(self, container):
        terrain = GeoMipTerrain("surface")
        self.regionTerrain = GeoMipTerrain("region_surface")
        root = terrain.getRoot()
        root.reparentTo(render)
        root.setSz(100)
        self.regionTerrain.getRoot().setSz(100)
        root.setShaderAuto()
        messenger.send('makePickable', [root])
        messenger.send("makePickable", [self.regionTerrain.getRoot()])
        self.active_terrain = terrain
        
        import base64
        heightmap = PNMImage()
        imageString = base64.b64decode(container.heightmap)
        heightmap.read(StringStream(imageString))
        
        terrain.setHeightfield(heightmap)
        terrain.setBruteforce(True)
        #terrain.setFocalPoint(base.camera)
        self.regionTerrain.setHeightfield(heightmap)
        self.regionTerrain.setBruteforce(True)
        
        terrain.generate()
        self.regionTerrain.generate()
        
        self.terrains.append(terrain)
        
        colormap = PNMImage(heightmap.getXSize(), heightmap.getYSize())
        colormap.addAlpha()
        slopemap = terrain.makeSlopeImage()
        
        # Iterate through every pix of color map. This will be very slow so until faster method is developed, use sparingly
        # getXSize returns pixles length starting with 1, subtract 1 for obvious reasons
        for x in range(0, colormap.getXSize()-1):
            for y in range(0, colormap.getYSize()-1):
                # Else if statements used to make sure one channel is used per pixel
                # Also for some optimization
                # Snow. We do things funky here as alpha will be 1 already.
                if heightmap.getGrayVal(x, y) < 200:
                    colormap.setAlpha(x, y, 0)
                else:
                    colormap.setAlpha(x, y, 1)
                # Beach. Estimations from http://www.simtropolis.com/omnibus/index.cfm/Main.SimCity_4.Custom_Content.Custom_Terrains_and_Using_USGS_Data
                if heightmap.getGrayVal(x,y) < 62:
                    colormap.setBlue(x, y, 1)
                # Rock
                elif slopemap.getGrayVal(x, y) > 170:
                    colormap.setRed(x, y, 1)
                else:
                    colormap.setGreen(x, y, 1)
        
        colorTexture = Texture()
        colorTexture.load(colormap)
        colorTS = TextureStage('color')
        colorTS.setSort(0)
        colorTS.setPriority(1)
        
        # Textureize
        grassTexture = loader.loadTexture("Textures/grass.png")
        grassTS = TextureStage('grass')
        grassTS.setSort(1)
        
        rockTexture = loader.loadTexture("Textures/rock.jpg")
        rockTS = TextureStage('rock')
        rockTS.setSort(2)
        rockTS.setCombineRgb(TextureStage.CMAdd, TextureStage.CSLastSavedResult, TextureStage.COSrcColor, TextureStage.CSTexture, TextureStage.COSrcColor)
        
        sandTexture = loader.loadTexture("Textures/sand.jpg")
        sandTS = TextureStage('sand')
        sandTS.setSort(3)
        sandTS.setPriority(5)
        
        snowTexture = loader.loadTexture("Textures/ice.png")
        snowTS = TextureStage('snow')
        snowTS.setSort(4)
        snowTS.setPriority(0)
        
        # Grid for city placement and guide and stuff
        gridTexture = loader.loadTexture("Textures/grid.png")
        gridTexture.setWrapU(Texture.WMRepeat)
        gridTexture.setWrapV(Texture.WMRepeat)
        gridTS = TextureStage('grid')
        gridTS.setSort(5)
        gridTS.setPriority(10)        
                
        # Set multi texture
        # Source http://www.panda3d.org/phpbb2/viewtopic.php?t=4536
        
        if colormap.getXSize() > colormap.getYSize():
            size = colormap.getXSize()-1
        else:
            size = colormap.getYSize()-1
        self.size = size
        
        root.setTexture( colorTS, colorTexture ) 
        root.setTexture( grassTS, grassTexture )
        root.setTexScale(grassTS, size, size) 
        root.setTexture( rockTS, rockTexture ) 
        root.setTexScale(rockTS, size, size) 
        root.setTexture( sandTS, sandTexture) 
        root.setTexScale(sandTS, size, size) 
        root.setTexture( snowTS, snowTexture ) 
        root.setTexScale(snowTS, size, size) 
        root.setTexture( gridTS, gridTexture ) 
        root.setTexScale(gridTS, size, size)
        
        root.setShaderInput('size', size, size, size, size)
        root.setShader(loader.loadShader('Shaders/terraintexture.sha')) 
        terrain.update()
        
        # Getting messy in here eh?
        citycolors = {}
        citymap = PNMImage(heightmap.getXSize()-1, heightmap.getYSize()-1)
        import random
        #citymap.addAlpha()
        
        for city in container.cities:
            citycolors[city.id] = Vec3(random.rand(), random.rand(), random.rand())
        
        tiles = container.tiles
        # List with city id
        all_tiles = []
        position = 0
        # Expand tile list
        for x in range(0, heightmap.getXSize()-1 * heightmap.getYSize()-1):
            all_tiles.append(0)
        
        tiles = container.tiles
        print tiles
        
        for tile in container.tiles:
            if tile.cityid:                    
                citymap.setXel(tile.positionx, tile.positiony, citycolors[tile.cityid])
                citymap.setAlpha(tile.positionx, tile.positiony, 1)
                print "Owner detected"
            else:
                citymap.setXel(tile.positionx, tile.positiony, 1.0)
        
        

        cityTexture = Texture()
        cityTexture.load(citymap)
        cityTS = TextureStage('citymap')
        cityTS.setSort(0)
        
        self.regionTerrain.getRoot().setTexture(cityTS, cityTexture)
        self.regionTerrain.getRoot().setTexture(gridTS, gridTexture)
        self.regionTerrain.getRoot().setTexScale(gridTS, size, size)
        self.regionTerrain.update()
        
        print "Done with terrain generation"
        camera = gui.Camera()
        #camera = gui.CameraHandler()
        #camera.setPanLimits(-20, size+20, -20, size+20)
        #task = taskMgr.add(self.updateTerrain, "updateTerrain")
        messenger.send("finishedTerrainGen")
    
    #def updateTerrain(self, task):
    #    root = self.active_terrain.getRoot()
    #    position = self.getMouseCell(self.queue)
    #    if position:
    #        print "Position:", position
    #        #root.setTexOffset(self.tileTS, float(position[0])/self.size, float(position[1])/self.size)
    #        #root.setTexOffset(self.tileTS, float(position[0]), float(position[1]))      
    #    try:
    #        #print "Position:", position
    #        #print root.getTexOffset(self.tileTS)
    #        pass
    #    except:
    #        #print "error", position
    #        pass
    #    return Task.cont
    
    def getMouseCell(self, queue):
        #print "Mousepick"
        #get mouse coords
        #if base.mouseWatcherNode.hasMouse()==False: return "Mouse is theved"
        if base.mouseWatcherNode.hasMouse()==False: return
        mpos=base.mouseWatcherNode.getMouse()
        #locate ray from camera lens to mouse coords
        self.ray.setFromLens(base.camNode, mpos.getX(),mpos.getY())
        #get collision: picked obj and point
        pickedObj,pickedPoint=self.getCollision(queue)
        if pickedObj==None:  return
        cell=(int(math.floor(pickedPoint[0])),int(math.floor(pickedPoint[1])))
        return cell
        
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
    
    def regionViewNormal(self):
        self.regionTerrain.getRoot().detachNode()
        self.terrains[0].getRoot().reparentTo(render)
        self.active_terrain = self.terrains[0]
    
    def regionViewOwners(self):
        self.terrains[0].getRoot().detachNode()
        self.regionTerrain.getRoot().reparentTo(render)
        self.active_terrain = self.regionTerrain
    
    def regionViewFound(self):
        '''Gui for founding a new city!'''
        root = self.regionTerrain.getRoot()
        task = taskMgr.add(self.newTerrainOverlay, "newTerrainOverlay")
        tileTexture = loader.loadTexture("Textures/tile2.png")
        tileTexture.setWrapU(Texture.WMClamp)
        tileTexture.setWrapV(Texture.WMClamp)
        self.tileTS = TextureStage('tile')
        self.tileTS.setSort(6)
        #self.tileTS.setMode(TextureStage.MBlend)
        self.tileTS.setMode(TextureStage.MDecal)
        #self.tileTS.setColor(Vec4(1,0,1,1))
        root.setTexture(self.tileTS, tileTexture)
        root.setTexScale(self.tileTS, self.size/32, self.size/32)
        self.acceptOnce("mouse1", self.regionViewFound2)
    
    def newTerrainOverlay(self, task):
        root = self.active_terrain.getRoot()
        position = self.getMouseCell(self.queue)
        if position:
            # Check to make sure we do not og out of bounds
            if position[0] < 16:
                position = (16, position[1])
            elif position[0] > self.size-16:
                position = (self.size-16, position[1])
            if position[1] < 16:
                position = (position[0], 16)
            elif position [1] > self.size-16:
                position = (position[0], self.size-16)                
            root.setTexOffset(self.tileTS, -float(position[0]-16)/32, -float(position[1]-16)/32)
        return Task.cont
    
    def regionViewFound2(self):
        '''Grabs cell location for founding.
        The texture coordinate is used as the mouse may enter an out of bounds area.
        '''
        root = self.active_terrain.getRoot()
        root_position = root.getTexOffset(self.tileTS)
        # We offset the position of the texture, so we will now put the origin of the new city not on mouse cursor but the "bottom left" of it. Just need to add 32 to get other edge
        position = [int(abs(root_position[0]*32)), int(abs(root_position[1]*32))]
        print "Position of new city is:", position
        print "The bounds are:", position[0], position[0]+32, position[1]+32, position[1]
        taskMgr.remove("newTerrainOverlay")
        messenger.send("found_city_name", [position])
            

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open("client.raw", "w")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)  
        
    def close(self):
        self.log.close()

def loadMod(name):
    """
    Loads the designated mod into memory, will require some helper functions in other classes
    """

def main(var = None):
    # Create the directories
    #filesystem.home(oo = True)
    #print "Path:", filesystem.home()

    #LOG_FILENAME = 'client.log'
    #logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,)
    
    sys.stdout = Logger()
    connection = network.ServerSocket()
    
    script = gui.Script()
    
    #messenger.toggleVerbose()

    #aiVoice = Audio.AIVoice()
    #audioManager = Audio.AudioManager()

    world=World()
    #camera = gui.Camera()
    #camera = gui.CameraHandler()
    guiController = gui.GUIController(script)
    guiController.mainMenu()
    serverHost = 'localhost'
    serverPort = 52003

    run()

if __name__ == '__main__':
    main()
