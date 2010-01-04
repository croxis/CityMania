# -*- coding: utf-8 -*-
"""
Network stuffs
"""

import protocol_pb2 as proto
from direct.showbase import DirectObject
from direct.stdpy import threading

from pandac.PandaModules import QueuedConnectionManager, QueuedConnectionReader, ConnectionWriter, QueuedConnectionListener, Thread
from direct.task import Task

# Networking
import socket, select

#class ServerSocket(threading.Thread, DirectObject.DirectObject):
#class ServerSocket(Thread, DirectObject.DirectObject):
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
        #self.cManager = QueuedConnectionManager()
        #self.cReader = QueuedConnectionReader(self.cManager,0)
        #self.cReader.setRawMode(True)
        #self.cWriter = ConnectionWriter(self.cManager,0)
        #self.cWriter.setRawMode(True)
        #self.cListener = QueuedConnectionListener(self.cManager, 0)
        #self.connection = None
        
        self.buffer = ""
        self.accept("exit", self.exit)
        self.accept("connect", self.connect)
        self.accept("sendData", self.send)
        #threading.Thread.__init__(self)
        #Thread.__init__(self)
    
    def connect(self, host, userName, userPassword):
        """
        connects with the server
        """
        self.s.connect((host, 52003))
        self.s.setblocking(0)
        ##self.s.settimeout(1)
        self.peer = self.s.getpeername()
        #print "Connection created with:", self.peer
        # Fire login data!
        #self.myConnection=  self.cManager.openTCPClientConnection(host,52003,3000)
        #self.cReader.addConnection(self.myConnection)
        
        container = proto.Container()
        container.login.name = userName
        container.login.password = userPassword
        container.login.regionPassword = ""
        self.send(container)
        #self.start()
        #self.run()
        
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
        import time
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
            #d = ""
            #print self.cReader.getData(d)
            #print "Data?", self.cReader.dataAvailable()
            #time.sleep(1)
            #if self.cReader.dataAvailable():
            #    v = self.cReader.getData(d)
            #    print "I gots:", v, d
            #    self.buffer += d
            #try:
                ## Appends message to any existing buffer
                ##d = self.s.recv(4096)
                #d = ""
                #if self.cReader.getData(d):
                    #self.buffer += d
            #except socket.timeout:
                ## No message this time!
                #print "Yo?"
                #continue
            #except socket.error:
                ## caused by main thread doing a socket.close on this socket
                ## It is a race condition if this exception is raised or not.
                #print "Race Condition!"
                #raise
                #return
            #except:  # some error or connection reset by peer
                #self.running = False
                #break
                #return
            #if not len(d): # a disconnect (socket.close() by client)
            #    self.running = False
            #    break
            #    return
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
        print "Recieved Data:", str(container)[0:100]
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