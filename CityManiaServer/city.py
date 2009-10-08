# -*- coding: utf-8 -*-
"""
City class! Woot woot
"""
import engine

class City(engine.Entity):
    """
    This is the City class, the center piece to the entire simulation
    """
    def __init__(self, name="City", size=1):
        """
        self.size: City size.  Equivlent to SC4 city sizes.  Size 1 is small, Size 2 is Medium, Size 4 is large
        self.id: Unique ID for the city, position in the region cities list
        self.position:  Position of the city in the region
        self.neighbors: coordiants and cityID of the neighbor at those coordiants
        ex: (0,49,1) from tile 0 to 49 on that side, city 1 is the neighbor. NESW ([[(0,49,4)],[],[],[]])
        """
        self.name = name
        self.size = size
        self.id = 0
        self.position = (0,0)
        self.neighbors = [[],[],[],[]]
    
    def generate(self):
        pass