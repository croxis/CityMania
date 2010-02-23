 
"""
boxes.py

A partial implementation of the theory of packing boxes (for laying out
objects in two dimensions, although it could easily be extended to 3D)
from GTK+. This framework can be used to layout any NodePath or
DirectGui object.

Theory Of Packing Boxes
-----------------------

From GTK+. Boxes are invisible GUI widgets into which you pack other
widgets to achieve a desired layout. In a horizontal box (hbox) objects
are packed from left to right or right to left. In a vertical box (vbox)
objects are packed from top to bottom or bottom to top. You can pack
objects in both directions in the same box at the same time by using the
two different pack methods. Options control whether objects are packed
as tightly possible, or whether the objects are spread out to fill the
amount of space alloted to the box, etc.

Finally, a table is a type of box that manages a number of cells in rows
and columns. Objects are packed into the cells. A single object can
occupy multiple cells. When packing an object, you specify the range of
cells it will occupy by specifying left, right, bottom, and top cells.

What's implemented so far:

* hboxes with packing from left to right.
* vboxes with packing from top to bottom.
* You can pack boxes into boxes in any combination. Except that you
  cannot pack a box into itself.

Todo:

* Support packing in both directions.
* Option to pack objects tightly or space them out to fill a given
  width.
* Vertical alignment option for hboxes and horizontal alignment option
  for vboxes.
* Table box class.
* Refactor. Box should extend NodePath rather than DirectFrame, and
  should emulate a Python container class.

"""
from pandac.PandaModules import *
from direct.gui.DirectGui import *

# We want our layout containers to be able to contain DirectGUI
# objects as well as NodePaths. The problem: we rely on
# NodePath.getTightBounds(), which returns the bounds of the object
# relative to its parent node. But with DirectGUI objects,
# getTightBounds() just returns (Point3(0,0,0),Point3(0,0,0). So
# we would like to write a wrapper class for DirectGUI objects, but
# which class do we extend? We want a class that is able to extend
# any DirectGUI object. We need to use mixins!
#
# (A mixin is a class that derives from an interface or abstract class,
# so that at run time it may extend any concrete class that implements
# a particular interface. Since Python has no explicit support for
# either interfaces or abstract classes, a Python implementation of
# mixins is a bit more informal than one in Java or C.)
#
def mixin(pyClass, mixInClass):
    """Append mixInClass to the front of the inheritance path of
    pyClass. This alters the behaviour of pyClass at runtime.
       
    This little function implements mixins in Python by adding a
    new class into the inheritance path of a class at runtime. Because
    mixInClass is added to the front of the inheritance path, methods in
    mixInClass will override methods in any other class that pyClass
    derives from (but they will not override methods in pyClass itself,
    although you could also implement mixins like that if you wanted).
   
    """
    if mixInClass not in pyClass.__bases__:
        pyClass.__bases__ = (mixInClass,) + pyClass.__bases__

class Mixin_DirectGuiFix():
    """A class for mixing-in with DirectGUI classes, that overrides
    the behaviour of getTightBounds() to make it consistent with
    NodePath.
   
    To support mixing with this class, a class must have a getBounds()
    method that returns four floats (l,r,b,t), the bounds of the object
    in the objects own coordinate space. All the DirectGUI widgets
    implement this interface.
   
    Since getTightBounds() is useless as is (it always returns a bunch
    of zeros), it should not cause any problem to override its behaviour
    at the class level at runtime. (Surely no one could be making use of
    an apparently useless method?)
   
    """
    def getTightBounds(self):
        # With DirectGUI classes, getBounds() returns four floats,
        # apparently in the coordinate space of the object itself. We
        # translate this into the (Point3,Point3) format and translate
        # the values into the coordinate space of the parent.
        # FIXME: This is not the correct way to translate between
        # coordinate spaces!
        l,r,b,t = self.getBounds()
        l *= self.getScale().getX()
        l += self.getPos().getX()
        r *= self.getScale().getX()
        r += self.getPos().getX()
        b *= self.getScale().getZ()
        b += self.getPos().getZ()
        t *= self.getScale().getZ()
        t += self.getPos().getZ()
        return (Point3(l,0,b),Point3(r,0,t))

# Apply our mixin class to a few DirectGui classes that we will use
# later. You need to do this for every DirectGui class you're gonna use,
# so should probably do it for all of them right here.
mixin(DirectLabel,Mixin_DirectGuiFix)
mixin(DirectEntry,Mixin_DirectGuiFix)
mixin(DirectButton,Mixin_DirectGuiFix)

# FIXME: I don't see any point in Box inheriting from DirectFrame
# anymore and it's starting to get in the way (e.g. Box can't emulate a
# Python container class because DirectFrame is already abusing those
# methods). Should inherit from NodePath instead to get methods like
# setPos, getPos, getTightBounds, reparentTo, etc. that Box uses, but
# this will require some refactoring work. (In theory Box shouldn't need
# to maintain its own bounds as NodePath does this correctly.)
class Box(DirectFrame):
    """
    Base class for HBox and VBox. Not meant to be instantiated itself.
   
    """
   
    def __init__(self,**args):
        """Initialise the Box. **args is just passed to the DirectFrame
        initialiser.
       
        """
        DirectFrame.__init__(self, **args)
        self.initialiseoptions(Box)

        # We maintain our own list of objects packed into this box,
        # rather than reusing the scene graph. This means we don't have
        # to capture new children that are added to this node in the
        # scene graph using (for example) reparentTo, and it means that
        # users can add children to this node without them being packed
        # into the box, which might be useful.
        self._objects = []
       
        # DirectFrame does not appear to maintain its bounds in any
        # useful way  so we maintain our own bounds in the same
        # format used by NodePath.
        self._tightBounds = (Point3(0,0,0),Point3(0,0,0))

    # Some convenience methods for dealing with this annoying bounds
    # structure. This is a humane API!
    def bottom_left(self):
        return self._tightBounds[0]       
    def top_right(self):
        return self._tightBounds[1]
    def left(self):
        return self.bottom_left().getX()   
    def right(self):
        return self.top_right().getX()   
    def bottom(self):
        return self.bottom_left().getZ()   
    def top(self):
        return self.top_right().getZ()   
    def set_left(self,left):
        self.bottom_left().setX(left)
    def set_right(self,right):
        self.top_right().setX(right)
    def set_bottom(self,bottom):
        self.bottom_left().setZ(bottom)
    def set_top(self,top):
        self.top_right().setZ(top)

    def __len__(self):
        return len(self._objects)
    # We would like to emulate a Python container type but DirectFrame
    # is already using those methods so we stay away from them.   
    def get(self,key):
        return self._objects[key]
    # Todo: implement set(self,key,value), del(self,key) and
    # __iter__(self)

    # This is for compatibility with NodePath behaviour.
    def getTightBounds(self):
        """Return the tight bounds of this object relative to its'
        parent node."""
        
        #bounds = self.node().getFrame() #also try parent['frameSize']
        #for c in parent.getChildren():
        #    cB = getWidgetsBounds(c)
        #    bounds.setX(min(cB[0],bounds[0])) #L
        #    bounds.setY(max(cB[1],bounds[1])) #R
        #    bounds.setZ(min(cB[2],bounds[2])) #B
        #    bounds.setW(max(cB[3],bounds[3])) #T
        #return bounds
       
        # FIXME: Err... this is not the correct way to translate to the
        # parent nodes coordinate space. It doesn't even account for
        # scale!
        return (self.bottom_left()+self.getPos(),self.top_right()+self.getPos())

    def pack(self,obj):
        """
        Pack a new object into this box.
       
        Box.pack handles updating the bounds of the box, appending the
        new object to the list of packed objects, and updating the scene
        graph. It calls layout() to allow the new object to be
        positioned, subclasses should override layout to implement
        different layouts.
       
        """
        # First reparent the object to the box in the scene graph, so
        # that values it returns are relative to the box.
        obj.reparentTo(self)
       
        # Give derived classes a chance to position the new object.
        self.layout(obj)

        # Get the bounds of the new object.
        bottom_left,top_right = obj.getTightBounds()
        left = bottom_left.getX()
        right = top_right.getX()
        bottom = bottom_left.getZ()
        top = top_right.getZ()
        # Update the bounds of this box to encompass the new object.
        if left < self.left(): self.set_left(left)
        if right > self.right(): self.set_right(right)
        if bottom < self.bottom(): self.set_bottom(bottom)
        if top > self.top(): self.set_top(top)

        # Add the object to the list of packed objects.
        self._objects.append(obj)
   
    def layout(self,obj):
        """
        Position a new object that is being packed into this box.
        Subclasses should override this method to implement their
        own layouts.
       
        """
        pass
       
class HBox(Box):
    """
    A horizontal container. Objects that are packed into this box will
    be layed out along a horizontal line.
   
    """

    def __init__(self,margin=0,**args):
        """Initialise the hbox. margin specifies a horizontal gap
        between each object and the next in the box. **args is passed
        straight to Box.
       
        """
        self.margin = margin
        Box.__init__(self,**args)
           
    def layout(self,obj):
        """
        Align the left side of the new object with the right side of
        the last packed object, and align the top of the new object
        with the top of the last packed object.       
                   
        """             
        if self._objects == []:
            # This is the first object to be packed. Align it with
            # this empty box.
            right = self.right()
            top = self.top()
        else:
            # Align the new object with the last object that was
            # packed.
            last = self._objects[-1]
            bottom_left,top_right = last.getTightBounds()
            right = top_right.getX()
            top = top_right.getZ()

        # Align the left of the new object with `right`.
        bottom_left,top_right = obj.getTightBounds()       
        left = bottom_left.getX()
        distance = right - left
        obj.setPos(obj.getPos() + Point3(distance,0,0))
       
        # Align the top of the new object with `top`.
        t = top_right.getZ()
        distance = top - t
        obj.setPos(obj.getPos() + Point3(0,0,distance))
       
        obj.setPos(obj.getPos() + Point3(self.margin,0,0))
       
class VBox(Box):
    """
    A vertical container. Objects that are packed into this box will
    be layed out along a vertical line.
   
    """

    def __init__(self,margin=0,**args):
        """Initialise the vbox. margin specifies a vertical gap
        between each object and the next in the box. **args is passed
        straight to Box.
       
        """
        self.margin = margin
        Box.__init__(self,**args)
               
    def layout(self,obj):
        """
        Align the top side of the new object with the bottom side of
        the last packed object, and align the left of the new object
        with the left of the last packed object.       
                   
        """
        if self._objects == []:
            # This is the first object to be packed. Align it with
            # this empty box.
            bottom = self.bottom()
            left = self.left()
        else:
            # Align the new object with the last object that was
            # packed.
            last = self._objects[-1]
            bottom_left,top_right = last.getTightBounds()
            bottom = bottom_left.getZ()
            left = bottom_left.getX()

        # Align the top of the new object with `bottom`.
        bottom_left,top_right = obj.getTightBounds()       
        top = top_right.getZ()
        distance = bottom - top
        obj.setPos(obj.getPos() + Point3(0,0,distance))

        # Align the left of the new object with `left`.
        l = bottom_left.getX()
        distance = left - l
        obj.setPos(obj.getPos() + Point3(distance,0,0))
       
        obj.setPos(obj.getPos() + Point3(0,0,-self.margin))
   
if __name__== '__main__' :
    """
    For the test we make a grid of different-coloured cards by packing 4
    cards each into 6 vboxes, and packing the vboxes into an hbox. We
    also put an hbox on each card and pack some DirectGUI objects into
    it.
   
    """     
    import direct.directbase.DirectStart
    from random import random

    # Use the CardMaker to generate some nodepaths for flat,
    # card-like geometry.
    cm = CardMaker('cm')
    left,right,bottom,top = 0,2,0,-2
    width = right - left
    height = top - bottom
    cm.setFrame(left,right,bottom,top)

    hbox = HBox(margin=.05)
    hbox.setPos(-1.2,0,0.9)
    for i in range(5):       
        vbox = VBox(margin=.05)
        for j in range(4):       
            np = aspect2d.attachNewNode(cm.generate())
            np.setScale(.2)
            np.setColor(random(),random(),random())
            another_vbox = VBox(margin=.05)
            dl = DirectLabel(text="I'm a label, look at me!",scale=.2)
            another_vbox.pack(dl)
            de = DirectEntry(initialText="I'm a text entry, write on me!",scale=.2,width=4,numLines=4)
            another_vbox.pack(de)
            db = DirectButton(text="I'm a button, click me!",scale=.2,relief=None)
            another_vbox.pack(db)
            another_vbox.reparentTo(np)
            vbox.pack(np)       
        hbox.pack(vbox)
         
    run() 
