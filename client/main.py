# -*- coding: utf-8 -*-
title="City Mania"
#setup config file
from pandac.PandaModules import loadPrcFileData
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

#loadPrcFileData("", "interpolate-frames 1")
#loadPrcFileData("", "clock-mode limited")
#loadPrcFileData("", "clock-frame-rate 25")

loadPrcFileData("", "sync-video 0")

loadPrcFileData("", "audio-library-name p3openal_audio")

#import panda modules
import direct.directbase.DirectStart
from direct.showbase import DirectObject
from pandac.PandaModules import OrthographicLens, VBase3, GeomVertexReader, Texture, Vec4
from direct.gui.OnscreenText import OnscreenText,TextNode
from direct.interval.IntervalGlobal import *
from direct.fsm import FSM
from direct.gui.DirectGui import *
#from panda3d.core import NodePath, CollisionTraverser,CollisionHandlerQueue,CollisionNode,CollisionRay,GeomNode, GeoMipTerrain,  PNMImage, StringStream, TextureStage, Vec3, VBase3D
from panda3d.core import CardMaker, TransparencyAttrib, BitMask32, Plane, Point3, PlaneNode, CullFaceAttrib
from pandac.PandaModules import NodePath, CollisionTraverser,CollisionHandlerQueue,CollisionNode,CollisionRay,GeomNode, GeoMipTerrain,  PNMImage, StringStream, TextureStage, Vec3, VBase3D
from direct.task.Task import Task    

#import python modules
import sys, subprocess, math
sys.path.append("..")
#import logging

import gui
import network
#from common.tile import Tile
from tile import Tile
import region
import water

picker = gui.getPicker()

class World(DirectObject.DirectObject):
    def __init__(self):
        """initialize"""
        self.server = None
        self.language = 'english'
        self.singlePlayer = False
        self.accept('exit', self.exit)
        
        base.disableMouse()
        
        base.setFrameRateMeter(True)
        self.keys()
        
        # Initialize classes
        self.lights = gui.Lights(self, lightsOn = True, showLights = True)
        
        self.root = NodePath('rootMain')
        self.root.reparentTo(render)
        
        #self.picker = Picker(self)
        
        self.terrainManager = TerrainManager()
    
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
        self.accept("updateRegion", self.updateRegion)
        self.terrains=[]   
        
        self.accept("mouse1", self.lclick)
        self.waterType = 2
        self.water = None
        self.accept("h", self.switchWater)
        
        # view 0: region view
        # view #: cityid view
        self.view = 0
    
    def generateWorld(self, heightmap, tiles, cities, container):
        terrain = GeoMipTerrain("surface")
        terrain.setFocalPoint(base.camera)
        
        root = terrain.getRoot()
        root.reparentTo(render)
        root.setSz(100)
        
        
        self.active_terrain = terrain
        terrain.setHeightfield(heightmap)
        #terrain.setBruteforce(True)
        terrain.setFocalPoint(base.camera)
        terrain.setBlockSize(64)
        #terrain.setNear(40)
        #terrain.setFar(100)
        
        self.regionTerrain = GeoMipTerrain("region_surface")
        self.regionTerrain.getRoot().setSz(100)
        self.regionTerrain.setHeightfield(heightmap)
        self.regionTerrain.setBruteforce(True)
        
        messenger.send('makePickable', [root])
        messenger.send("makePickable", [self.regionTerrain.getRoot()])
        
        terrain.generate()
        self.regionTerrain.generate()
        
        self.terrains.append(terrain)
        
        colormap = self.generateColorMap(heightmap)
        
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
        self.citycolors = {0: VBase3D(1, 1, 1)}
        citymap, citylabels = self.generateCityMap(cities, tiles)
        
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
        
        self.generateWater(2)
                
        # Skybox
        self.att_skybox = water.SkyDome2(render)
        self.att_skybox.setStandardControl()
        
        taskMgr.add(self.updateTerrain, "updateTerrain")
        messenger.send("finishedTerrainGen")
        messenger.send("updateCityLabels", [citylabels, terrain])
    
    def generateWater(self, style):
        '''Generates water
        style 0: blue card
        style 1: reflective card
        style 2: reflective card with shaders
        '''
        if self.water:
            self.water.removeNode()
        if style is 0:
            cm = CardMaker("water")
            cm.setFrame(-1, 1, -1, 1)
            cm.setColor(0, 0, 1, 0.9)
            self.water = render.attachNewNode(cm.generate())
            self.water.setScale(512)
            self.water.lookAt(0, 0, -1)
            self.water.setZ(22)
            messenger.send('makePickable', [self.water])
        elif style is 1:
            # From Prosoft's super awesome terrain demo
            cm = CardMaker("water")
            cm.setFrame(-1, 1, -1, 1)
            self.water = render.attachNewNode(cm.generate())
            self.water.setScale(512)
            self.water.lookAt(0, 0, -1)
            self.water.setZ(22)
            self.water.setShaderOff(1)
            self.water.setLightOff(1)
            self.water.setAlphaScale(0.5)
            self.water.setTransparency(TransparencyAttrib.MAlpha)
            wbuffer = base.win.makeTextureBuffer("water", 512, 512)
            wbuffer.setClearColorActive(True)
            wbuffer.setClearColor(base.win.getClearColor())
            self.wcamera = base.makeCamera(wbuffer)
            self.wcamera.reparentTo(render)
            self.wcamera.node().setLens(base.camLens)
            self.wcamera.node().setCameraMask(BitMask32.bit(1))
            self.water.hide(BitMask32.bit(1))
            wtexture = wbuffer.getTexture()
            wtexture.setWrapU(Texture.WMClamp)
            wtexture.setWrapV(Texture.WMClamp)
            wtexture.setMinfilter(Texture.FTLinearMipmapLinear)
            self.wplane = Plane(Vec3(0, 0, 1), Point3(0, 0, self.water.getZ()))
            wplanenp = render.attachNewNode(PlaneNode("water", self.wplane))
            tmpnp = NodePath("StateInitializer")
            tmpnp.setClipPlane(wplanenp)
            tmpnp.setAttrib(CullFaceAttrib.makeReverse())
            self.wcamera.node().setInitialState(tmpnp.getState())
            self.water.projectTexture(TextureStage("reflection"), wtexture, self.wcamera)
            messenger.send('makePickable', [self.water])
        elif style is 2:
            # From Clcheung just as super awesome demomaster
            self.water_level = Vec4(0.0, 0.0, 22.0, 1.0)
            self.water = water.WaterNode(0, 0, 512, 512, self.water_level.getZ())
            self.water.setStandardControl()
            self.water.changeParams(None)
            wl=self.water_level
            wl.setZ(wl.getZ()-0.05)
            #root.setShaderInput('waterlevel', self.water_level)
            render.setShaderInput('time', 0)
            messenger.send('makePickable', [self.water.waterNP])
    
    def switchWater(self):
        self.waterType += 1
        if self.waterType > 2:
            self.waterType = 0
        self.generateWater(self.waterType)
        
    def updateTerrain(self, task):
        '''Updates terrain and water'''
        self.terrains[0].update()
        # Water
        if self.waterType is 2:
            pos = base.camera.getPos()
            render.setShaderInput('time', task.time)
            mc = base.camera.getMat( )
            self.water.changeCameraPos(pos,mc)
            self.water.changeCameraPos(pos,mc)
        #print "Render diagnostics"
        #render.analyze()
        #base.cTrav.showCollisions(render)
        return task.cont        
        
    def lclick(self):
        cell = picker.getMouseCell()
        print "Cell:", cell
        if not self.view:
            messenger.send("clickForCity", [cell])
    
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
        tileTexture = loader.loadTexture("Textures/tile.png")
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
        position = picker.getMouseCell()
        if position:
            # Check to make sure we do not go out of bounds
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
        root.clearTexture(self.tileTS)
        messenger.send("found_city_name", [position])
    
    def generateColorMap(self, heightmap):
        colormap = PNMImage(heightmap.getXSize(), heightmap.getYSize())
        colormap.addAlpha()
        slopemap = self.terrains[0].makeSlopeImage()
        
        # Iterate through every pix of color map. This will be very slow so until faster method is developed, use sparingly
        # getXSize returns pixles length starting with 1, subtract 1 for obvious reasons
        for x in range(0, heightmap.getXSize()-1):
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
        return colormap
    
    def generateCityMap(self, cities, tiles):
        '''Generates a simple colored texture to be applied to the city info region overlay.
        Due to different coordinate systems (terrain org bottom left, texture top left)
        some conversions are needed,
        
        Also creates a citylabels dict for the region view
        '''
        citymap = PNMImage(self.size, self.size)
        citylabels = cities
        scratch = {}
        #citymap.addAlpha()
        import random
        
        # Setup for city labels
        for ident in cities:
            scratch[ident] = []
        
        # conversion for y axis
        ycon = []
        s = self.size - 1
        for y in range(self.size):
            ycon.append(s)
            s -= 1
        for ident, city in cities.items():
            if ident not in self.citycolors:
                self.citycolors[ident] = VBase3D(random.random(), random.random(), random.random())
        for tile in tiles:
            # X Y is flipped with a converter. Too tired to figure out why,
            citymap.setXel(tile.coords[1], ycon[tile.coords[0]], self.citycolors[tile.cityid])
            # Scratch for labeling
            if tile.cityid:
                scratch[tile.cityid].append((tile.coords[0], tile.coords[1]))
        for ident, values in scratch.items():
            xsum = 0
            ysum = 0
            n = 0
            for coords in values:
                xsum += coords[0]
                ysum += coords[1]
                n += 1
            xavg = xsum/n
            yavg = ysum/n
            citylabels[ident]["position"] = (xavg, yavg)
        return citymap, citylabels
    
    def updateRegion(self, heightmap, tiles, cities):
        #colormap = self.generateColorMap(heightmap)
        #colorTexture = Texture()
        #colorTexture.load(colormap)
        #colorTS = TextureStage('color')
        #colorTS.setSort(0)
        #colorTS.setPriority(1)
        
        #self.terrains[0].getRoot().setTexture( colorTS, colorTexture ) 
        #self.terrains[0].update()
        
        citymap, citylabels = self.generateCityMap(cities, tiles)
        
        cityTexture = Texture()
        cityTexture.load(citymap)
        cityTS = TextureStage('citymap')
        cityTS.setSort(0)
        
        self.regionTerrain.getRoot().setTexture(cityTS, cityTexture)
        self.regionTerrain.update()
        messenger.send("updateCityLabels", [citylabels, self.terrains[0]])
        
        
        


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
    reg = region.Region()
    run()

if __name__ == '__main__':
    main()
