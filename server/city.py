# -*- coding: utf-8 -*-
"""
City class! Woot woot
"""
import engine

class City(engine.Entity):
    """
    This is the City class, the center piece to the entire simulation
    """
    def __init__(self, name="City", id=0, password="", funds=100000, mayor="", population = 0):
        """
        self.id: Unique ID for the city, position in the region cities list
        self.neighbors: coordiants and cityID of the neighbor at those coordiants
        """
        self.name = name
        self.id = 0
        self.funds = funds
        self.password = password
        self.mayor = mayor
        self.population = population
    
    def generate(self):
        pass
