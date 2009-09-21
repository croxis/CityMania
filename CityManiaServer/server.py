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
    """
    def __init__(self):
        self.accept("lockCommandQueue", self.lockQueue)
        self.accept("unlockCommandQueue", self.unlockQueue)
        self.accept("gotData", self.queue)
        self.accept("tick", self.step)
        self.commandQueue = []
        self.lock = False
    
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
            print "Login Request"
            messenger.post("loginRequest", [peer, container.login])
        if container.HasField("chat"):
            messenger.post("chat", [peer, container.chat])


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


class IRCClientSocket(ClientSocket):
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
            print "Recieved Data from:", self.peer
            messenger.post("gotIRCData", [self.peer, data])
         
        def send(self, data):
            """
            sends data to client
            """
            try:
                self.s.send(data)
            except:
                print "Oops"


class Network(engine.Entity, threading.Thread):
    """
    Network interface
    """
    def __init__(self):
        global chatQueue
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
        
        threading.Thread.__init__(self)
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
    

# We initialize the CityMania engine
import __builtin__
#__builtin__.messenger = engine.EventManager()
commandProcessor = CommandProcessor()

def main():
    network = Network()
    reg = region.Region()
    reg.generate()
    messenger.start()

if __name__ == "__main__":
    main()