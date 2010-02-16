# -*- coding: utf-8 -*-
"""
Filesystem class and supporting functions
Combines program files and userspace files into one filesystem.
Requires the python fs library http://code.google.com/p/pyfilesystem/
http://www.willmcgugan.com/blog/tech/2008/9/21/announcing-fs-010-a-python-file-system/
"""
import engine
import sys
sys.path.append("..")
import common.protocol_pb2 as proto
#import fs.osfs, fs.memoryfs, fs.utils
import os, base64, shutil

class FileSystem(engine.Entity):
    """
    Temporary class until a suitable replacement can be found.
    Uses assets in program directory only
    """
    def __init__(self):
        '''Initiates VFS.'''
        self.accept("requestMaps", self.sendMaps)
        self.accept("mapRequest", self.generateRegion)
        
        # Checks to see if home directory is set up properly and does so
        self.home = ""
        if os.name == "nt":
            from win32com.shell import shell
            df = shell.SHGetDesktopFolder()
            pidl = df.ParseDisplayName(0, None,"::{450d8fba-ad25-11d0-98a8-0800361b1103}")[1]
            self.home = shell.SHGetPathFromIDList(pidl)
        else:
            self.home = os.path.expanduser("~")
        if "CityMania" not in os.listdir(self.home):
            os.makedirs(self.home + "/CityMania/Maps")
            os.makedirs(self.home + "/CityMania/Regions")
            os.makedirs(self.home + "/CityMania/Logs")
        self.path = self.home + '/CityMania/'
        self.logs = self.path + 'Logs/'
    
    def sendMaps(self, peer):
        """
        Usually called when a client requests a game state with no region loaded
        Or wishes to generate a new region.
        maps = {"Mapname": (heightmap, citybitmap)}
        """
        maps = {}
        #os.chdir("Maps/")
        for directory in os.listdir("Maps/"):
            heightMap = open("Maps/"+directory+"/heightmap.png")
            # Convert to base64 for transmission over wire
            maps[directory] = base64.b64encode(heightMap.read())
            heightMap.close()
        
        # Now for a good question, how to send over wire with pb?
        container = proto.Container()
        for mapName in maps:
            mapContainer = container.maps.add()
            mapContainer.name = mapName
            mapContainer.heightmap = maps[mapName]
        messenger.send("sendData", [peer, container])
    
    def generateRegion(self, mapName, regionName="TestRegion"):
        """
        Generates new region filesystem
        """
        x = True
        n = 1
        version = ""
        # We spin through a versioning number system to emulate how sc4 did regions with the same name
        # This prevents an accedental overwrite
        # Information is then copied to the region in the home directory
        while x:
            if regionName + version in os.listdir(self.home + "/CityMania/Regions"):
                version = "[" + str(n) + "]"
                n += 1
            else:
                self.regionPath = self.home + "/CityMania/Regions/" + regionName+ version + "/"
                os.makedirs(self.regionPath)
                x = False
                try:
                    shutil.copyfile("Maps/"+mapName+"/heightmap.png", self.regionPath +"heightmap.png")
                except:
                    print "TODO: Add error message for missing map"
                    contrainer = proto.Container()
                    container.mapSelectError.message = "No such map name"
                    messenger.send("broadcastData", [container])
                    return
        heightMapFile = open(self.regionPath + "heightmap.png")
        heightMap = heightMapFile.read()
        heightMapFile.close()
        messenger.send("generateRegion", [regionName, heightMap])
    

class FileSystemWIP(engine.Entity):
    def __init__(self):
        """
        self.fs:    A RAM based filesystem that is the heart of the server fs
            May be converted into another system if memory requirements become too large
        self.programFS: OS FIlesystem representing the program files
        self.userFS:    OS Filesystem representing the user ~ files
        TODO: How to handle save and loads?
        """
        print "Loading files"
        self.fs = fs.memoryfs.MemoryFS()
        self.programFS = fs.osfs.OSFS(".")
        
        # We need to identify what os we are in, and generate the correct path
        if os.name == "nt":
            from win32com.shell import shell
            df = shell.SHGetDesktopFolder()
            pidl = df.ParseDisplayName(0, None,"::{450d8fba-ad25-11d0-98a8-0800361b1103}")[1]
            userPath = shell.SHGetPathFromIDList(pidl)
        else:
            userPath = os.path.expanduser("~")
        
        userPath += "/CityMania/"
        if not os.path.isdir(userPath):
            os.makedirs(userPath + "Maps/")
        
        self.userFS = fs.osfs.OSFS(userPath)
        
        self.loadFS()
    
    def loadFS(self):
        """
        Main FS is loaded here. Program files are load first, then user files
        This allows the user to overide defaults.
        """
        # Process the maps first, as it is the first I implimented
        #self.fs.makedir("Maps")
        #progMaps = self.programFS.opendir("Maps/")
        #fs.utils.copydir(progMaps, (self.fs, "Maps/"))
        #fs.utils.copydir(progMaps, self.fs)
        #print self.programFS.listdir("Maps/")
        fs.utils.copydir((self.programFS, "Maps"), (self.fs, "Maps"))
        
        # Test if we copies ok
        print self.fs.listdir("Maps/")
