# -*- coding: utf-8 -*-
"""
region.py
Class for region, esentially the master model
"""
import engine
class Region(engine.Entity):
    def __init__(self):
        self.accept("loginRequest", self.login)

        self.name = "Region"
        self.cities = []
        self.password = ""
        self.players = {}
        self.terrainTextureDB = {}
        self.playersLoggedIn = []

    def generateRegion(self, hightMap=None, colorMap=None, terrainTextureDB=None):
        """
        Generates region
        heightmap is a grayscale bitmap for heigh
        colormap is color bitmap for terrain texture
        terrainTextureDB is data on texture to use for color map
        Creates an unfounded city
        """
    
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
    def login(self, login):
        """
        Logs in a player to a region
        """
        if login.regionPassword != self.password:
            #Send wrong password message
            return
        if login.name not in self.players:
            self.addPlayer(login.name, login.password)
        if self.players[login.name] != login.password:
            # Send player password missmatch
            return
        self.playersLoggedIn.append(login.name)
        # Send logged in message
        print "Player logged in"
    
    def syncCities(self):
        """
        Syncronizes intercity effects on a regulat basis
        """

