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

import direct.directbase.DirectStart

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


DIRECTORY = 'windowBorders/'

DEFAULT_TITLE_GEOM_LEFT                 = loader.loadTexture( DIRECTORY+'titleLeft.png' )
DEFAULT_TITLE_GEOM_CENTER               = loader.loadTexture( DIRECTORY+'titleCenter.png' )
DEFAULT_TITLE_GEOM_RIGHT                = loader.loadTexture( DIRECTORY+'titleRight.png' )
DEFAULT_TITLE_GEOM_RIGHT_CLOSE          = loader.loadTexture( DIRECTORY+'titleRightClose.png' )
DEFAULT_RESIZE_GEOM                     = loader.loadTexture( DIRECTORY+'resize.png' )

VERTICALSCROLL_FRAMETEXTURE             = loader.loadTexture( DIRECTORY+'scrollVerticalBorder.png' )
VERTICALSCROLL_INCBUTTON_FRAMETEXTURE   = loader.loadTexture( DIRECTORY+'scrollVerticalDown.png' )
VERTICALSCROLL_DECBUTTON_FRAMETEXTURE   = loader.loadTexture( DIRECTORY+'scrollVerticalUp.png' )
VERTICALSCROLL_TUMB_FRAMETEXTURE        = loader.loadTexture( DIRECTORY+'scrollVerticalBar.png' )
HORIZONTALSCROLL_FRAMETEXTURE           = loader.loadTexture( DIRECTORY+'scrollHorizontalBorder.png' )
HORIZONTALSCROLL_INCBUTTON_FRAMETEXTURE = loader.loadTexture( DIRECTORY+'scrollHorizontalRight.png' )
HORIZONTALSCROLL_DECBUTTON_FRAMETEXTURE = loader.loadTexture( DIRECTORY+'scrollHorizontalLeft.png' )
HORIZONTALSCROLL_TUMB_FRAMETEXTURE      = loader.loadTexture( DIRECTORY+'scrollHorizontalBar.png' )

class DirectWindow( DirectFrame ):
  def __init__( self,
                pos              = ( -.5, .5),
                title            = 'Title',
                curSize          = ( 1, 1),
                maxSize          = ( 1, 1 ),
                minSize          = ( .5, .5 ),
                backgroundColor  = ( 1, 1, 1, 1 ),
                borderColor      = ( 1, 1, 1, 1 ),
                titleColor       = ( 1, 1, 1, 1 ),
                borderSize       = 0.04,
                titleSize        = 0.06,
                closeButton      = False,
              ):
    
    self.windowPos = pos
    DirectFrame.__init__( self,
        parent       = aspect2d,
        pos          = ( self.windowPos[0], 0, self.windowPos[1] ),
        frameColor  = ( 0, 0, 0, 0 ),
        frameTexture = loader.loadTexture( DIRECTORY+'transparent.png' )
      )
    self.setTransparency(True)
    
    # the title part of the window, drag around to move the window
    self.headerHeight = titleSize
    h = -self.headerHeight
    self.windowHeaderLeft = DirectButton(
        parent       = self,
        frameTexture = DEFAULT_TITLE_GEOM_LEFT,
        frameSize    = ( -.5, .5, -.5, .5 ),
        borderWidth  = ( 0, 0 ),
        relief       = DGG.FLAT,
        frameColor   = titleColor,
      )
    self.windowHeaderCenter = DirectButton(
        parent       = self,
        frameTexture = DEFAULT_TITLE_GEOM_CENTER,
        frameSize    = ( -.5, .5, -.5, .5 ),
        borderWidth  = ( 0, 0 ),
        relief       = DGG.FLAT,
        frameColor   = titleColor,
      )
    if closeButton:
      rightTitleGeom = DEFAULT_TITLE_GEOM_RIGHT_CLOSE
      command = self.destroy
    else:
      rightTitleGeom = DEFAULT_TITLE_GEOM_RIGHT
      command = None
    self.windowHeaderRight = DirectButton(
        parent       = self,
        frameTexture = rightTitleGeom,
        frameSize    = ( -.5, .5, -.5, .5 ),
        borderWidth  = ( 0, 0 ),
        relief       = DGG.FLAT,
        frameColor   = titleColor,
        command      = command
      )
    
    self.windowHeaderLeft.setTransparency(True)
    self.windowHeaderCenter.setTransparency(True)
    self.windowHeaderRight.setTransparency(True)
    
    self.windowHeaderLeft.bind( DGG.B1PRESS, self.startWindowDrag )
    self.windowHeaderCenter.bind( DGG.B1PRESS, self.startWindowDrag )
    self.windowHeaderRight.bind( DGG.B1PRESS, self.startWindowDrag )
    
    # this is not handled correctly, if a window is dragged which has been
    # created before another it will not be released
    # check the bugfixed startWindowDrag function
    #self.windowHeader.bind(DGG.B1RELEASE,self.stopWindowDrag)
    
    text = TextNode('WindowTitleTextNode')
    text.setText(title)
    text.setAlign(TextNode.ACenter)
    text.setTextColor( 0, 0, 0, 1 )
    text.setShadow(0.05, 0.05)
    text.setShadowColor( 1, 1, 1, 1 )
    self.textNodePath = self.attachNewNode(text)
    self.textNodePath.setScale(self.headerHeight*0.8)
    
    # the content part of the window, put stuff beneath
    # contentWindow.getCanvas() to put it into it
    self.maxVirtualSize = maxSize
    self.minVirtualSize = minSize
    self.resizeSize     = borderSize
    self.contentWindow = DirectScrolledFrame(
        parent                                  = self,
        pos                                     = ( 0, 0, -self.headerHeight ),
        canvasSize                              = ( 0, self.maxVirtualSize[0], 0, self.maxVirtualSize[1] ),
        frameColor                              = ( 0, 0, 0, 0), # defines the background color of the resize-button
        relief                                  = DGG.FLAT,
        borderWidth                             = (0, 0),
        verticalScroll_frameSize                = [0, self.resizeSize, 0, 1],
        horizontalScroll_frameSize              = [0, 1, 0, self.resizeSize],
        
        # resize the scrollbar according to window size
        verticalScroll_resizeThumb              = False,
        horizontalScroll_resizeThumb            = False,
        # define the textures for the scrollbars
        verticalScroll_frameTexture             = VERTICALSCROLL_FRAMETEXTURE,
        verticalScroll_incButton_frameTexture   = VERTICALSCROLL_INCBUTTON_FRAMETEXTURE,
        verticalScroll_decButton_frameTexture   = VERTICALSCROLL_DECBUTTON_FRAMETEXTURE,
        verticalScroll_thumb_frameTexture       = VERTICALSCROLL_TUMB_FRAMETEXTURE,
        horizontalScroll_frameTexture           = HORIZONTALSCROLL_FRAMETEXTURE,
        horizontalScroll_incButton_frameTexture = HORIZONTALSCROLL_INCBUTTON_FRAMETEXTURE,
        horizontalScroll_decButton_frameTexture = HORIZONTALSCROLL_DECBUTTON_FRAMETEXTURE,
        horizontalScroll_thumb_frameTexture     = HORIZONTALSCROLL_TUMB_FRAMETEXTURE,
        # make all flat, so the texture is as we want it
        verticalScroll_relief                   = DGG.FLAT,
        verticalScroll_thumb_relief             = DGG.FLAT,
        verticalScroll_decButton_relief         = DGG.FLAT,
        verticalScroll_incButton_relief         = DGG.FLAT,
        horizontalScroll_relief                 = DGG.FLAT,
        horizontalScroll_thumb_relief           = DGG.FLAT,
        horizontalScroll_decButton_relief       = DGG.FLAT,
        horizontalScroll_incButton_relief       = DGG.FLAT,
        # colors
        verticalScroll_frameColor               = borderColor,
        verticalScroll_incButton_frameColor     = borderColor,
        verticalScroll_decButton_frameColor     = borderColor,
        verticalScroll_thumb_frameColor         = borderColor,
        horizontalScroll_frameColor             = borderColor,
        horizontalScroll_incButton_frameColor   = borderColor,
        horizontalScroll_decButton_frameColor   = borderColor,
        horizontalScroll_thumb_frameColor       = borderColor,
      )
    self.contentWindow.setTransparency(True)
    
    # background color
    self.backgroundColor = DirectFrame(
        parent       = self.contentWindow.getCanvas(),
        frameSize    = ( 0, self.maxVirtualSize[0], 0, self.maxVirtualSize[1] ),
        frameColor   = backgroundColor,
        relief       = DGG.FLAT,
        borderWidth  = ( .01, .01),
      )
    self.backgroundColor.setTransparency(True)
    
    # is needed for some nicer visuals of the resize button (background)
    self.windowResizeBackground = DirectButton(
        parent       = self,
        frameSize    = ( -.5, .5, -.5, .5 ),
        borderWidth  = ( 0, 0 ),
        scale        = ( self.resizeSize, 1, self.resizeSize ),
        relief       = DGG.FLAT,
        frameColor   = backgroundColor,
      )
    # the resize button of the window
    self.windowResize = DirectButton(
        parent       = self,
        frameSize    = ( -.5, .5, -.5, .5 ),
        borderWidth  = ( 0, 0 ),
        scale        = ( self.resizeSize, 1, self.resizeSize ),
        relief       = DGG.FLAT,
        frameTexture = DEFAULT_RESIZE_GEOM,
        frameColor   = borderColor,
      )
    self.windowResize.setTransparency(True)
    self.windowResize.bind(DGG.B1PRESS,self.startResizeDrag)
    self.windowResize.bind(DGG.B1RELEASE,self.stopResizeDrag)
    
    # offset then clicking on the resize button from the mouse to the resizebutton
    # position, required to calculate the position / scaling
    self.offset = None
    self.taskName = "resizeTask-%s" % str(hash(self))
    
    # do sizing of the window (minimum)
    #self.resize( Vec3(0,0,0), Vec3(0,0,0) )
    # maximum
    #self.resize( Vec3(100,0,-100), Vec3(0,0,0) )
    self.resize( Vec3(curSize[0], 0, -curSize[1]), Vec3(0,0,0))
  
  def getCanvas(self):
    return self.contentWindow.getCanvas()
  
  # dragging functions
  def startWindowDrag( self, param ):
    self.wrtReparentTo( aspect2dMouseNode )
    self.ignoreAll()
    self.accept( 'mouse1-up', self.stopWindowDrag )
  def stopWindowDrag( self, param=None ):
    # this is called 2 times (bug), so make sure it's not already parented to aspect2d
    if self.getParent() != aspect2d:
      self.wrtReparentTo( aspect2d )
  
  # resize functions
  def resize( self, mPos, offset ):
    mXPos = max( min( mPos.getX(), self.maxVirtualSize[0] ), self.minVirtualSize[0])
    mZPos = max( min( mPos.getZ(), -self.minVirtualSize[1] ), -self.maxVirtualSize[1]-self.headerHeight)
    self.windowResize.setPos( mXPos-self.resizeSize/2., 0, mZPos+self.resizeSize/2. )
    self.windowResizeBackground.setPos( mXPos-self.resizeSize/2., 0, mZPos+self.resizeSize/2. )
    self['frameSize'] = (0, mXPos, 0, mZPos)
    self.windowHeaderLeft.setPos( self.headerHeight/2., 0, -self.headerHeight/2. )
    self.windowHeaderLeft.setScale( self.headerHeight, 1, self.headerHeight )
    self.windowHeaderCenter.setPos( mXPos/2., 0, -self.headerHeight/2. )
    self.windowHeaderCenter.setScale( mXPos - self.headerHeight*2., 1, self.headerHeight )
    self.windowHeaderRight.setPos( mXPos-self.headerHeight/2., 0, -self.headerHeight/2. )
    self.windowHeaderRight.setScale( self.headerHeight, 1, self.headerHeight )
    self.contentWindow['frameSize'] = ( 0, mXPos, mZPos+self.headerHeight, 0)
    self.textNodePath.setPos( mXPos/2., 0, -self.headerHeight/3.*2. )
    # show and hide that small background for the window sizer
    if mXPos == self.maxVirtualSize[0] and \
       mZPos == -self.maxVirtualSize[1]-self.headerHeight:
      self.windowResizeBackground.hide()
    else:
      self.windowResizeBackground.show()
  
  def resizeTask( self, task=None ):
    mPos = aspect2dMouseNode.getPos( self )+self.offset
    self.resize( mPos, self.offset )
    return task.cont
  def startResizeDrag( self, param ):
    self.offset  = self.windowResize.getPos( aspect2dMouseNode )
    taskMgr.remove( self.taskName )
    taskMgr.add( self.resizeTask, self.taskName )
  def stopResizeDrag( self, param ):
    taskMgr.remove( self.taskName )
    # get the window to the front
    self.wrtReparentTo( aspect2d )

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
        print self.getPos()
        
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
