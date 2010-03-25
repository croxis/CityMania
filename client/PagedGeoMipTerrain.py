'''PagedGeoMipTerrain.py
Hacked together by croxis 2010
BSD licence'''

from panda3d.core import NodePath, PNMImage, GeoMipTerrain, Texture, TextureStage
from panda3d.core import Vec2
from panda3d.core import GeomVertexReader, GeomVertexWriter

import math

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
        self.bruteForce = False
        self.heightfield = None
        self.xsize = 0
        self.ysize = 0
    
    def clearColorMap(self):
        '''Clears the color map. Non functional.'''
    
    def generate(self):
        '''(Re)generate the entire terrain erasing any current changes'''
        factor = self.blockSize*self.chunkSize
        #print "Factor:", factor
        for terrain in self.terrains:
            terrain.getRoot().removeNode()
        self.terrains = []
        # Breaking master heightmap into subimages
        heightmaps = []
        self.xchunks = (self.heightfield.getXSize()-1)/factor
        self.ychunks = (self.heightfield.getYSize()-1)/factor
        #print "X,Y chunks:", self.xchunks, self.ychunks
        n = 0
        for y in range(0, self.ychunks):
            for x in range(0, self.xchunks):
                heightmap = PNMImage(factor+1, factor+1)
                heightmap.copySubImage(self.heightfield, 0, 0, xfrom = x*factor, yfrom = y*factor)
                heightmaps.append(heightmap)
                n += 1
        
        # Generate GeoMipTerrains
        n = 0
        y = self.ychunks-1
        x = 0
        for heightmap in heightmaps:
            terrain = GeoMipTerrain(str(n))
            terrain.setHeightfield(heightmap)
            terrain.setBruteforce(self.bruteForce)
            terrain.setBlockSize(self.blockSize)
            terrain.generate()
            self.terrains.append(terrain)
            root = terrain.getRoot()
            root.reparentTo(self.root)
            root.setPos(n%self.xchunks*factor, (y)*factor, 0)
            
            # In order to texture span properly we need to reiterate through every vertex
            # and redefine the uv coordinates based on our size, not the subGeoMipTerrain's
            root = terrain.getRoot()
            children = root.getChildren()
            for child in children:
                geomNode = child.node()
                for i in range(geomNode.getNumGeoms()):
                    geom = geomNode.modifyGeom(i)
                    vdata = geom.modifyVertexData()
                    texcoord = GeomVertexWriter(vdata, 'texcoord')
                    vertex = GeomVertexReader(vdata, 'vertex')
                    while not vertex.isAtEnd():
                        v = vertex.getData3f()
                        t = texcoord.setData2f((v[0]+ self.blockSize/2 + self.blockSize*x)/(self.xsize - 1),
                                                        (v[1] + self.blockSize/2 + self.blockSize*y)/(self.ysize - 1))
            x += 1
            if x >= self.xchunks:
                x = 0
                y -= 1
            n += 1
    
    def getBlockFromPos(self, x, y):
        '''Gets the coordinates of the block at the specific position.'''
        if x < 0: x=0
        if y < 0: y=0
        if x > self.xsize - 1: x = self.xsize - 1
        if y > self.ysize - 1: y = self.ysize - 1
        factor = self.chunkSize * self.blockSize
        x = math.floor(x/factor)
        y = math.floor(y/factor)
        return Vec2(x, y)
    
    def getBlockNodePath(self, x, y):
        '''Returns NodePath of the specified block'''
        # Divide by chunksize to get terrain responsible
        xchunk = x/self.chunkSize
        ychunk = y/self.chunkSize
        terrain = self.terrains[int(ychunk*self.xchunks + xchunk)]
        nodePath = terrain.getBlockNodePath(x-(xchunk*self.chunkSize), y-(ychunk*self.chunkSize))
        return nodePath
    
    def getChunk(self, x, y):
        '''Returns the GeoMipTerrain at the specificed position'''
    
    def getBlockSize(self):
        '''Returns the block size.'''
        return self.blockSize
    
    def getBruteforce(self):
        '''Returns boolian if terrain is being rendered with brute force or not'''
        return bruitForce
    
    def getElevation(self, x, y):
        '''Returns elevation at specific point in px.
        Due to specific customizations for CityMania xy is in world coordinates.
        When this is generalized to a PagedGeoMipTerrain this will need to be redone.
        Z scale is not observed'''
        factor = self.blockSize*self.chunkSize
        # Determine which geomip holds the terrain
        row = y/(factor)
        col = x/(factor)
        #chunk = -row*self.ychunks - col
        chunk = self.getBlockFromPos(x, y)
        xchunk = chunk[0]/self.chunkSize
        ychunk = chunk[1]/self.chunkSize
        terrain = self.terrains[int(ychunk*self.xchunks + xchunk)]
        #terrain = self.terrains[int(chunk)]
        #terrain = self.terrains[int(row*self.xchunks + col)]
        # Convert to xy of chunk
        chunkx = x - col*factor
        chunky = y - row*factor
        elevation = terrain.getElevation(chunkx, chunky)
        return elevation
    
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
    
    def getSz(self):
        '''Citymania overide for sz'''
        return self.sz
    
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
    
    def makeTextureMap(self):
        '''Citymania function that generates and sets the 4 channel texture map'''
        self.colorTextures = []
        for terrain in self.terrains:
            terrain.getRoot().clearTexture()
            heightmap = terrain.heightfield()
            colormap = PNMImage(heightmap.getXSize()-1, heightmap.getYSize()-1)
            colormap.addAlpha()
            slopemap = terrain.makeSlopeImage()
            for x in range(0, colormap.getXSize()):
                for y in range(0, colormap.getYSize()):
                    # Else if statements used to make sure one channel is used per pixel
                    # Also for some optimization
                    # Snow. We do things funky here as alpha will be 1 already.
                    if heightmap.getGrayVal(x, y) < 200:
                        colormap.setAlpha(x, y, 0)
                    else:
                        colormap.setAlpha(x, y, 1)
                    # Beach. Estimations from http://www.simtropolis.com/omnibus/index.cfm/Main.SimCity_4.Custom_Content.Custom_Terrains_and_Using_USGS_Data
                    if heightmap.getGrayVal(x,y) < 62:
                        colormap.setBlue(x, y, 1)
                    # Rock
                    elif slopemap.getGrayVal(x, y) > 170:
                        colormap.setRed(x, y, 1)
                    else:
                        colormap.setGreen(x, y, 1)
            colorTexture = Texture()
            colorTexture.load(colormap)
            colorTS = TextureStage('color')
            colorTS.setSort(0)
            colorTS.setPriority(1)
            self.colorTextures.append((colorTexture, colorTS))
    
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
        if type(heightfield) is str:
            heightfield = PNMImage(heightfield)
        self.heightfield = heightfield
        self.xsize = heightfield.getXSize()
        self.ysize = heightfield.getYSize()
    
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
    
    def setSz(self, z):
        '''Citymania override to set the scale to the terrains'''
        self.sz = z
        for terrain in self.terrains:
            terrain.getRoot().setSz(z)
    
    def setTextureMap(self):
        '''Reactivates the texture map'''
        for n in range(0, len(self.terrains)):
            terrain = self.terrains[n]
            colorTexture, colorTS = self.colorTextures[n]
            terrain.getRoot().setTexture( colorTS, colorTexture )
    
    def update(self):
        '''Loops through all of the terrain blocks, and checks whether they need to be updated. '''
        for terrain in self.terrains:
            terrain.update()
