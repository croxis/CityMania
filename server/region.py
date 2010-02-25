# -*- coding: utf-8 -*-
"""
region.py
Class for server region, esentially the master model
"""
import engine
import city
import Image
import base64, math
import StringIO
import users
import sys
sys.path.append("..")
from common.tile import Tile
import common.protocol_pb2 as proto
#import .common.tile
import logging
logger = logging.getLogger('server.region')

class Region(engine.Entity):
    def __init__(self):
        self.accept("generateRegion", self.generate)
        self.accept("newCityRequest", self.newCity)
        self.accept("sendGameState", self.sendGameState)
        self.accept("requestUnfoundCity", self.unfoundCity)
        self.accept("requestEnterCity", self.checkEnterCity)
        self.name = "Region"
        # Dict to use cityid as quick lookup
        self.cities = {}
        # Arbatary city limit. End user can set this
        self.city_limit = 32
        self.tiles = []
        self.terrainTextureDB = {}
        self.width= 0
        self.height = 0

    def generate(self, name, heightmap):
        """
        Generates region
        heightmap is a grayscale bitmap for height
        colormap is color bitmap for terrain texture
        terrainTextureDB is data on texture to use for color map
        """
        self.heightmap = heightmap
        heightmapBuffer = StringIO.StringIO(self.heightmap)
        heightmapImage = Image.open(heightmapBuffer)
        self.width, self.height = heightmapImage.size
        # Image is 1 px more than number of tiles
        self.width -= 1
        self.height -= 1
        self.name = name
        # Generate the simulation tiles
        tileid = 0
        for y in range(self.height):
            for x in range(self.width):
                tile = Tile(tileid, coords=(x,y))
                self.tiles.append(tile)
                tileid+= 1
        # Other generations such as initial roads, etc, is done here
        self.sendGameState()
    
    def sendGameState(self, peer=None):
        '''Sends game state. Requires full simulation pause while in progress.
        In this region package tiles are sent by changes in city id. No other data needs to be sent until a city is activated.
        '''
        messenger.send("setServerState", [1])
        container = proto.Container()
        container.gameState.name = self.name
        container.gameState.heightmap = base64.b64encode(self.heightmap)
        # Used to check for change
        tilecityid = -1
        for tile in self.tiles:
            if tile.cityid != tilecityid:
                tilecityid = tile.cityid
                t = container.gameState.tiles.add()
                t.id = tile.id
                t.positionx = tile.coords[0]
                t.positiony = tile.coords[1]
                t.cityid = tile.cityid
        
        for ident, city in self.cities.items():
            c = container.gameState.cities.add()
            c.id = ident
            c.name = city.name
            c.mayor = city.mayor
            c.population = city.population
            c.funds = city.funds
        
        if peer:
            messenger.send("sendData", [peer, container])
        else:
            messenger.send("broadcastData", [container])
        # TODO: Create method to return to previous server state after we finished sending
    
    def getCityTiles(self, cityid):
        '''Returns tiles for a particular city.'''
        # Itterate, yuck and slow. This should only be called when a city loads
        cityTiles = []
        for tile in self.tiles:
            if tile.cityid is cityid:
                cityTiles.append(tile)
        return cityTiles
    
    def getTile(self, x, y):
        '''Returns tile by coordinate. 
        Thankfully smart enough to find a way to not iterate
        '''
        value = y * self.width + x
        return self.tiles[value]
    
    def loadCity(self, cityKey, playerName, password=""):
        """
        loads a city based on cityKey
        """
        self.cities[cityKey].login(playerName, password="")
    
    def newCity(self, peer, info):
        '''Checks to make sure city location is valid. 
        If so we establish city!
        '''
        for x in range(0, 32):
            for y in range(0,32):
                tile = self.getTile(info.positionx+x, info.positiony+y)
                if tile.cityid:
                    container = proto.Container()
                    container.newCityResponse.type = 0
                    container.newCityResponse.message = "A city already claims tile " + str((info.positionx+x, info.positiony+y))
                    messenger.send("sendData", [peer, container])
                    return
        
        # Grab next free id. If we are at region city limit then no build!
        cityids = self.cities.keys()
        cityid = 1
        for n in range(1, self.city_limit):
            if n not in cityids:
                cityid = n
                break
        else:
            container = proto.Container()
            container.newCityResponse.type = 0
            container.newCityResponse.message = "This region has reached its max limit of  " + str(self.city_limit) + " cities."
            messenger.send("sendData", [peer, container])
            return
        
        # Passed the test! Time to found!
        user = users.getNameFromPeer(peer)
        newcity = city.City(info.name, cityid, mayor = user)
        self.cities[cityid] = newcity
        updated_tiles = []
        for y in range(0, 32):
            for x in range(0,32):
                tile = self.getTile(info.positionx+x, info.positiony+y)
                tile.cityid = cityid
                updated_tiles.append(tile)
        
        container = proto.Container()
        container.newCityResponse.type = 1
        #messenger.send("sendData", [peer, container])
        print info.name, "founded with", newcity.funds
        
        #container = proto.Container()
        container.newCity.id = cityid
        container.newCity.name = info.name
        container.newCity.mayor = user
        container.newCity.population = newcity.population
        container.newCity.funds = newcity.funds
        #messenger.send("broadcastData", [container])
        
        #container = proto.Container()
        for tile in updated_tiles:
            self.updateTile(container, tile)
        messenger.send("broadcastData", [container])
    
    def unfoundCity(self, peer, ident):
        '''Checks permissions and, if all good, unfounds city.'''
        # Can't unfound the region or a city that doesn't exist
        logging.debug("Requesting to unfound city %s by %s" %(ident, peer))
        container = proto.Container()
        if not ident or ident not in self.cities:
            container.response = "Can not unfound imaginary city."
            messenger.send("sendData", [peer, container])
            return
        
        user = users.getNameFromPeer(peer)
        access = users.getType(user)
        
        if access > 1 or self.cities[ident].mayor == user:
            for tile in self.tiles:
                if tile.cityid is ident:
                    tile.cityid = 0
                    self.updateTile(container, tile)
            del self.cities[ident]
            container.unfoundCity = ident
            messenger.send("broadcastData", [container])
        else:
            container.response = "Lack permissions for unfounding this city."
            messenger.send("sendData", [peer, container])
        logging.info("City %s unfounded. New city db: %s" %(ident, self.cities))
    
    def checkEnterCity(self, peer, ident):
        '''Checks if user can enter city and if so, what permissions.'''
        userName = users.getNameFromPeer(peer)
        city = self.cities[ident]
        container = proto.Container()
        if users.isAdmin(userName) or userName == city.mayor:
            container.enterCity = ident
        elif users.canUser(userName, ident, 'viewCity'):
            container.enterCity = ident
        else:
            container.response = "You lack permission to enter city."
        messenger.send("sendData", [peer, container])
    
    def updateTile(self, container, tile):
        t = container.updatedTiles.add()
        t.id = tile.id
        t.positionx = tile.coords[0]
        t.positiony = tile.coords[1]
        t.cityid = tile.cityid
