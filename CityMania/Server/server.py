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
        self.listeners = {}
        
    def accept(self, event, object, method, extraArgs):
        """
        Adds a new listener into the database.  This is stored by event to reduce chattyness
        """
        if event not in self.listeners:
            self.listeners[event] = {}
        self.listeners[event][object] = [method, extraArgs]
            
    def send(self, event, extraArgs=[]):
        """
        Notify all listening object of an event
        TODO: Add error checking
        """
        objects = self.listeners[event]
        for object in objects:
            method, extraArgs = objects[object]
            method(extraArgs)

# We initialize the CityMania engine
messenger = EventManager()
import time

class Spinner(Entity):
    """
    Master game loop spinner thing
    May wish to consider intigrating a task manager
    Speeds are normal, medium, and fast speeds in Hz
    Regulates simulation speed
    Pause is set to high number to prevent divide by 0 errors
    TODO: Develop system for Hz to be adjuststed based on slower clients
    """
    PAUSE = 999999999999999999.0
    SLOW = 1.0
    MEDIUM = 2.0
    FAST = 3.0
    def __init__(self):
        self.running = False
        self.speed = SLOW
    
    def start(self):
        self.running = True
        while self.running:
            try:
                # Possible problems: we might run into wierd dependency issues
                # Also, this blank event is the time keeper tick, do we want this 
                # inherient for all Entities, or just those worried about keeping
                # track of the time?
                self.step()
                time.sleep(1/self.speed)
            except KeyboardInterrupt:
                self.stop()
    
    def stop(self):
        self.running = False
    
    def step(self):
        messenger.send(Event())
    
    def setSpeed(self, speed):
        """
        sets speed of simulation
        speed = 0, 1, 2, 3
        """
        if speed is 0:
            self.speed = PAUSE
        elif speed is 1:
            self.speed = SLOW
        elif speed is 2:
            self.speed = MEDIUM
        elif speed is 3:
            self.speed = FAST
    
spinner = Spinner()

main():
    pass

if __name__ == "__main__":
    main()