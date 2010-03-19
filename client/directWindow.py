# -*- coding: utf-8 -*-
from pandac.PandaModules import TextNode, Vec3
from direct.gui.DirectGui import DirectFrame,DirectButton,DirectScrolledFrame,DGG,DirectLabel, DirectEntry, DirectScrolledList
import boxes
import direct.directbase.DirectStart

#from direct.gui.DirectGui import DirectLabel, DirectEntry
#from panda3d.core import Point3


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
                curSize          = (1, 1),
                maxSize          = ( 1, 1 ),
                minSize          = ( .5, .5 ),
                backgroundColor = ( 0, 0, 1, .6),
                borderColor      = ( 1, 1, 1, 1 ),
                titleColor       = ( 1, 1, 1, 1 ),
                borderSize       = 0.04,
                titleSize        = 0.06,
                closeButton      = False,
                windowParent     = aspect2d,
                preserve         = True,
                preserveWhole      = True, 
              ):
    self.preserve = preserve
    self.preserveWhole = preserveWhole
    self.windowParent = windowParent
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

    # Add a box
    self.box = boxes.VBox(parent = self.getCanvas())

   
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
    self.widgets = []
  
  def getCanvas(self):
    return self.contentWindow.getCanvas()
  
  # dragging functions
  def startWindowDrag( self, param ):
    self.wrtReparentTo( aspect2dMouseNode )
    self.ignoreAll()
    self.accept( 'mouse1-up', self.stopWindowDrag )
  def stopWindowDrag( self, param=None ):
    # this is called 2 times (bug), so make sure it's not already parented to aspect2d
    if self.getParent() != self.windowParent:
      self.wrtReparentTo( self.windowParent )
    if self.preserve:
        if self.preserveWhole:
            if self.getZ() > 1:
                self.setZ(1)
            elif self.getZ() < -1 - self.getHeight():
                self.setZ(-1 - self.getHeight())
            if self.getX() > base.a2dRight - self.getWidth():
                self.setX(base.a2dRight - self.getWidth())
            elif self.getX() < base.a2dLeft:
                self.setX(base.a2dLeft)
        else:
            if self.getZ() > 1:
                self.setZ(1)
            elif self.getZ() < -1 + self.headerHeight:
                self.setZ(-1 + self.headerHeight)
            if self.getX() > base.a2dRight - self.headerHeight:
                self.setX(base.a2dRight - self.headerHeight)
            elif self.getX() < base.a2dLeft + self.headerHeight - self.getWidth():
                self.setX(base.a2dLeft + self.headerHeight - self.getWidth())
    #else: #Window moved beyond reach. Destroy window?
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
    self.wrtReparentTo( self.windowParent )
  def addHorizontal(self, widgets):
      """
      Accepts a list of directgui objects which are added to a horizontal box, which is then added to the vertical stack.
      """
      hbox = boxes.HBox()
      for widget in widgets:
          widget.setScale(0.05)
          hbox.pack(widget)
          self.widgets.append(widget)
      self.box.pack(hbox)
      self.updateMaxSize()
  
  def addVertical(self, widgets):
      """
      Accepts a list of directgui objects which are added to a vertical box, which is then added to the vertical stack.
      May cause funky layout results.
      """
      for widget in widgets:
          widget.setScale(0.05)
          self.box.pack(widget)
          self.widgets.append(widget)
      self.updateMaxSize()
  
  def add(self, widgets):
      """Shortcut function for addVertical"""
      self.addVertical(widgets)
  
  def updateMaxSize(self):
      """Updates the max canvas size to include all items packed.
      Window is resized to show all contents."""
      bottomLeft, topRight = self.box.getTightBounds()
      self.maxVirtualSize = (topRight[0], -bottomLeft[2])
      if self.minVirtualSize[0] > self.maxVirtualSize[0]:
          self.minVirtualSize = (self.maxVirtualSize[0], self.minVirtualSize[1])
      if self.minVirtualSize[1] > self.maxVirtualSize[1]:
          self.minVirtualSize = (self.minVirtualSize[0], self.maxVirtualSize[1]+self.headerHeight)
      self.contentWindow['canvasSize'] = ( 0, self.maxVirtualSize[0], -self.maxVirtualSize[1],  0)
      self.backgroundColor['frameSize'] = ( 0, self.maxVirtualSize[0], -self.maxVirtualSize[1], 0 )
      # For CityMania Onlue
      self.reset()
      self.center()
  
  def reset(self):
    """Poorly named function that resizes window to fit all contents"""
    self.resize( Vec3(self.maxVirtualSize[0], 0, -self.maxVirtualSize[1]-self.headerHeight), Vec3(0,0,0))

  def center(self):
      """Centers window on screen"""
      self.setPos(-self.maxVirtualSize[0]/2.0, 0, (self.maxVirtualSize[1]+self.headerHeight)/2.0)
  
  def getEntries(self):
        """Returns the fields for any entires"""
        entries = []
        for widget in self.widgets:
            if isinstance(widget, DirectEntry):
                entries.append(widget.get())
        return entries

  def addScrolledList(self, items, numItemsVisible = 4, itemHeight = 1):
        '''Adds a list of items into a scrolled list'''
        scrolled_list = DirectScrolledList(
            decButton_pos= (0.35, 0, 5),
            decButton_text = "Up",
            decButton_borderWidth = (0.005, 0.005),
            
            incButton_pos= (0.35, 0, -5),
            incButton_text = "Down",
            incButton_borderWidth = (0.005, 0.005),
            
            frameSize = (-5, 5, -5, 5),
            frameColor = (1,0,1,0.5),
            pos = (-1, 0, 0),
            items = items,
            numItemsVisible = numItemsVisible,
            forceHeight = itemHeight,
            itemFrame_frameSize = (-5, 5, -5, 5),
            itemFrame_pos = (0.35, 0, 0.4),
            scale = (0.05),
            #parent = (aspect2d),
            )
        scrolled_list.updateFrameStyle()
        self.add([scrolled_list])


class MessageWindow(DirectWindow):
    """
    Generates a "simple" dialogue window with text and an ok button to close.
    A custom button can be passed instead
    """
    def __init__(self, text, button=None, **args):
        DirectWindow.__init__(self, **args)
        self.initialiseoptions(self)
        textBox = DirectLabel(text = text, scale=0.05)
        if not button:
            button = DirectButton(text = "OK", command = self.destroy, scale=0.05)
        self.add([textBox, button])
        self.reset()
        self.center()
        

if __name__ == '__main__':
  # a first window
  window1 = DirectWindow(
      title           = 'window1',
      pos             = ( -.8, .8 ),
      backgroundColor = ( 0, 0, 1, .6),
      borderColor     = ( 1, 0, 0, .6),
      titleColor      = ( 0, 1, 0, .6),
      titleSize       = 0.1,
      borderSize      = 0.1,
    )
  windowContent = DirectButton(text = "Button1", scale=0.5, relief     = DGG.FLAT, frameColor = (0,1,0,1),)
  windowContent2 = DirectButton(text = "B2", scale=0.5, relief     = DGG.FLAT, frameColor = (0,1,0,1),)
  window1.addVertical([windowContent, windowContent2])
  
  # a second window
  window2 = DirectWindow(
      title            = 'window2',
      pos              = ( -.4, .4),
      backgroundColor  = (1,0,0,1),
    )
  windowContent = DirectLabel(text = 'Label1   ', frameColor = (0,1,1,1), scale=0.1)
  windowContent2 = DirectLabel(text = 'L2', frameColor = (0,1,1,1), scale=0.1)
  window2.addHorizontal([windowContent, windowContent2])
  
  # a third window with a close button featuring autoresize
  window3 = DirectWindow(
      title='window3',
      pos = ( 0, 0),
      closeButton=True
    )
  windowContent = DirectButton(
      text = "Press 1 to close me",
      relief     = DGG.FLAT,
      frameColor = (0,1,1,1),
      scale      = 0.05,
    )
  window3.add([windowContent])
  window3.reset()
  
  base.accept('1', window3.destroy)
  
  window4 = MessageWindow(title="message", text="testing")
  
  run()
