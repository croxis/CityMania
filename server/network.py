'''Network related code.'''
import threading, socket
import logging
import engine
import time

logger = logging.getLogger('server.network')

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
        logger.info("Connection created with: %(peer)s"  %{'peer': self.peer})
        self.accept("exit", self.exit)
        self.sendCache = []
        self.sendLock = threading.Lock()
        threading.Thread.__init__(self)
        
    def run(self):
        self.running = True
        while self.running:
            try:
                data = self.s.recv(4096)
                messenger.send("gotData", [self.peer, data])
            except socket.timeout:
                continue
            # Normally we'll inform the client why it is being disconnected
            # But if the socket is foobar, well, duh.
            except:  # some error or connection reset by peer
                messenger.send('logout', [self.peer])
            if not len(data): # a disconnect (socket.close() by client)
                messenger.send('logout', [self.peer])
            time.sleep(0.1)
    
    def send(self, data):
        """
        sends data to client
        data needs to be a Protocol Buffer object
        the citymania end tag "[!]" is added to signify the end of the message
        This way the client can accept larger file transfers
        """
        #print data.SerializeToString()+"[!]"
        self.sendLock.acquire()
        try:
            logger.debug("Sending %s: %s" %(self.peer, data))
            self.s.sendall(data.SerializeToString()+"[!]")
        except:
            logger.warning("Object is not a protocol buffer object: %s" %data)
        self.sendLock.release()
        
    def exit(self):
        logger.info("Closing thread for %(peer)s" %{'peer': self.peer})
        self.s.close()
        self.running = False


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
        if peer not in self.clients:
            logger.critical("%s not in client list! Attempting to send: %s" %(peer, data))
            return
        self.clients[peer].send(data)
    
    def exit(self):
        """
        Server is shutting down, so let us tidy up
        """
        #self.ignore("tick")
        container = proto.Container()
        container.disconnect = "Server is shutting down."
        self.broadcast(container)
        for peer, client in self.clients.items():
            client.exit()
        self.clients = {}
        self.running = False
        self.s.close()
    
    def logout(self, peer):
        self.lock.acquire()
        if peer in self.clients:
            self.clients[peer].exit()
            del self.clients[peer]
            logger.info("Logged out (%s, %s)" %peer)
        else:
            logger.info("%s is not in peer list: %s" %(peer, self.clients))
        self.lock.release()
