# -*- coding: utf-8 -*-
"""
City Mania
version: You have to start somewhere right?
"""
import engine
import region
import protocol_pb2 as proto
import chat

# TODO: These values should be in seperate config file
HOST = ""
PORT = 52003

# TODO: Seperate files dude!       
                
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
        self.accept("tick", self.step)
        self.commandQueue = []
        self.lock = False
        
        self.password = ""
        self.players = {}
        self.playersLoggedIn = {}
    
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
        print "Data:", container
        # Parsing chain!
        # Great care will need to be taken on when to use if, else, and elif
        # If the profile for this process takes too long
        if container.HasField("login"):
            #print "Login Request"
            #messenger.post("loginRequest", [peer, container.login])
            self.login(peer, container.login)
        # If the player is not logged in we will not process any other message
        if peer not in self.playersLoggedIn:
            print "Unauthorized message from", peer, ". Skipping."
            return
        if container.HasField("chat"):
            messenger.post("onChat", [peer, container.chat])
    
    def addPlayer(self, playerName, password):
        """
        Adds player to region
        """
        self.players[playerName] = password
    
    def login(self, peer, login):
        """
        Logs in player to the server
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
        messenger.post("loggedIn", [peer, login.name])


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
                return
            except:  # some error or connection reset by peer
                break
            if not len(data): # a disconnect (socket.close() by client)
                break
            #self.processData(data)
            print "Recieved Data from:", self.peer
            messenger.post("gotData", [self.peer, data])
    
    def send(self, data):
        """
        sends data to client
        data needs to be a Protocol Buffer object
        """
        try:
            self.s.send(data.SerializeToString())
        except:
            print "Object is not a protocol buffer object"
    
    def exit(self):
        self.s.close()
        self.running = False


class ClientSocketIRC(ClientSocket):
    """
    Connection to an IRC client
    """        
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
                return
            except:  # some error or connection reset by peer
                break
            if not len(data): # a disconnect (socket.close() by client)
                break
                #self.processData(data)
            print "Recieved IRC Data from:", self.peer
            # As TCP is a stream we are going to break apart any combined commands
            splitData = data.split("\r\n")
            #print "spitData:", splitData
            for d in splitData:
                if d:
                    messenger.post("gotIRCData", [self.peer, d])
         
    def send(self, data):
        """
        sends data to client
        """
        try:
            print "Sending Data"
            self.s.send(data)
        except:
            print "Oops"


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
        self.clients = {}
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((HOST, PORT))
        self.s.listen(3) 
        self.daemon = True
        self.start()
    
    def run(self):
        while self.running:
            self.listen()
    
    def listen(self):
        """
        Listens for new connection and spawn processes
        """
        try:
            clientsock, clientaddr = self.s.accept()
            clientsock.settimeout(1) 
            t = ClientSocket(clientsock)
            self.clients[t.peer] = t
            t.daemon = True
            t.start()
        except:
            print "Main socket error"    
        
    
    def broadcast(self, data):
        """
        Broadcasts data to all clients 
        """
        # I have a feelling this wont work
        print "Broadcasting Data"
        for peer in self.clients:
            self.send(peer, data)
    
    def send(self, peer, data):
        """
        Sends data to a specific client
        """
        self.clients[peer].send(data)
    
    def exit(self):
        """
        Server is shutting down, so let us tidy up
        """
        #self.ignore("tick")
        self.running = False
        self.s.close()

class NetworkIRC(Network):
    """
    Network interface for IRC clients
    """
    def __init__(self, host="", port=6667):
        global chatQueue
        #self.accept("tick", self.listen)
        threading.Thread.__init__(self)
        self.running = True
        self.accept("exit", self.exit)
        self.accept("broadcastIRCData", self.broadcast)
        self.accept("sendIRCData", self.send)
        self.clients = {}
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((host, port))
        self.s.listen(3) 
        self.daemon = True
        self.start()
                
    def listen(self):
        """
        Listens for new connection and spawn processes
        """
        try:
            clientsock, clientaddr = self.s.accept()
            clientsock.settimeout(1) 
            t = ClientSocketIRC(clientsock)
            self.clients[t.peer] = t
            t.daemon = True
            t.start()
        except:
            print "Main socket error"
   

# We initialize the CityMania engine
import __builtin__
#__builtin__.messenger = engine.EventManager()
commandProcessor = CommandProcessor()

def main():
    irc = True
    network = Network()
    if irc:
        networkirc = NetworkIRC()
    chatServer = chat.ChatServer()
    reg = region.Region()
    reg.generate()
    messenger.start()

if __name__ == "__main__":
    main()