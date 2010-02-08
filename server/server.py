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
        self.lock = False
        # Simple list to make sure people who are here should be here
        self.peers =[]
        self.password = ""
    
    def lockQueue(self):
        self.lock = True
    
    def unlockQueue(self):
        self.lock = False
    
    def queue(self, peer, data):
        self.commandQueue.append((peer, data))
    
    def step(self):
        #print "Step1"
        if not self.lock and self.commandQueue:
            peer, data = self.commandQueue.pop()
            self.processData(peer, data)
    
    def processData(self, peer, data):
        """
        processes serialized network event object into internal message system
        """
        container = proto.Container()
        container.ParseFromString(data)
        print "Data:", str(container)[0:100]
        # Parsing chain!
        # Great care will need to be taken on when to use if, else, and elif
        # If the profile for this process takes too long
        if container.HasField("login"):
            self.login(peer, container.login)
        # If the player is not logged in we will not process any other message
        if peer not in self.peers:
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
                messenger.send("sendGameState")
        elif container.HasField("requestUnfoundCity"):
            messenger.send("requestUnfoundCity", [peer, container.requestUnfoundCity])
    
    def login(self, peer, login):
        """
        Logs in player to the server
        """
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
            print "Login incorrect"
        if container.loginResponse.type:
            container.loginResponse.usertype = users.getType(login.name)
            container.loginResponse.username = login.name
            messenger.send("loggedIn", [peer, login.name])
            self.peers.append(peer)
            print peer, "logged in."
            print self.peers
        messenger.send("sendData", [peer, container])

    def logout(self, peer):
        print peer, "logging out."
        print self.peers
        user_name = users.getNameFromPeer(peer)
        print "User", user_name, "exiting."
        # Temporary fix.
        if user_name:
            users.logout(user_name)
        index = self.peers.index(peer)
        del self.peers[index]
        print peer, "logged out."
        print self.peers
    

# We initialize the CityMania engine
import __builtin__
#__builtin__.messenger = engine.EventManager()
commandProcessor = CommandProcessor()

def main():
    network = Network(HOST, PORT)
    vfs = filesystem.FileSystem()
    chatServer = chat.ChatServer()
    state = GameState()
    reg = region.Region()
    messenger.start()

if __name__ == "__main__":
    main()
    import cProfile
    cProfile.run('main()', 'profile.txt')
    import pstats
    p = pstats.Stats('profile.txt')
    #p.sort_stats('name').print_stats()
    #p.sort_stats('cumulative').print_stats(10)
    p.sort_stats('time').print_stats(10)
    #p.sort_stats('file').print_stats('__init__')
    #p.dump_stats("stats.txt")






