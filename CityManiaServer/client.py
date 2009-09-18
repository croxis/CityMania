# -*- coding: utf-8 -*-
"""
Test client for network protocols
"""
import engine
 
# Networking
import threading, socket

class ServerSocket(engine.Entity, threading.Thread):
    """
    Connection to client
    """
    def __init__(self):
        """
        Overide to threading for client socket
        """
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect(("", 52003))
        self.peer = self.s.getpeername()
        print "Connection created with:", self.peer
        self.accept("exit", self.exit)
        threading.Thread.__init__(self)
        
    def run(self):
        self.running = True
        while self.running:
            print "Thread Pulse", self.peer
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
            print "Recieved Data:", data
            print "From:", self.peer
            messenger.post("gotData", data)
    
    def processData(self, data):
        """
        Processes network communication into engine event
        """
        print "Recieved Data:", data
        print "From:", self.peer
    
    def send(self, data):
        """
        sends data to client
        data needs to be a Protocol Buffer object
        """
        try:
            print "Sending Data"
            self.s.send(data.SerializeToString())
        except:
            print "Object is not a protocol buffer object or is missing a parameter."

    
    def exit(self):
        self.s.close()
        self.running = False


connection = ServerSocket()
connection.start()
import protocol_pb2 as proto
container = proto.Container()
container.login.name = "croxis"
container.login.password = ""
container.login.regionPassword = ""
connection.send(container)
while 1:
    pass