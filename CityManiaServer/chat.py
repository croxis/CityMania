# -*- coding: utf-8 -*-
"""
Chat server engine and interpriter
TODO: impliment IRC protocol
"""
import engine
import protocol_pb2 as proto

class ChatServer(engine.Entity):
    """
    Chat server implimentation
    There are plans to intigrate a minimal IRC capacity into this
    self.users = {username: peer}
    """
    def __init__(self):
        """
        """
        self.accept("gotIRCData", self.processIRCChat)
        self.accept("onChat", self.processChat)
        self.accept("loggedIn", self.addUser)
        self.users = {}
        # channels = {channel1: [user1, user2]}
        self.channels = {"#region": []}
        print "Chat server initialized"
    
    def processChat(self, peer, chat):
        """
        Peeks into the chat container for what to do
        The chat container is then resent, intact,
        to the message target
        """
        if not chat.HasField("to"):
            chat.to = "#region"
        # We inject who the chat is from, so we know who is talking
        for username, value in self.users.items():
            if value == peer:
                chat.sender = username
        if chat.to.startswith("#") and chat.to in self.channels:
            for user in self.users:
                peerTo = self.users[user]
                self.sendChat(peerTo, chat)
        elif container.to in self.users:
            peerTo = self.users[chat.to]
            self.sendChat(peerTo, chat)
        else:
            pass
            #return error
    
    def sendChat(self, peer, chat):
        container = proto.Container()
        container.chat.to = chat.to
        container.chat.sender = chat.sender
        container.chat.message = chat.message
        messenger.post("sendData", [peer, container])
        
    def processIRCChat(self, peer, message):
        """
        Processes irc (RFC 1459) messages
        """
        print "Pre processed message:", message
        prefix, command, args = self.parsemsg(message)
        print "IRC:", prefix, command, args
        
        # These are all the commands we are going to impliment at the moment
        
        if command == "PRIVMSG":
            pass
        elif command == "JOIN":
            self.joinChannel(self, peer, prefix, command, args)
        elif command == "PART":
            for channel in args:
                self.removeUser(peer, prefix, command, args, channel)
        elif command == "QUIT":
            self.users.remove(peer)
            for channel in self.channels:
                if peer in self.channels[channel]:
                    self.removeUser(peer, prefix, command, args, channel)
        elif command == "USER":
            self.addIRCUser(peer, prefix, command, args)
    
    def removeUser(self, peer, prefix, command, args, channel):
        # User has left said channel
        if peer in self.channels[channel]:
            self.channels[channel].remove(peer)
            if not self.channels[channel]:
                del self.channels[channel]
    
    def joinChannel(self, peer, channels):
        for channel in channels:
            if channel not in self.channels:
                self.channels[channel] = []
                self.channels[channel].append(peer)
    
    #def addIRCUser(self, peer, prefix, command, args):
        #self.users.append(peer)
        #self.joinChannel(peer, prefix, command, ["#region"])
        
    def addUser(self, peer, username):
        self.users[username] = peer
        self.joinChannel(peer, ["#region"])
        
    def parsemsg(self, s):
        """
        Breaks a message from an IRC server into its prefix, command, and arguments.
        Theved from twisted
        """
        prefix = ''
        trailing = []
        if not s:
            #raise IRCBadMessage("Empty line.")
            return None, None, None
        if s[0] == ':':
            prefix, s = s[1:].split(' ', 1)
        if s.find(' :') != -1:
            s, trailing = s.split(' :', 1)
            args = s.split()
            args.append(trailing)
        else:
            args = s.split()
        command = args.pop(0)
        return prefix, command, args