# -*- coding: utf-8 -*-
"""
region.py
Class for region, esentially the master model
"""
from server import Entity
class Region(Entity):
    def __init__(self):
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
    
    def login(self, password, playerName, playerPassword):
        """
        Logs in a player to a region
        """
        if password != self.password:
            #Send wrong password message
            return
        if playerName not in self.players:
            self.addPlayer(playerName, playerPassword)
        if self.players[playerName] != playerPassword:
            # Send player password missmatch
            return
        self.playersLoggedIn.append(playerName)
        # Send logged in message
    
    def syncCities(self):
        """
        Syncronizes intercity effects on a regulat basis
        """

