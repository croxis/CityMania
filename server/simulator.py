import engine

threads = {}
active_tiles = []

class SimulationCommander(engine.Entity):
    '''This class is responsible for connecting the rest of the engine to the threads.'''
    # TODO: Pausing a city should just remove it from the active tiles databases.
    def __init__(self):
        self.accept("requestGameState", self.pause)
        #self.accept('updateActiveTiles', self.updateActiveTiles)
        #self.accept('addSimulation', self.addSimulation)
        #self.accept('pause', self.pause)
        #self.accept('unpause', self.unpause)
    
    def pause(self, var1 = None):
        '''We will need to halt the simulation on some occasions, such as saving and connecting new clients.'''
        for thread in threads.values():
            thread.pause()

simulation_commander = SimulationCommander()

def updateActiveTiles(tile_list):
    '''Updates self and simulation thread active tiles database.
    It is up to the simulation to decide how to handle changes.
    '''
    self.active_tiles = tile_list
    for thread in self.threads.values():
        thread.updateActiveTiles(self.active_tiles)

def addSimulation(name, simulation):
    '''Accepts an uninstanced object.'''
    threads[name] = simulation(name=name, active_tiles = self.active_tiles)
    threads[name].start()

def pause(var1=None):
    '''For full region pausing'''
    for thread in threads.values():
        thread.pause()

def unpause():
    '''For full region unpausing.'''
    for thread in threads.values():
        thread.unpause()

import threading
class Simulation(engine.Entity, threading.Thread):
    '''Basic simulation thread. Can be subclasses or remade.
    These functions MUST exist so the simulation engine can use it.'''
    def __init__(self, name="Simulation", active_tiles=[]):
        '''Accepts name of the simulation as well as active tiles.'''
        threading.Thread.__init__(self)
        self.name = name
        self.active_tiles = active_tiles
        self.active_tiles_lock = threading.Lock()
        self.running = True
    
    def run(self):
        while self.running:
            pass
    
    def pause(self):
        pass
    
    def unpause(self):
        pass
    
    def updateActiveTiles(self, active_tiles):
        self.active_tiles_lock.acquire()
        self.active_tiles = active_tiles
        self.active_tiles_lock.release()
