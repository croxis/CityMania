# -*- coding: utf-8 -*-
'''
Simplified region class for client
'''
from direct.showbase import DirectObject
#from panda3d.core import PNMImage, StringStream
from pandac.PandaModules import PNMImage, StringStream
import sys
#sys.path.append("..")
#from common.tile import Tile
from tile import Tile

class Region(DirectObject.DirectObject):
    '''Stuff'''
    def __init__(self):
        self.tiles = []
        self.cities = {}
        self.accept('loadRegion', self.load)
        self.accept("updatedTiles", self.updateTiles)
        self.accept("newCity", self.newCity)
        self.accept("clickForCity", self.checkCity)
        
    def load(self, container, name="New Region"):
        '''Loads a new region, usually from connecting to a server
        Or starting a new or previously saved region.
        '''
        import base64
        self.heightmap = PNMImage()
        imageString = base64.b64decode(container.heightmap)
        self.heightmap.read(StringStream(imageString))
        self.region_size = (self.heightmap.getXSize()-1, self.heightmap.getYSize()-1)
        
        position = 0
        tileid = 0
        total_tiles = self.region_size[0] * self.region_size[1]
        ranges = []
        tiles = []
        
        for tile in container.tiles:
            tiles.append((tile.id, tile.cityid))
        for n in range(len(tiles)):
            try:
                ranges.append((tiles[n][0], tiles[n+1][0]-1, tiles[n][1]))
            except:
                ranges.append((tiles[n][0], total_tiles, tiles[n][1]))
        for r in ranges:
            for x in range(r[0], r[1]+1):
                #print "r0, r1, x", r[0], r[1], x
                self.tiles.append(Tile(tileid, r[2]))
                #print "Len", len(self.tiles)
                tileid += 1
        
        position = 0
        for x in range(self.region_size[0]):
            for y in range(self.region_size[1]):
                self.tiles[position].coords = (x,y)
                position += 1
        
        for city in container.cities:
            self.newCity(city)
        messenger.send("generateRegion", [self.heightmap, self.tiles, self.cities, container])
    
    def updateTiles(self, container):
        x = 0
        for tile in container:
            x += 1
            self.tiles[tile.id].cityid = tile.cityid
        print x, "tiles updated from server."
        messenger.send("updateRegion", [self.heightmap, self.tiles, self.cities])
    
    def newCity(self, city):
        self.cities[city.id] = {"name": city.name, "mayor": city.mayor, "funds": city.funds, "population": city.population}
    
    def checkCity(self, cell):
        '''Checks for city in given cell for region gui display'''
        if not cell: return
        tile = self.getTile(cell[0], cell[1])
        if tile.cityid:
            messenger.send("showRegionCityWindow", [self.cities[tile.cityid]])
        
    def getTile(self, x, y):
        '''Returns tile by coordinate. 
        Thankfully smart enough to find a way to not iterate
        '''
        value = y * self.region_size[0] + x
        return self.tiles[value]