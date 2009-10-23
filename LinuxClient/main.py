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

#if os.name == "nt":
#    loadPrcFileData( '', 'load-display pandadx9' )
#else:
#    loadPrcFileData( '', 'load-display pandagl' )
loadPrcFileData( '', 'notify-level-util error' )
loadPrcFileData( '', 'window-title '+title )

#loadPrcFileData( '', 'want-pstats 1')
#loadPrcFileData( '', 'task-timer-verbose 1')
#loadPrcFileData( '', 'pstats-tasks 1')

loadPrcFileData("", "interpolate-frames 1")
loadPrcFileData("", "clock-mode limited")
loadPrcFileData("", "clock-frame-rate 25")

loadPrcFileData("", "audio-library-name p3openal_audio")
#loadPrcFileData("", "direct-gui-edit 1")

#import panda modules
import direct.directbase.DirectStart
from direct.showbase import DirectObject
from pandac.PandaModules import OrthographicLens, VBase3, GeomVertexReader
from direct.gui.OnscreenText import OnscreenText,TextNode
from direct.interval.IntervalGlobal import *
from direct.fsm import FSM
from direct.gui.DirectGui import *

#import python modules
import sys, subprocess, logging

#import custom modules
import gui
#from Structure import Structure, loadStructures, StructureGraphic
#import Game
#import Map
#import Audio
import network
#import filesystem

#import Axis.ThreeAxisGrid as TAG
#from Axis import ThreeAxisGrid

#define constants
SIZE=65 # has to be a 2 exponent number plus one
ALT=1.0
RETRO=True
SUBDIVIDE=3

# From Camera.py
from pandac.PandaModules import NodePath,Vec3,Point3
from direct.task.Task import Task

#import Meshes

#This below belongs here
class World(DirectObject.DirectObject):
    def __init__(self):
        """initialize"""
        self.server = None
        self.language = 'english'
        self.singlePlayer = False
        self.accept('exit', self.exit)
        self.accept('newSPGame', self.launchSPServer)

        base.setFrameRateMeter(True)
        #self.toggleWireFrame()
        self.keys()
        
        # Initialize classes
        self.camera = None
        
        self.root = NodePath('rootMain')
        self.root.reparentTo(render)
        
        #self.picker = Picker(self)
        
        #self.terrainManager = TerrainManager(self)
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
        
    def keys(self):
        """keys"""
        self.accept('w',self.toggleWireFrame)
        self.accept('t',self.toggleTexture)
        self.accept('s',self.snapShot)
    def snapShot(self):
        base.screenshot("Snapshot")
    def toggleWireFrame(self):
        base.toggleWireframe()
    def toggleTexture(self):
        base.toggleTexture()
        
    def generateWorld(self, grid, theme):
        self.lights = gui.Lights(self, lightsOn = True, showLights = False)
        camera.node().clearEffects()
        #self.camera = Camera(self, isometric = False)
        self.camera = gui.Camera(self, isometric = True)

    def exit(self):
        print "Exit"
        messenger.send("sendData", ['killServerRequest'])
        #base.closeWindow(base.win)
        sys.exit()
    
    def launchServer(self):
        self.server = subprocess.Popen([sys.executable, 'Server.py', 'SP'])
    
    def launchSPServer(self):
        import socket
        serverSocket = socket.socket()
        serverSocket.settimeout(0.25)
        self.launchServer()
        z = True
        HOST = ''                 # Symbolic name meaning all available interfaces
        PORT = 50007              # Arbitrary non-privileged port
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, PORT))
        s.listen(1)
        while z:
            conn, addr = s.accept()
            z = False
        conn.close()
        messenger.send('connect')


class TerrainManager(DirectObject.DirectObject):
    '''
    Manages the creation and display of terrain levels
    '''
    def __init__(self, ancestor):
        self.accept('readyStartGame', self.generateWorld)
        self.accept('switchLevelRequest', self.switchLevel)
        self.terrains = []
        self.ancestor = ancestor
        self.root = NodePath('rootTerrainManager')
        self.root.reparentTo(self.ancestor.root)
    
    def generateWorld(self, grid, type):
        for i in range(len(grid)):
            terrain = Map.Terrain(self, data=grid[i], z=i, theme = type, mappath=filesystem.home()+"Maps/Client/Random/")
            terrain.root.setPos(0,0,i*-5)
            terrain.root.setHpr(-45,0,0)
            axis = ThreeAxisGrid(zsize = 0)
            gridnodepath = axis.create()
            gridnodepath.reparentTo(terrain.root)
            gridnodepath.setPos(0,0,0.01)
            if i > 0:
                terrain.root.setAlphaScale(0)
                terrain.root.hide()
            # Looks for any structures and erect proper graphics
            for x in range(len(terrain.data)):
                for y in range(len(terrain.data[x])):
                    if terrain.data[x][y]['structure']:
                        if terrain.data[x][y]['structure'].underConstruction:
                            structureGraphic = StructureGraphic(terrain, terrain.data[x][y]['structure'].structureID, [(x,y,i)])
                        else: 
                            structureGraphic = StructureGraphic(terrain, terrain.data[x][y]['structure'].structureID, [(x,y,i)], structureObject = terrain.data[x][y]['structure'])
                        terrain.data[x][y]['structureGraphic'] = structureGraphic
            
            self.terrains.append([terrain, axis, gridnodepath])
    
    def getTerrain(self, level):
        '''
        Returns the terrain object for a given level
        '''
        return self.terrains[level][0]
    def switchLevel(self, level):
        self.terrains[level][0].root.show()
        move = LerpPosInterval(self.root, 3, VBase3(0, 0, level*10), blendType = 'easeInOut')
        alphaFade = LerpFunc(self.fadeOut, duration = 1.25, name = 'fadeout', extraArgs = [self.ancestor.level])
        alphaIn = LerpFunc(self.fadeIn, duration = 1.25, name = 'fadein', extraArgs = [level])
        fadeSequ = Sequence(alphaFade, Wait(0.5), alphaIn)
        parallel = Parallel(move, fadeSequ, name = 'Level Mover')
        self.terrains[self.ancestor.level][1].parentNodePath.hide()
        parallel.start()
        self.terrains[level][1].parentNodePath.show()
        self.ancestor.level = level
        #print 'Level:', level
    def fadeOut(self, time, oldLevel):
        self.terrains[oldLevel][0].root.setAlphaScale(1-time)
        if 1-time < 0.1: self.terrains[oldLevel][0].root.hide()
    def fadeIn(self, time, level):
        #print self.terrains[level][0].root.getColorScale()
        if time == 0: self.terrains[level][1].parentNodePath.hide()
        elif time == 1: self.terrains[level][1].parentNodePath.show()
        self.terrains[level][0].root.setAlphaScale(time)
    

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

def main():
    # Create the directories
    #filesystem.home(oo = True)
    #print "Path:", filesystem.home()

    LOG_FILENAME = 'client.log'
    logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,)
    
    sys.stdout = Logger()
    connection = network.ServerSocket()
    #connection.start()
    
    script = gui.Script()
    
    #messenger.toggleVerbose()

    #aiVoice = Audio.AIVoice()
    #audioManager = Audio.AudioManager()

    world=World()
    guiController = gui.GUIController(script)
    guiController.mainMenu()
    serverHost = 'localhost'
    serverPort = 52003
    #client = Network.Client(serverHost, serverPort)
    #nsc =  Network.NetworkServerController()

    run()

if __name__ == '__main__':
    main()
