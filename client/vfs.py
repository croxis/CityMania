'''Class responsible for the virtual file system.'''
import os.path
from panda3d.core import VirtualFileSystem, Filename

vfs = None

def createVFS():
    '''Generates vfs. First loads program VFS, then user directory overrides'''
    global vfs
    vfs = VirtualFileSystem()
    vfs.mount(Filename('.'), Filename('.'), 0)
    vfs.mount(Filename(getHome()), Filename('.'), 0)

def getHome():
    '''Returns path to CityMania in the home directory.'''
    return os.path.expanduser('~') + '/CityMania/'
