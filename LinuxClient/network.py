# -*- coding: utf-8 -*-
"""
Network stuffs
"""

import protocol_pb2 as proto
from direct.showbase import DirectObject
from direct.stdpy import threading

# Networking
import socket

class ServerSocket(threading.Thread, DirectObject.DirectObject):
    """
    Connection to client
    """
    def __init__(self):
        """
        Overide to threading for client socket
        self.buffer:    Buffer string for incoming messages
        """
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.buffer = ""
        self.accept("exit", self.exit)
        self.accept("connect", self.connect)
        self.accept("sendData", self.send)
        threading.Thread.__init__(self)
    
    def connect(self, host, userName, userPassword):
        """
        connects with the server
        """
        self.s.connect((host, 52003))
        self.s.setblocking(0)
        #self.s.settimeout(1)
        self.peer = self.s.getpeername()
        print "Connection created with:", self.peer
        # Fire login data!
        container = proto.Container()
        container.login.name = userName
        container.login.password = userPassword
        container.login.regionPassword = ""
        self.send(container)
        self.start()
        
    def run(self):
        self.running = True
        while self.running:
            try:
                # Appends message to any existing buffer
                d = self.s.recv(4096)
                self.buffer += d
            except socket.timeout:
                # No message this time!
                continue
            except socket.error:
                # caused by main thread doing a socket.close on this socket
                # It is a race condition if this exception is raised or not.
                print "Race Condition!"
                raise
                return
            except:  # some error or connection reset by peer
                self.running = False
                break
                return
            if not len(d): # a disconnect (socket.close() by client)
                self.running = False
                break
                return
            # We now check for the end tag "[!]" and fire off the appropriate serialized string
            if "[!]" in self.buffer:
                # Only one string is brought out at a time
                # What ever partial or complete message is left is put back into the buffer for the next cycle
                # This is because I am lazy
                data, self.buffer = self.buffer.split("[!]", 1)
                self.processData(data)
            #print "Recieved Data:", data
            #print "From:", self.peer
            #messenger.post("gotData", data)
    
    def processData(self, data):
        """
        Processes network communication into engine events
        Some responses do not need any additional processing
        so we respond right away
        """
        container = proto.Container()
        container.ParseFromString(data)
        #print "Recieved Data:", container
        if container.HasField("chat"):
            if container.chat.to.startswith("#"):
                # Chat room
                print container.chat.to + " <" + container.chat.sender + "> " + container.chat.message
            else:
                # Direct PM
                print "<" + container.sender + "> " + container.message
        if container.HasField("serverState"):
            if container.serverState is 0:
                # Nothing running?! Lets get us some maps!
                container = proto.Container()
                container.requestMaps = 1
                self.send(container)
                # TODO: Notice of incoming files, or loading bar, or something
        # Because this is a repeted field we need to check for length as it will always be present
        elif len(container.maps):
            maps = {}
            import base64
            for map in container.maps:
                maps[map.name] = (base64.b64decode(map.heightmap))
            messenger.send("onGetMaps", [maps])
        elif container.HasField("loginResponse"):
            if container.loginResponse.type is 1:
                # Awesome, now we send a request to the server asking for the game state
                container = proto.Container()
                container.requestServerState = True
                self.send(container)
            else:
                # Got to think of an error message process for here
                pass
        elif container.HasField("gameState"):
            messenger.send("generateRegion", [container.gameState])
    
    def send(self, data):
        """
        sends data to client
        data needs to be a Protocol Buffer Container object
        """
        try:
            print "Sending Data:", data
            self.s.send(data.SerializeToString())
        except:
            print "Object is not a protocol buffer object or is missing a parameter."
    
    def exit(self):
        self.s.close()
        self.running = False


## Login Test
#print "Conducting Login Test"
#container = proto.Container()
#container.login.name = "croxis"
#container.login.password = ""
#container.login.regionPassword = ""
#connection.send(container)

## Wait for sucess login so we don't send other tests premature
#wait = True
#global wait
#while wait:
    #pass
#print "Login Successful"

## Chat test
#print "Conducting chat test"
#container = proto.Container()
#container.chat.message = "Hello world!"
#connection.send(container)