# -*- coding: utf-8 -*-
"""
Network stuffs for the panda client.
"""

import sys
sys.path.append("../..")
import CityMania.common.protocol_pb2 as proto
#import protocol_pb2 as proto
from direct.showbase import DirectObject
from direct.stdpy import threading

from pandac.PandaModules import QueuedConnectionManager, QueuedConnectionReader, ConnectionWriter, QueuedConnectionListener, Thread
from direct.task import Task

# Networking
import socket, select

class ServerSocket(DirectObject.DirectObject):
    """
    Connection to client
    """
    def __init__(self):
        """
        Overide to threading for client socket
        self.buffer:    Buffer string for incoming messages
        """
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sendBuffer = []        
        self.buffer = ""
        self.accept("exit", self.exit)
        self.accept("connect", self.connect)
        self.accept("sendData", self.send)
    
    def connect(self, host, userName, userPassword):
        """
        connects with the server
        """
        self.s.connect((host, 52003))
        self.s.setblocking(0)
        ##self.s.settimeout(1)
        self.peer = self.s.getpeername()
        
        container = proto.Container()
        container.login.name = userName
        container.login.password = userPassword
        container.login.regionPassword = ""
        self.send(container)
        
        # These are for using this class in non threaded mode.
        taskMgr.add(self.getData,"Poll the connection listener",-39)
        taskMgr.add(self.sendData,"Poll the connection sender",-40)
        taskMgr.add(self.processBuffer,"Poll the buffer manager",-41)
    
    def getData(self, taskData):
        """
        This is a function for recieving data in a nonthreaded class
        """
        inputready,outputready,exceptready = select.select([self.s], [self.s] ,[]) 
        if inputready:
            d = self.s.recv(4096)
            if d:
                self.buffer += d
        return Task.cont
    
    def sendData(self, taskData):
        """
        This is a function for sending data in a nonthreaded class
        """
        inputready,outputready,exceptready = select.select([self.s], [self.s] ,[]) 
        # Check if we have any data to send
        if self.sendBuffer and outputready:
            try:
                data = self.sendBuffer.pop()
                self.s.sendall(data)
            except:
                raise
        return Task.cont
    
    def processBuffer(self, taskData):
        """
        Processess anything in the buffer in the nonthreaded mode
        """
        if "[!]" in self.buffer:
            # Only one string is brought out at a time
            # What ever partial or complete message is left is put back into the buffer for the next cycle
            # This is because I am lazy
            data, self.buffer = self.buffer.split("[!]", 1)
            self.processData(data)
        return Task.cont
    
    def run(self):
        self.running = True
        while self.running:
            self.considerYield()
            inputready,outputready,exceptready = select.select([self.s], [self.s] ,[]) 
            # Check if we have any data to send
            if self.sendBuffer and outputready:
                try:
                    data = self.sendBuffer.pop()
                    self.s.sendall(data)
                except:
                    raise
            if inputready:
                d = self.s.recv(4096)
                print "d:", d
                if d:
                    self.buffer += d
            # We now check for the end tag "[!]" and fire off the appropriate serialized string
            if "[!]" in self.buffer:
                # Only one string is brought out at a time
                # What ever partial or complete message is left is put back into the buffer for the next cycle
                # This is because I am lazy
                data, self.buffer = self.buffer.split("[!]", 1)
                self.processData(data)
    
    def processData(self, data):
        """
        Processes network communication into engine events
        Some responses do not need any additional processing
        so we respond right away
        """
        container = proto.Container()
        container.ParseFromString(data)
        #print "Recieved Data:", str(container)[0:100]
        if container.HasField("chat"):
            if container.chat.to.startswith("#"):
                # Chat room
                print container.chat.to + " <" + container.chat.sender + "> " + container.chat.message
            else:
                # Direct PM
                print "<" + container.sender + "> " + container.message
        # Chunk Region City management #
        if container.HasField("newCityResponse"):
            messenger.send("newCityResponse", [container.newCityResponse])
        if container.HasField("newCity"):
            messenger.send("newCity", [container.newCity])
        elif container.HasField("unfoundCity"):
            messenger.send("unfoundCity", [container.unfoundCity])
            # End Chunk Region City management #
        
        ## THE POSITION OF THIS IS VERY IMPORTANT ##
        if len(container.updatedTiles):
            messenger.send("updatedTiles", [container.updatedTiles])
        ## ##
        
        if container.HasField("serverState"):
            if container.serverState is 0:
                # Nothing running?! Lets get us some maps!
                container = proto.Container()
                container.requestMaps = 1
                # TODO: Notice of incoming files, or loading bar, or something
            elif container.serverState is 1:
                # A map is loaded so we will just request the game state.
                container = proto.Container()
                container.requestGameState = 0
            self.send(container)
        # Because this is a repeated field we need to check for length as it will always be present
        elif len(container.maps):
            maps = {}
            import base64
            for map in container.maps:
                maps[map.name] = (base64.b64decode(map.heightmap))
            messenger.send("onGetMaps", [maps])
        elif container.HasField("loginResponse"):
            if container.loginResponse.type is 1:
                # Awesome, Server returns an int with our user status. We will use this to set up the UI for extra goodies.
                messenger.send("setSelfAccess", [container.loginResponse.usertype, container.loginResponse.username])
                #now we send a request to the server asking for the game state
                container = proto.Container()
                container.requestServerState = True
                self.send(container)
            else:
                # Got to think of an error message process for here
                messenger.send("loginError", container.loginResponse.message)
        elif container.HasField("gameState"):
            messenger.send("loadRegion", [container.gameState])
    
    def send(self, data):
        """
        Adds message to the internal message database
        data needs to be a Protocol Buffer Container object
        """
        try:
            self.sendBuffer.append(data.SerializeToString())
        except:
            print "There was an error serializing the protocol:", str(data)[0:100]
    
    def exit(self):
        print "Closing up shop"
        self.s.close()
        self.running = False
