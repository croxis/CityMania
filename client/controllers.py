# -*- coding: utf-8 -*-
'''Controllers for stuff'''

from direct.showbase import DirectObject

class KMController(DirectObject.DirectObject):
    '''Class converts mouse and keyboard commands into internal messages.
    This will allow for user defined keybindings'''
    def __init__(self):
        '''Initializes internal commands only'''
        self.hardCodeInit()
    def hardCodeInit(self):
        '''Temporary function to set up keybindings'''
        self.accept('w', lambda : messenger.send('camera-up'))
        self.accept('a', lambda : messenger.send('camera-left'))
        self.accept('s', lambda : messenger.send('camera-down'))
        self.accept('d', lambda : messenger.send('camera-right'))
        self.accept('w-repeat', lambda : messenger.send('camera-up'))
        self.accept('a-repeat', lambda : messenger.send('camera-left'))
        self.accept('s-repeat', lambda : messenger.send('camera-down'))
        self.accept('d-repeat', lambda : messenger.send('camera-right'))
        
