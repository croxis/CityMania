# -*- coding: utf-8 -*-
"""
City class! Woot woot
"""
import engine

class City(engine.Entity):
    """
    """
    def __init__(self, name="City", ident=0, password="", funds=100000, mayor="", population = 0):
        """
        self.id: Unique ID for the city, position in the region cities list
        """
        self.name = name
        self.ident = 0
        self.funds = funds
        self.password = password
        self.mayor = mayor
        self.population = population
    
    def generate(self):
        pass
