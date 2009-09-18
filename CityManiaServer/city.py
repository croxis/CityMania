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
        """
        self.name = name
        self.size = size