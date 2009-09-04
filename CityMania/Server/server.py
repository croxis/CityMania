# -*- coding: utf-8 -*-
"""
City Mania
version: You have to start somewhere right?
"""

# TODO: These values should be in seperate config file
HOST = ""
PORT = 52003

# TODO: Seperate files dude!

class Entity(object):
    """
    Basic Entity which almost everything should inherint from.  Currently provides integration to the event engine.
    """
    def __init__(self):
        pass
    
    def accept(self, event, method, extraArgs=[]):
        return messenger.accept(event, method, extraArgs, self)         



class EventManager(Entity):
    def __init__ (self):
        """
        self.listeners: {event: {object1: [method, [arguments]], object2: [method2, [arguments]]}, event2... }
        self.eventQueueLock:  If the simulation is busy it locks the eventQueue??
        I *think* this is thread safe as is as thread's arn't directly writing to it.
        We'll find out :P
        """
        self.listeners = {}
        self.eventQueue = []
        self.eventQueueLock = False
        self.running = False
        
        self.accept("lockEventQueue", self.lock, [], self)
        self.accept("unlockEventQueue", self.unlock, [], self)  
        
    def accept(self, event, method, extraArgs, object):
        """
        Adds a new listener into the database.  This is stored by event to reduce chattyness
        Overides Entity.accept(), not best design
        """
        if event not in self.listeners:
            self.listeners[event] = {}
        self.listeners[event][object] = [method, extraArgs]
    
    def post(self, event, extraArgs=[]):
        """
        Events are posted into self.eventQueue
        """
        self.eventQueue.append((event, extraArgs))
    
    def start(self):
        self.running = True
        while self.running:
            try:
                self.step()
            except KeyboardInterrupt:
                messenger.post("exit")
                self.stop()
                
    def stop(self):
        self.running = False
        
    def step(self):
        self.send()
            
    def send(self):
        """
        Notify all listening object of an event
        We also pump tick events here
        TODO: Add error checking
        """
        if not self.eventQueueLock and self.eventQueue:
            event, extraArgs = self.eventQueue.pop()
            objects = self.listeners[event]
            for object in objects:
                method, args = objects[object]
                method(extraArgs)
        objects = self.listeners["tick"]
        for object in objects:
            method, args = objects[object]
            method()
                
    def lock(self):
        """
        Lock self.eventQueue
        """
        self.eventQueueLock = True
    
    def unlock(self):
        """
        Unlock self.eventQueue
        """
        self.eventQueueLock = False


# Networking
import threading, socket

class Client(Entity, threading.Thread):
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
            print "Pulse"
            try:
                data = clientsock.recv(4096)
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
            self.processData(data)               
    
    def processData(self, data):
        """
        Processes network communication into engine events
        """
        print "Recieved Data:", data
        print "From:", self.peer
    
    def send(self, data):
        """
        sends data to client
        """
        self.s.send(data)
    
    def exit(self):
        self.s.close()
        self.running = False


class Network(Entity):
    """
    Network interface
    """
    def __init__(self):
        global chatQueue
        self.accept("tick", self.listen)
        self.accept("exit", self.exit)
        self.accept("broadcastData", self.broadcast)
        self.clients = []
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((HOST, PORT))
        self.s.listen(3)
    
    def listen(self):
        """
        Listens for new connection and spawn processes
        """
        try:
            clientsock, clientaddr = self.s.accept()
            clientsock.settimeout(1)
            t = Client(clientsock)
            self.clients.append(t)
            t.run()
        except:
            pass
    
    def broadcast(self, data):
        """
        Broadcasts data to all clients 
        """
        # I have a feelling this wont work
        for client in self.clients:
            client.send(data)
        
    
    def exit(self):
        """
        Server is shutting down, so let us tidy up
        """
        self.s.close()
    

# We initialize the CityMania engine
messenger = EventManager()

def main():
    network = Network()
    messenger.start()

if __name__ == "__main__":
    main()