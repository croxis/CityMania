# -*- coding: utf-8 -*-
 
"""
CityMania Engine
Contains message system, task manager, and the like
"""

class EventManager(object):
    def __init__ (self):
        """
        self.listeners: {event: {object1: [method, [arguments]], object2: [method2, [arguments]]}, event2... }
        I *think* this is thread safe as is as thread's arn't directly writing to it.
        We'll find out :P
        """
        self.listeners = {}
        self.eventQueue = []
        self.running = False
        
    def accept(self, event, method, extraArgs, object):
        """
        Adds a new listener into the database.  This is stored by event to reduce chattyness
        Overides Entity.accept(), not best design
        """
        if event not in self.listeners:
            self.listeners[event] = {}
        self.listeners[event][object] = [method, extraArgs]
    
    def ignore(self, event, object):
        """
        Removes listening object from database
        Removes event if that event databse is empty
        """
        if event in self.listeners:
            if object in self.listeners[event]:
                del self.listeners[event][object]
            if not self.listeners[event]:
                del self.listeners[event]
    
    def post(self, event, extraArgs=[]):
        """
        Events are posted into self.eventQueue
        """
        self.eventQueue.append((event, extraArgs))
    
    def start(self):
        self.running = True
        while self.running:
            try:
                #print "Tickstep"
                self.step()
                #print "End tick"
            except KeyboardInterrupt:
                print "Interupt!"
                messenger.post("exit")
                self.stop()
                
    def stop(self):
        self.running = False
        print "Stopping"
        
    def step(self):
        self.send()
        #print "End Send"
            
    def send(self):
        """
        Notify all listening object of an event
        We also pump tick events here
        TODO: Add error checking
        """
        #print "Send"
        objects = self.listeners["tick"]
        for object in objects:
            method, args = objects[object]
            #print object, method, args
            method()
        #print "Send2"
        if self.eventQueue:
            event, extraArgs = self.eventQueue.pop()
            if event in self.listeners:
                objects = self.listeners[event]
                for object in objects:
                    method, args = objects[object]
                    
                    method(*extraArgs)
import __builtin__
__builtin__.messenger = EventManager()


class Entity(object):
    """
    Basic Entity which almost everything should inherint from.  Currently provides integration to the event engine.
    """
    def __init__(self):
        pass
    
    def accept(self, event, method, extraArgs=[]):
        """
        Add object to event system
        """
        return messenger.accept(event, method, extraArgs, self)    
        
    def ignore(self):
        """
        Removes object from event system
        """
        return messenger.ignore(event, self) 