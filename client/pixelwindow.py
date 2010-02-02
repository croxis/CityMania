# -*- coding: utf-8 -*-
from pandac.PandaModules import TextNode
from direct.gui.DirectGui import *
from direct.showbase import DirectObject
from layout import HBox, VBox
# Constants
# Text heigh in px
TEXT_SCALE = 0.05
BUTTON_SCALE = 0.05
ENTRY_SCALE = 0.05
TITLE_SCALE = 0.05

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

from pandac.PandaModules import TextNode, Vec3
from direct.gui.DirectGui import DirectFrame,DirectButton,DirectScrolledFrame,DGG

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
        VBox.__init__(self, parent = base.aspect2d, pos = (0, 0, 0), state = DGG.NORMAL, frameSize = (0,0,0,0))
        self.initialiseoptions(self)
        
        # Accept main window resize events and redraws the widgets
        self.accept('window-event', self.draw)
        
        # Generate title bar
        self.window_title = title
        self.widgets = []
        self.size = size
        
        # Main container
        if center:
            self.windowPosition = [0, 0]
        elif xcenter:
            self.windowPosition = [0, position[1]]
        elif ycenter:
            self.windowPosition = [position[0], 0]
        else:
            self.windowPosition = [position[0], position[1]]
        
        xpos = self.windowPosition[0]
        ypos = self.windowPosition[1]
        
        self.setPos((xpos, 0, ypos))
        self.setBin("gui-popup", 50)
        #print self.getPos()
        
        # Title bar
        #ypos = self.size[1] + 0.05
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
        
        # Draw window
        #left = -self.px2float(self.size[0]/2)
        left = bounds[0][2]
        right = -left
        bottom = -self.size[1]
        top = -bottom
        #self.background['frameSize'] = (left, right, bottom, top)
        #self['frameSize'] = (left, right, bottom, top)
        
        # Rescale bottom for the title bar
        ypos = self.size[1]/2
        #self.titleBar.setPos(0, 0, ypos)
        top = TITLE_SCALE
        bottom = -top
        #self.titleBar['frameSize'] = (left, right, bottom, top)
        
        # Adjust title scale
        self.textNodePath.setScale(TITLE_SCALE) 
        
        # Process Boxes?
        
        # Process widgets
        for widget in self.widgets:
            self.processWidget(widget)
    
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
            widget.setScale(BUTTON_SCALE)
        elif isinstance(widget, DirectLabel):
            widget.setScale(TEXT_SCALE)
        elif isinstance(widget, DirectEntry):
            widget.setScale(ENTRY_SCALE)
        elif isinstance(widget, DirectScrolledList):
            print dir(widget)
            #for item in widget.items:
            #    self.processWidget(item)
    
    
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
    
    def addScrolledList(self, items):
        '''Adds a list of items into a scrolled list'''
        scrolled_list = DirectScrolledList(
            decButton_pos= (0.35, 0, 0.53),
            decButton_text = "Dec",
            decButton_text_scale = 0.04,
            decButton_borderWidth = (0.005, 0.005),
            incButton_pos= (0.35, 0, -0.02),
            incButton_text = "Inc",
            incButton_text_scale = 0.04,
            incButton_borderWidth = (0.005, 0.005),
            frameSize = (0.0, 0.7, -0.05, 0.59),
            frameColor = (1,0,0,0.5),
            pos = (-1, 0, 0),
            itemFrame_frameSize = (-0.2, 0.2, -0.37, 0.11),
            itemFrame_pos = (0.35, 0, 0.4),
            )
        for widget in items:
            self.processWidget(widget)
            scrolled_list.addItem(widget)
        self.pack(scrolled_list)


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
