'''Network related code.'''
import threading, socket
import engine
import time

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
        messenger.send("logout", [self.peer])
        print "Peer", self.peer, "attempting to exit memory"


class Network(engine.Entity, threading.Thread):
    """
    Network interface
    """
    def __init__(self, host, port):
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
        self.s.bind((host, port))
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
        print "Braodcasting to clients:", self.clients
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
        self.lock.acquire()
        del self.clients[peer]
        self.lock.release()
