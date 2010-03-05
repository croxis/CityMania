'''PagedGeoMipTerrain.py
Hacked together by croxis 2010
BSD licence'''

from panda3d.core import NodePath, PNMImage, GeoMipTerrain

class PagedGeoMipTerrain(object):
    '''Terrain using GeoMipTerrains from a heightfield. Paged in and out of render tree based if in view fullstrum.
    Syntax is as close to GeoMipTerrain as possible.
    Can accept any heightmap based on block*chunksize + 1
    The higher these values the fewer geoms, but the less variability allowed in the terrain.'''
    def __init__(self, name):
        self.name = name
        self.root = NodePath(name)
        self.blockSize = 32
        self.chunkSize = 1
        self.colorMap = None
        self.terrains = []
        self.bruitForce = False
        self.heightfield = None
    
    def clearColorMap(self):
        '''Clears the color map. Non functional.'''
    
    def generate(self):
        '''(Re)generate the entire terrain erasing any current changes'''
        factor = self.blockSize*self.chunkSize
        for terrain in self.terrains:
            terrain.getRoot().destroy()
        self.terrains = []
        # Breaking master heightmap into subimages
        heightmaps = []
        self.xchunks = (self.heightfield.getXSize()-1)/factor
        self.ychunks = (self.heightfield.getYSize()-1)/factor
        n = 0
        for y in range(0, self.ychunks):
            for x in range(0, self.xchunks):
                heightmap = PNMImage(factor+1, factor+1)
                heightmap.copySubImage(self.heightfield, 0, 0, xfrom = x*factor, yfrom = y*factor)
                heightmaps.append(heightmap)
                n += 1
        
        # Generate GeoMipTerrains
        n = 0
        for heightmap in heightmaps:
            terrain = GeoMipTerrain(str(n))
            terrain.setHeightfield(heightmap)
            terrain.setBruteforce(self.bruteForce)
            terrain.setBlockSize(self.blockSize)
            terrain.generate()
            self.terrains.append(terrain)
            root = terrain.getRoot()
            root.reparentTo(self.root)
            root.setPos(n%self.xchunks*factor, (self.ychunks-1-n/self.ychunks)*factor, 0)
            n += 1
    
    def getBlockFromPos(self, x, y):
        '''Gets the coordinates of the block at the specific position.'''
    
    def getBlockNodePath(self, x, y):
        '''Returns NodePath of the specified block'''
    
    def getChunk(self, x, y):
        '''Returns the GeoMipTerrain at the specificed position'''
    
    def getBlockSize(self):
        '''Returns the block size.'''
        return self.blockSize
    
    def getBruteforce(self):
        '''Returns boolian if terrain is being rendered with brute force or not'''
        return bruitForce
    
    def getElevation(self, x, y):
        '''Returns elevation at specific point in px.'''
        
    
    def getFocalPoint(self, x, y):
        '''Returns focal point as a node path'''
    
    def getMaxLevel(self):
        ''''Returns highest level of detail possible with current block size'''
    
    def getMinLevel(self):
        ''''Returns highest level of detail possible with current block size'''
    
    def getNormal(self, x, y):
        '''Returns normal at specified pixles'''
    
    def getRoot(self):
        '''Returns root nodepath'''
        return self.root
    
    def hasColorMap(self):
        '''Returns if a color map has been set'''
        if self.colorMap:
            return True
        return False
    
    def heightfield(self):
        '''Returns a reference to the master heightfield'''
    
    def isDirty(self):
        '''Returns a bool indicating is the terain will need to be updated next update(). 
        Usually because the heightfield has changed.'''
    
    def makeSlopeImage(self):
        '''Returns a greyscale PNMImage containing the slope angles.
        This is composited from the assorted GeoMipTerrains.'''
        slopeImage = PNMImage(self.heightfield.getXSize(), self.heightfield.getYSize())
        factor = self.blockSize*self.chunkSize
        n = 0
        for y in range(0, self.ychunks):
            for x in range(0, self.xchunks):
                slopei = self.terrains[n].makeSlopeImage()
                #slopeImage.copySubImage(slopei, x*factor, y*factor, 0, 0)
                slopeImage.copySubImage(slopei, x*factor, y*factor)
                n += 1
        return slopeImage
    
    def setAutoFlatten(self, mode):
        '''The terrain can be automatically flattened after each update'''
    
    def setBlockSize(self, size):
        '''Sets the block size. Must be power of 2.'''
        # TODO: Add power of two check
        self.blockSize = size
    
    def setBorderStitching(self, stitching):
        '''If set true the LOG at borders will be 0'''
    
    def setBruteforce(self, bruteForce):
        '''Set boolian if rendering will happen by brute force'''
        self.bruteForce = bruteForce
    
    def setColorMap(self, cm):
        '''Sets the color map. As GeoMipTerrain has several possible entries we will need to typecheck.'''
    
    def setFar(self, far):
        '''Sets the far LOD distance at which the terrain will be rendered at the lowest quality.'''
        for terrain in self.terrains:
            terrain.setFar(far)
    
    def setFocalPoint(self, focalPoint):
        '''Sets the focal point. Can be Nodepath, LPoint3, LPoint2'''
        for terrain in self.terrains:
            terrain.setFocalPoint(focalPoint)
    
    def setHeightfield(self, heightfield):
        '''Loads the heighmap image. Currently only accepts PNMIMage
        TODO: str path, FileName'''
        self.heightfield = heightfield
    
    def setMinLevel(self):
        ''' Sets the minimum level of detail at which blocks may be generated by generate() or update(). '''
    
    def setNear(self, near):
        '''Sets the near LOD distance, at which the terrain will be rendered at highest quality. '''
        for terrain in self.terrains:
            terrain.setNear(near)
    
    def setNearFar(self,near, far):
        '''Sets the near and far LOD distances in one call. '''
        for terrain in self.terrains:
            terrain.setNearFar(near, far)
    
    def update(self):
        '''Loops through all of the terrain blocks, and checks whether they need to be updated. '''
        for terrain in self.terrains:
            terrain.update()
