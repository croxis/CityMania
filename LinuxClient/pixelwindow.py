# -*- coding: utf-8 -*-
from pandac.PandaModules import TextNode
from direct.gui.DirectGui import *
from direct.showbase import DirectObject
from layout import HBox, VBox
# Constants
# Text heigh in px
TEXT_HEIGHT = 25
BUTTON_HEIGHT = 25
ENTRY_HEIGHT = 25
TITLE_HEIGHT = 30

# a task that keeps a node at the position of the mouse-cursor
def mouseNodeTask( task ):
    if base.mouseWatcherNode.hasMouse():
        x=base.mouseWatcherNode.getMouseX()
        y=base.mouseWatcherNode.getMouseY()
        # the mouse position is read relative to render2d, so set it accordingly
        aspect2dMouseNode.setPos( render2d, x, 0, y )
    return task.cont
# maybe we should check if aspect2d doesnt already contain the aspect2dMouseNode
aspect2dMouseNode = aspect2d.attachNewNode( 'aspect2dMouseNode', sort = 999999 )
taskMgr.add( mouseNodeTask, 'mouseNodeTask' )


#class Window(DirectFrame):
class Window(VBox):
    """
    Base window for pixel based GUI
    Positioning reparented to the bottom left corner of the screen. 
    Based on Hypnos post here http://www.panda3d.org/phpbb2/viewtopic.php?t=4861
    """
    def __init__ (self, title="Title", size=(0,0), position=(0,0), center=False, xcenter=False, ycenter=False):
        """
        size:   size in absolute pixlesish
        widgets:    widgets contained in this window
        position:   Window Coordinates in px
        center:     If true the window will be initially drawn in the center of the screen overriding any position parameter
        xcenter:    If true the widow will be centered on the xaxis
        ycenter:    If true the window will be centered on the yaxis
        """
        #DirectFrame.__init__(self, parent = base.a2dBottomLeft, pos = (0, 0, 0), frameSize = (0,1,0,0), state = DGG.NORMAL)
        VBox.__init__(self, parent = base.a2dBottomLeft, pos = (0, 0, 0), state = DGG.NORMAL, frameSize = (0,0,0,0))
        self.initialiseoptions(self)
        
        # Accept main window resize events and redraws the widgets
        self.accept('window-event', self.draw)
        
        # Generate title bar
        self.window_title = title
        self.widgets = []
        self.size = size
        
        # Main container
        if center:
            centerxpx = base.win.getXSize()/2
            centerypx = base.win.getYSize()/2
            self.windowPosition = [centerxpx, centerypx]
        elif xcenter:
            centerxpx = base.win.getXSize()/2
            self.windowPosition = [centerxpx, position[1]]
        elif ycenter:
            centerypx = base.win.getYSize()/2
            self.windowPosition = [position[0], centerypx]
        else:
            self.windowPosition = [position[0], position[1]]
        
        xpos = self.px2float(self.windowPosition[0])
        ypos = self.px2float(self.windowPosition[1])
        
        self.setPos((xpos, 0, ypos))
        self.setBin("gui-popup", 50)
        
        # Title bar
        ypos = self.px2float(self.size[1]/2 + TITLE_HEIGHT/2)
        #self.titleBar = DirectButton(
        #                             parent = self, 
        #                             relief = DGG.FLAT,
        #                             pos = (0, 0, ypos)
        #                             )
        #self.titleBar = DirectButton(relief = DGG.FLAT)
        self.titleBar = DirectButton()
        self.titleBar['frameColor'] = (.1,.7,.1,1)
        text = TextNode("WindowTitleTextNode")
        text.setText(title)
        text.setAlign(TextNode.ACenter)
        self.textNodePath = self.titleBar.attachNewNode(text)
        self.textNodePath.setScale(0.07) 
        
        self.titleBar.bind(DGG.B1PRESS,self.startWindowDrag)
        self.pack(self.titleBar)
        
        #self.background = DirectFrame(parent = self, frameSize = (0,0,0,0),  state = DGG.NORMAL)
        #self.background = DirectFrame(parent = self, state = DGG.NORMAL)
        
        # This little bit is for Open Outpost
        messenger.send('makePickable', [self])
        messenger.send('makePickable', [self.titleBar])
        self.draw()
    
    def draw(self, args=None):
        """
        Draws window and contained elements
        """
        bounds = self.getTightBounds()
        print "Bounds:", bounds
        
        # Draw window
        #left = -self.px2float(self.size[0]/2)
        left = bounds[0][2]
        right = -left
        bottom = -self.px2float(self.size[1]/2)
        top = -bottom
        #self.background['frameSize'] = (left, right, bottom, top)
        #self['frameSize'] = (left, right, bottom, top)
        
        # Rescale bottom for the title bar
        ypos = self.px2float(self.size[1]/2 + TITLE_HEIGHT/2)
        #self.titleBar.setPos(0, 0, ypos)
        top = self.px2float(TITLE_HEIGHT/2)
        bottom = -top
        #self.titleBar['frameSize'] = (left, right, bottom, top)
        
        # Adjust title scale
        self.textNodePath.setScale(self.px2float(TITLE_HEIGHT/2)) 
        
        # Process Boxes?
        
        # Process widgets
        for widget in self.widgets:
            self.processWidget(widget)
    
    def px2float(self, px):
        """
        Converts an absolute pixel coordinate to the aspect2d float coordinate
        Aspect2d scale is dependent or width or height, whichever is shorter
        """
        # Find the shorter side and use that resolution
        xrez = base.win.getXSize()
        yrez = base.win.getYSize()
        if xrez > yrez:
            rez = yrez
        else:
            rez = xrez
        return float(px)/float(rez)*2
    
    def startWindowDrag( self, param ):
        self.wrtReparentTo( aspect2dMouseNode )
        self.ignoreAll()
        self.accept( 'mouse1-up', self.stopWindowDrag )
    
    def stopWindowDrag( self, param=None ):
    # this is called 2 times (bug), so make sure it's not already parented to aspect2d
        if self.getParent() != base.a2dBottomLeft:
            self.wrtReparentTo( base.a2dBottomLeft )
    
    def processWidget(self, widget):
        """
        Processes widget to proper size and adds widget to database
        If not directgui we return
        """
        if isinstance(widget, DirectButton):
            widget.setScale(self.px2float(BUTTON_HEIGHT)/2)
        elif isinstance(widget, DirectLabel):
            textScale = self.px2float(TEXT_HEIGHT/2)
            widget.setScale(textScale)
        elif isinstance(widget, DirectEntry):
            widget.setScale(self.px2float(ENTRY_HEIGHT)/2)
    
    
class StandardWindow(Window):
    """
    Standard window.  Boxes are added in a top to bottom fashion
    """
    def addHorizontal(self, widgets):
        """
        Accepts a list of directgui objects which are added to a horizontal box, which is then added to the vertical stack.
        """
        hbox = HBox(parent = self)
        for widget in widgets:
            self.processWidget(widget)
            hbox.pack(widget)
            self.widgets.append(widget)
        self.pack(hbox)
    
    def addVertical(self, widgets):
        """
        Accepts a list of directgui objects which are added to a vertical box, which is then added to the vertical stack.
        May cause funky layout results.
        """
        vbox = VBox(parent=self)
        for widget in widgets:
            self.processWidget(widget)
            vbox.pack(widget)
            self.widgets.append(widget)
        self.pack(vbox)      
    
    def addWidget(self, widget):
        """
        Processes widget to proper size, packs it into box, and adds widget to database
        """
        self.processWidget(widget)
        self.pack(widget)
        self.widgets.append(widget)
    
    def getEntries(self):
        """
        Returns the fields for any entires
        """
        entries = []
        for widget in self.widgets:
            if isinstance(widget, DirectEntry):
                entries.append(widget.get())
        return entries


class MessageWindow(StandardWindow):
    """
    Generates a "simple" dialogue window with text and an ok button to close.
    A custom button can be passed instead
    """
    def __init__(self, text, title = "Title", button=None):
        StandardWindow.__init__(self, title=title, size=(0,0), center = True)
        #textBox = DirectLabel(text = text, parent = self)
        textBox = DirectLabel(text = text)
        self.pack(textBox)
        if not button:
            #button = DirectButton(parent = self, text = text, command = self.destroy())
            button = DirectButton(text = "OK", command = self.destroy)
        self.pack(button)
        self.draw()
