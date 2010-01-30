'''Common game tiles'''
class Tile(object):
    """
    Basic tile in simulation. Stores stuff
    """
    def __init__(self,ident,cityid=0,coords = (0,0)):
        """
        id: id number of tile
        cityid: id number of the city that owns the tile.
        """
        # TODO: Make thread safe
        self.id = ident
        self.cityid = cityid
        self.coords = coords
