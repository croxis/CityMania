# -*- coding: utf-8 -*-
"""
City Mania
version: You have to start somewhere right?
"""

# TODO: These values should be in seperate config file
PORT = 2003

# TODO: Seperate files dude!

class Entity(object):
    """
    Basic Entity which almost everything should inherint from.  Currently provides integration to the event engine.
    """
    def __init__(self):
        pass
    
    def accept(self, event, method, extraArgs=[]):
        return messenger.accept(event, self, method, extraArgs)


class Event(object):
    """
    Base event. Used as empty tick for internal communication (maybe?).  Independent of game tick
    """
    def __init__ (self):
        self.name = "event"

class EventManager(object):
    def __init__ (self):
        """
        self.listeners: {event: {object1: [method, [arguments]], object2: [method2, [arguments]]}, event2... }
        """
        self.eventQueue = []
        self.listeners = {}
        
    def accept(self, event, object, method, extraArgs):
        """
        Adds a new listener into the database.  This is stored by event to reduce chattyness
        """
        if event not in self.listeners:
            self.listeners[event] = {}
        self.listeners[event][object] = [method, extraArgs]
            
    def send(self, event):
        """
        Notify all listening object of an event
        We will want to make this more intelligent to make the event system less chatty
        """
        self.eventQueue.append(event)
        
    def tick(self):
        """
        Processes self.eventQueue, one event at a time.  
        If no event, an empty tick event is sent (may not be necessary)
        """
        if self.eventQueue:
            event = self.eventQueue.pop()
        else:
            event = Event()
            
        for listener in self.listeners:
            listener.notify(event)

# We initialize the CityMania engine
messenger = EventManager()
