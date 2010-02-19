# -*- coding: utf-8 -*-
"""
City Mania
version: You have to start somewhere right?
"""
import engine
import region

import sys
sys.path.append("..")
import common.protocol_pb2 as proto
import chat
import filesystem
from threading import Lock
import users
import simulator
from network import Network

# TODO: These values should be in seperate config file
HOST = ""
PORT = 52003

# TODO: Seperate files dude!

class GameState(engine.Entity):
    """
    Defines the game state (running, loaded, saving?).
    May end up being a finite state machine of some sort
    """
    def __init__(self):
        """
        Server states:
        0:  No region loaded.
        1:  Region loaded, but full simulation pause
        """
        self.serverState = 0
        self.accept("requestServerState", self.getServerState)
        self.accept("requestGameState", self.fullPause)
        self.accept("setServerState", self.setServerState)
    
    def getServerState(self, peer):
        container = proto.Container()
        container.serverState = self.serverState
        messenger.send("sendData", [peer, container])
    
    def setServerState(self, state):
        self.serverState = state
        print "Server set to state", state
    
    def fullPause(self, var1=None):
        # If serverstate is 0 then can't change it to 1!
        if self.serverState:
            self.serverState = 1
    

class CommandProcessor(engine.Entity):
    """
    This converts incomming communication into the server message system
    Locking system provided so the server can halt the queue mid operation
    TODO: Add more refined locking for a per city basis (so one city update wont block the others)
    TODO: Add user account management/command authorization here
    """
    def __init__(self):
        self.accept("lockCommandQueue", self.lockQueue)
        self.accept("unlockCommandQueue", self.unlockQueue)
        self.accept("gotData", self.queue)
        self.accept("logout", self.logout)
        self.accept("tick", self.step)
        self.commandQueue = []
        self.lock = Lock()
        # Simple list to make sure people who are here should be here
        self.password = ""
    
    def lockQueue(self):
        #self.lock.aquire()
        pass
    
    def unlockQueue(self):
        #self.lock.release()
        pass
    
    def queue(self, peer, data):
        self.commandQueue.append((peer, data))
    
    def step(self):
        #print "Step1"
        if self.commandQueue:
            #self.lock.acquire()
            peer, data = self.commandQueue.pop()
            self.processData(peer, data)
            #self.lock.release()
    
    def processData(self, peer, data):
        """
        processes serialized network event object into internal message system
        """
        container = proto.Container()
        container.ParseFromString(data)
        logger.debug("Data from: %s\nData: %s" %(peer, container))
        # Parsing chain!
        # Great care will need to be taken on when to use if, else, and elif
        # If the profile for this process takes too long
        if container.HasField("login"):
            self.login(peer, container.login)
        # If the player is not logged in we will not process any other message
        if peer not in users.peers:
            print "Unauthorized message from", peer, ". Skipping."
            return
        if container.HasField("chat"):
            messenger.send("onChat", [peer, container.chat])
        if container.HasField("requestServerState"):
            messenger.send("requestServerState", [peer])
        elif container.HasField("requestMaps"):
            messenger.send("requestMaps", [peer])
        elif container.HasField("mapRequest"):
            # Make sure user is admin!
            name = users.getNameFromPeer(peer)
            if users.isAdmin(name):
                messenger.send("mapRequest", [container.mapRequest])
        elif container.HasField("newCityRequest"):
            messenger.send("newCityRequest", [peer, container.newCityRequest])
        elif container.HasField("requestGameState"):
            if not container.requestGameState:
                messenger.send("sendGameState", [peer])
        elif container.HasField("requestUnfoundCity"):
            messenger.send("requestUnfoundCity", [peer, container.requestUnfoundCity])
        elif container.HasField("requestEnterCity"):
            messenger.send("requestEnterCity", [peer, container.requestEnterCity])
    
    def login(self, peer, login):
        """
        Logs in player to the server
        """
        self.lock.acquire()
        container = proto.Container()
        container.loginResponse.type = 1
        if login.regionPassword != self.password:
            container.loginResponse.type = 0
            container.loginResponse.message = "Region password incorrect"
        if login.name not in users.userdb:
            users.addUser(login.name, login.password)
        loginType = users.login(login.name, login.password, peer)
        if not loginType:
            container.loginResponse.type = 0
            container.loginResponse.message = "Player password incorrect"
        if container.loginResponse.type:
            container.loginResponse.usertype = users.getType(login.name)
            container.loginResponse.username = login.name
            messenger.send("loggedIn", [peer, login.name])
            logger.info("Logged in: %s %s" %(login.name, peer) )
        messenger.send("sendData", [peer, container])
        self.lock.release()

    def logout(self, peer):
        self.lock.acquire()
        userName = users.getNameFromPeer(peer)
        # Temporary fix.
        if userName:
            users.logout(userName)
            logger.info("User %s %s exiting." %(userName, peer))
        self.lock.release()


# We initialize the CityMania engine
import __builtin__
#__builtin__.messenger = engine.EventManager()
commandProcessor = CommandProcessor()

# Set up logging
import logging
logger = logging.getLogger('server')
logger.setLevel(logging.DEBUG)
stream = logging.StreamHandler()
formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
stream.setFormatter(formatter)
logger.addHandler(stream)
logger.info('Logging stream handler added.')

def main():
    vfs = filesystem.FileSystem()
    # Finish setting up logger
    logPath = vfs.logs + 'server.log'
    logFile = logging.FileHandler(logPath)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logFile.setFormatter(formatter)
    logger.addHandler(logFile)
    logger.info("Logging file handler added. Logging to %s" % logPath)
    
    network = Network(HOST, PORT)
    chatServer = chat.ChatServer()
    state = GameState()
    reg = region.Region()
    
    try:
        messenger.start()
    except Exception, e:
        logger.exception(e)

if __name__ == "__main__":
    main()
