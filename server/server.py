# -*- coding: utf-8 -*-
"""
City Mania
version: You have to start somewhere right?
"""
import engine
import region
import protocol_pb2 as proto
import chat
import filesystem
import time
import users
import simulator

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
    
    def login(self, peer, login):
        """
        Logs in player to the server
        """
        container = proto.Container()
        container.loginResponse.type = 1
        if login.regionPassword != self.password:
            container.loginResponse.type = 0
            container.loginResponse.message = "Region password incorrect"
        if not users.login(login.name, login.password, peer):
            users.addUser(login.name, login.password)
        if users.login(login.name, login.password, peer) is 1:
            container.loginResponse.type = 0
            container.loginResponse.message = "Player password incorrect"
        if container.loginResponse.type:
            container.loginResponse.usertype = users.getType(login.name)
            messenger.send("loggedIn", [peer, login.name])
            self.peers.append(peer)
        messenger.send("sendData", [peer, container])

    def logout(self, peer):
        index = self.peers.index(peer)
        del self.peers[index]
        user_name = users.getNameFromPeer(peer)
        users.logout(user_name)


# Networking
import threading, socket

class ClientSocket(engine.Entity, threading.Thread):
    """
    Connection to client
    """
    def __init__(self, clientsock):
        """
        Overide to threading for client socket
        """
        self.s = clientsock
        self.peer = self.s.getpeername()
        print "Connection created with:", self.peer
        self.accept("exit", self.exit)
        threading.Thread.__init__(self)
        
    def run(self):
        self.running = True
        while self.running:
            #print "Thread Pulse", self.peer
            try:
                data = self.s.recv(4096)
            except socket.timeout:
                continue
            except socket.error:
                # caused by main thread doing a socket.close on this socket
                # It is a race condition if this exception is raised or not.
                self.running = False
                self.exit()
                break
            except:  # some error or connection reset by peer
                self.running = False
                self.exit()
                break
            if not len(data): # a disconnect (socket.close() by client)
                self.running = False
                self.exit()
                break
            print "Recieved Data from:", self.peer
            messenger.send("gotData", [self.peer, data])
            time.sleep(0.1)
        #messenger.send("loggout", [self.peer])
    
    def send(self, data):
        """
        sends data to client
        data needs to be a Protocol Buffer object
        the citymania end tag "[!]" is added to signify the end of the message
        This way the client can accept larger file transfers
        """
        #print data.SerializeToString()+"[!]"
        try:
            print "Sending:", str(data)[0:100]
            self.s.sendall(data.SerializeToString()+"[!]")
        except:
            print "Object is not a protocol buffer object:", data[0:100]
    
    def exit(self):
        self.s.close()
        self.running = False
        messenger.send("loggout", [self.peer])
        print "Peer", self.peer, "attempting to exit memory"


class Network(engine.Entity, threading.Thread):
    """
    Network interface
    """
    def __init__(self):
        global chatQueue
        threading.Thread.__init__(self)
        #self.accept("tick", self.listen)
        self.running = True
        self.accept("exit", self.exit)
        self.accept("broadcastData", self.broadcast)
        self.accept("sendData", self.send)
        self.accept("logout", self.logout)
        self.clients = {}
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((HOST, PORT))
        self.s.listen(3) 
        self.daemon = True
        self.lock = threading.Lock()
        self.start()
    
    def run(self):
        while self.running:
            self.listen()
            time.sleep(0.1)
    
    def listen(self):
        """
        Listens for new connection and spawn processes
        """
        try:
            clientsock, clientaddr = self.s.accept()
            clientsock.settimeout(1) 
            t = ClientSocket(clientsock)
            self.lock.acquire()
            self.clients[t.peer] = t
            self.lock.release()
            t.daemon = True
            t.start()
        except:
            print "Main socket error"    
        print "Clients:", self.clients
    
    def broadcast(self, data):
        """
        Broadcasts data to all clients 
        """
        self.lock.acquire()
        for peer in self.clients:
            self.send(peer, data)
        self.lock.release()
    
    def send(self, peer, data):
        """
        Sends data to a specific client
        """
        print "Peer:", peer
        self.clients[peer].send(data)
    
    def exit(self):
        """
        Server is shutting down, so let us tidy up
        """
        #self.ignore("tick")
        self.running = False
        self.s.close()
    
    def logout(self, peer):
        self.lock.aquire()
        del self.clients[peer]
        self.lock.release()
    

# We initialize the CityMania engine
import __builtin__
#__builtin__.messenger = engine.EventManager()
commandProcessor = CommandProcessor()

def main():
    network = Network()
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






