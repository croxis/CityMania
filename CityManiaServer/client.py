# -*- coding: utf-8 -*-
"""
Test client for network protocols
"""
import engine
import protocol_pb2 as proto
 
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
        self.s.settimeout(1)
        self.peer = self.s.getpeername()
        print "Connection created with:", self.peer
        self.accept("exit", self.exit)
        threading.Thread.__init__(self)
        
    def run(self):
        self.running = True
        while self.running:
            try:
                data = self.s.recv(4096)
            except socket.timeout:
                continue
            except socket.error:
                # caused by main thread doing a socket.close on this socket
                # It is a race condition if this exception is raised or not.
                print "Broken3"
                return
            except:  # some error or connection reset by peer
                print "Broken1"
                self.running = False
                break
                return
            if not len(data): # a disconnect (socket.close() by client)
                self.running = False
                break
                return
            self.processData(data)
            #print "Recieved Data:", data
            #print "From:", self.peer
            #messenger.post("gotData", data)
    
    def processData(self, data):
        """
        Processes network communication into test client report
        """
        container = proto.Container()
        container.ParseFromString(data)
        print "Recieved Data:", container
        # Overrides login wait
        if container.HasField("loginResponse"):
            if container.loginResponse.type is 1:
                global wait
                wait = False
                print "Stopping wait"
        if container.HasField("chat"):
            if container.chat.to.startswith("#"):
                # Chat room
                print container.chat.to + " <" + container.chat.sender + "> " + container.chat.message
            else:
                # Direct PM
                print "<" + container.sender + "> " + container.message
    
    def send(self, data):
        """
        sends data to client
        data needs to be a Protocol Buffer object
        """
        try:
            print "Sending Data:", data
            self.s.send(data.SerializeToString())
        except:
            print "Object is not a protocol buffer object or is missing a parameter."

    
    def exit(self):
        self.s.close()
        self.running = False


connection = ServerSocket()
connection.start()

# Login Test
print "Conducting Login Test"
container = proto.Container()
container.login.name = "croxis"
container.login.password = ""
container.login.regionPassword = ""
connection.send(container)

# Wait for sucess login so we don't send other tests premature
wait = True
global wait
while wait:
    pass
print "Login Successful"

# Chat test
print "Conducting chat test"
container = proto.Container()
container.chat.message = "Hello world!"
connection.send(container)

while 1:
    pass