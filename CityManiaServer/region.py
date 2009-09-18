# -*- coding: utf-8 -*-
"""
region.py
Class for region, esentially the master model
"""
import engine
import protocol_pb2 as proto
import city

class Region(engine.Entity):
    def __init__(self):
        self.accept("loginRequest", self.login)

        self.name = "Region"
        self.cities = []
        self.password = ""
        self.players = {}
        self.terrainTextureDB = {}
        self.playersLoggedIn = {}

    def generate(self, hightMap=None, colorMap=None, cityMap=None, terrainTextureDB=None):
        """
        Generates region
        heightmap is a grayscale bitmap for heigh
        colormap is color bitmap for terrain texture
        terrainTextureDB is data on texture to use for color map
        Creates an unfounded city
        """
        # if no paramets are passed
        # default is two small, one large
        # one medium
        # two small
        x, y = 0, 0
        defaultCityMap = [[(1,0,0),(1,0,0),(0,0,1),(0,0,1),(0,0,1),(0,0,1)],
            [(0,1,0),(0,1,0),(0,0,1),(0,0,1),(0,0,1),(0,0,1)],
            [(0,1,0),(0,1,0),(0,0,1),(0,0,1),(0,0,1),(0,0,1)],
            [(1,0,0),(1,0,0),(0,0,1),(0,0,1),(0,0,1),(0,0,1)]]
        
        
        # Default Heighmap
        # Default Colormap
            
        # Convert Bitmap to test list
        # If failure resort to default
        cityMap = defaultCityMap
        cityCounter = 1
        
        # Skip contians the pixles to skip over for the non small city sizes
        skip = []
        for row in cityMap:
            for pixel in row:
                if (x,y) not in skip:
                    name = "City " + str(cityCounter)
                    if pixel[0] is 1:
                        #print "Small"
                        c = city.City(name=name, size=1)
                    elif pixel[1] is 1:
                        #print "Medium"
                        c = city.City(name=name, size=2)
                        skip += [(x+1,y),
                            (x,y+1),(x+1,y+1)]
                    elif pixel[2] is 1:
                        #print "Large"
                        c = city.City(name=name, size=4)
                        skip += [(x+1,y),(x+2,y),(x+3,y),
                            (x,y+1),(x+1,y+1),(x+2,y+1),(x+3,y+1),
                            (x,y+2),(x+1,y+2),(x+2,y+2),(x+3,y+2),
                            (x,y+3),(x+1,y+3),(x+2,y+3),(x+3,y+3)]
                    c.position = (x,y)
                    c.id = cityCounter
                    self.cities.append(c)
                    cityCounter += 1
                x += 1
            x = 0
            y += 1
        # 6 Total
        print "Cities:", self.cities
        print "Total Cities:", len(self.cities)
    
    def addPlayer(self, playerName, password):
        """
        Adds player to region
        """
        self.players[playerName] = password
    
    def loadCity(self, cityKey, playerName, password=""):
        """
        loads a city based on cityKey
        """
        self.cities(cityKey).login(playerName, password="")
    
    #def login(self, password, playerName, playerPassword):
    def login(self, peer, login):
        """
        Logs in a player to a region
        """
        container = proto.Container()
        container.loginResponse.type = 1
        if login.regionPassword != self.password:
            container.loginResponse.type = 0
            #container.loginResponse.message = "Region password incorrect"
        if login.name not in self.players:
            # If new player
            self.addPlayer(login.name, login.password)
        if self.players[login.name] != login.password:
            container.loginResponse.type = 0
            #container.loginResponse.message = "Player password incorrect"
            
        self.playersLoggedIn[peer] = login.name        
        messenger.post("sendData", [peer, container])
    
    def syncCities(self):
        """
        Syncronizes intercity effects on a regulat basis
        """
    
