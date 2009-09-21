# -*- coding: utf-8 -*-
"""
Chat server engine and interpriter
TODO: impliment IRC protocol
"""
import engine

class ChatServer(engine.Entity):
    """
    Chat server implimentation
    There are plans to intigrate a minimal IRC capacity into this
    """
    def __init__(self):
        """
        """
        self.accept("chat", self.processChat)
        self.users = []
        # channels = {channel1: [user1, user2]}
        self.channels = {"#region": []}
    
        
    def processChat(self, peer, message):
        """
        Processes irc (RFC 1459) messages
        
        """
        prefix, command, args = self.parsemsg(message)
        print message
        print prefix, command, args
        
        # These are all the commands we are going to impliment at the moment
        
        if command == "PRIVMSG":
            pass
        elif command == "JOIN":
            if args[0] not in self.channels:
                self.channels[args[0]] = []
            self.channels.append(peer)
        elif command == "PART":
            for channel in args:
                self.removeUser(peer, prefix, command, args, channel)
        elif command == "QUIT":
            self.users.remove(peer)
            for channel in self.channels:
                if peer in self.channels[channel]:
                    self.removeUser(peer, prefix, command, args, channel)
    
    def removeUser(self, peer, prefix, command, args, channel):
        # User has left said channel
        if peer in self.channels[channel]:
            self.channels[channel].remove(peer)
            if not self.channels[channel]:
                del self.channels[channel]
        
    def parsemsg(self, s):
        """Breaks a message from an IRC server into its prefix, command, and arguments.
        Theved from twisted
        """
        prefix = ''
        trailing = []
        if not s:
            raise IRCBadMessage("Empty line.")
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