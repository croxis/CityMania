# -*- coding: utf-8 -*-
'''All this code comes from the awesome demomaster by clcheung
http://www.panda3d.org/phpbb2/viewtopic.php?t=5915
'''

from pandac.PandaModules import Filename, CardMaker
from pandac.PandaModules import NodePath, WindowProperties,TextureStage, Texture
from pandac.PandaModules import Vec3,Vec4,Point3
from pandac.PandaModules import Plane
from pandac.PandaModules import PlaneNode
from pandac.PandaModules import PStatClient
from pandac.PandaModules import CullFaceAttrib
from pandac.PandaModules import RenderState
from pandac.PandaModules import ShaderAttrib, TransparencyAttrib

class Att_base():
    def __init__(self, fReadOnly, name=None, NodeName=None):
        self.fReadOnly = fReadOnly
        if name == None:
            name = "Value"
        self.name = name
        self.NodeName = NodeName

    def getNodeName(self):
        if self.NodeName == None:
            return self.name
        return self.NodeName

    def setNotifier(self, notifier):
        self.notifier = notifier

    def notify(self):
        if hasattr(self,'notifier') and inspect.isroutine(self.notifier):
            self.notifier(self)

class WaterNode(Att_base):
    def __init__(self, x1, y1, x2, y2, z):
        Att_base.__init__(self, False, "Water1")
        # Water surface
        maker = CardMaker( 'water' )
        maker.setFrame( x1, x2, y1, y2 )

        self.waterNP = render.attachNewNode(maker.generate())
        self.waterNP.setHpr(0,-90,0)
        self.waterNP.setPos(0,0,z)
        self.waterNP.setTransparency(TransparencyAttrib.MAlpha )
        self.waterNP.setShader(loader.loadShader( 'Shaders/water1.sha' ))

        # Reflection plane
        self.waterPlane = Plane( Vec3( 0, 0, z+1 ), Point3( 0, 0, z ) )

        planeNode = PlaneNode( 'waterPlane' )
        planeNode.setPlane( self.waterPlane )

        # Buffer and reflection camera
        self.buffer = base.win.makeTextureBuffer( 'waterBuffer', 512, 512 )
        self.buffer.setClearColor( Vec4( 0, 0, 0, 1 ) )

        cfa = CullFaceAttrib.makeReverse( )
        rs = RenderState.make(cfa)

        self.watercamNP = base.makeCamera( self.buffer )
        self.watercamNP.reparentTo(render)

        sa = ShaderAttrib.make()
        sa = sa.setShader(loader.loadShader('Shaders/splut3Clipped.sha') )

        self.cam = self.watercamNP.node()
        self.cam.getLens( ).setFov( base.camLens.getFov( ) )
        self.cam.getLens().setNear(1)
        self.cam.getLens().setFar(5000)
        self.cam.setInitialState( rs )
        self.cam.setTagStateKey('Clipped')
        self.cam.setTagState('True', RenderState.make(sa))


        # ---- water textures ---------------------------------------------

        # reflection texture, created in realtime by the 'water camera'
        tex0 = self.buffer.getTexture( )
        tex0.setWrapU(Texture.WMClamp)
        tex0.setWrapV(Texture.WMClamp)
        ts0 = TextureStage( 'reflection' )
        self.waterNP.setTexture( ts0, tex0 )

        # distortion texture
        tex1 = loader.loadTexture('Textures/water.png')
        ts1 = TextureStage('distortion')
        self.waterNP.setTexture(ts1, tex1)


    def Destroy(self):
        base.graphicsEngine.removeWindow(self.buffer)
        self.cam.setInitialState(RenderState.makeEmpty())
        self.watercamNP.removeNode()
        self.waterNP.clearShader()
        self.waterNP.removeNode()

    def setParams(self, offset, strength, refractionfactor, refractivity, vx, vy, scale):
        self.waterNP.setShaderInput('waterdistort', Vec4( offset, strength, refractionfactor, refractivity ))
        self.waterNP.setShaderInput('wateranim', Vec4( vx, vy, scale, 0 )) # vx, vy, scale, skip

    def changeCameraPos(self, pos, mc=None):
        if mc != None:
            # update matrix of the reflection camera
            mf = self.waterPlane.getReflectionMat( )
            self.watercamNP.setMat(mc * mf)

    def changeParams(self, object):
        self.setParams(self.att_offset.v,self.att_strength.v,self.att_refractionfactor.v,self.att_refractivity.v,
                self.att_vx.v, self.att_vy.v, self.att_scale.v)

    def setStandardControl(self):
        self.att_offset = Att_FloatRange(False, "Water:Offset", 0.0, 1.0, 0.4)
        self.att_strength = Att_FloatRange(False, "Water:Strength", 0.0, 100.0, 4)
        self.att_refractionfactor = Att_FloatRange(False, "Water:Refraction Factor", 0.0, 1.0, 0.2)
        self.att_refractivity = Att_FloatRange(False, "Water:Refractivity", 0.0, 1.0, 0.45)
        self.att_vx = Att_FloatRange(False, "Water:Speed X", -1.0, 1.0, 0.1)
        self.att_vy = Att_FloatRange(False, "Water:Speed Y", -1.0, 1.0, -0.1)
        self.att_scale = Att_FloatRange(False, "Water:Scale", 1.0, 200.0, 64.0,0)
        self.att_offset.setNotifier(self.changeParams)
        self.att_strength.setNotifier(self.changeParams)
        self.att_refractionfactor.setNotifier(self.changeParams)
        self.att_refractivity.setNotifier(self.changeParams)
        self.att_vx.setNotifier(self.changeParams)
        self.att_vy.setNotifier(self.changeParams)
        self.att_scale.setNotifier(self.changeParams)
        self.changeParams(None)


    def hide(self):
        self.waterNP.hide()

    def show(self):
        self.waterNP.show()

    def setFov(self, fov):
        # the reflection cam has to follow the base.cam fov
        self.cam.getLens().setFov(fov)

    def setCubeMap(self, cubemapfile):
        pass


class Att_NumRange(Att_base):
    def __init__(self, fReadOnly, name, fInteger, minv, maxv, default, NodeName):
        Att_base.__init__(self, fReadOnly, name, NodeName)
        self.fInteger = fInteger
        self.minv = minv
        self.maxv = maxv
        self.v = default
        self.default = default

    def fix(self):
        if self.minv != self.maxv:
            self.v = max(self.v, self.minv)
            self.v = min(self.v, self.maxv)

    def update(self, v):
        if self.fReadOnly:
            return
        if self.fInteger:
            v = int(v)
        else:
            v = float(v)
        if self.minv >= self.maxv or (v <= self.maxv and v >= self.minv):
            self.v = v
        self.notify()


class Att_FloatRange(Att_NumRange):
    def __init__(self, fReadOnly, name, minv, maxv, default, precision=2,NodeName=None):
        Att_NumRange.__init__(self,fReadOnly, name, False, minv, maxv, default,NodeName=NodeName)
        self.precision = precision

# Does this belong in water.py? Nevar!
class SkyDome2(Att_base):
    def __init__(self, scene, rate=Vec4(0.004, 0.002, 0.008, 0.010),
                skycolor=Vec4(0.25, 0.5, 1, 0),
                texturescale=Vec4(1,1,1,1),
                scale=(4000,4000,1000),
                texturefile=None):
        Att_base.__init__(self,False, "Sky Dome 2")
        self.skybox = loader.loadModel("Models/dome2")
        self.skybox.reparentTo(scene)
        self.skybox.setScale(scale[0],scale[1],scale[2])
        self.skybox.setLightOff()

        if texturefile == None:
            texturefile = "Textures/clouds_bw.png"
        texture = loader.loadTexture(texturefile)
        self.textureStage0 = TextureStage("stage0")
        self.textureStage0.setMode(TextureStage.MReplace)
        self.skybox.setTexture(self.textureStage0,texture,1)
        #self.skybox.setTexScale(self.textureStage0, texturescale[0], texturescale[1])

        self.rate = rate
        self.textureScale = texturescale
        self.skycolor = skycolor
        self.skybox.setShader( loader.loadShader( 'Shaders/skydome2.sha' ) )
        self.setShaderInput()

    def setRate(self, rate):
        self.rate = rate

    def setTextureScale(self, texturescale):
        self.skybox.setTexScale(self.textureStage0, texturescale[0], texturescale[1])

    def Destroy(self):
        self.skybox.clearShader()
        self.skybox.removeNode()

    def setPos(self, v):
        self.skybox.setPos(v)

    def show(self):
        self.skybox.show()

    def hide(self):
        self.skybox.hide()

    def setStandardControl(self):
        self.att_rate = Att_Vecs(False,"Cloud Speed",4,self.rate,-1,1,3)
        self.att_scale = Att_Vecs(False, "Tex-scale", 4, self.textureScale, 0.01, 100.0, 2)
        self.att_skycolor = Att_color(False, "Sky Color", self.skycolor)
        self.att_rate.setNotifier(self.changeParams)
        self.att_scale.setNotifier(self.changeParams)
        self.att_skycolor.setNotifier(self.changeParams)

    def changeParams(self, object):
        self.rate = self.att_rate.getValue()
        self.skycolor = self.att_skycolor.getColor()
        self.textureScale = self.att_scale.getValue()
        self.setShaderInput()

    def setShaderInput(self):
        self.skybox.setShaderInput("sky", self.skycolor)
        self.skybox.setShaderInput("clouds", self.rate)
        self.skybox.setShaderInput("ts", self.textureScale)


class Att_Vecs(Att_base):
    def __init__(self, fReadOnly, name, l, vec, minv, maxv, precision=2, NodeName=None):
        Att_base.__init__(self, fReadOnly, name, NodeName=NodeName)
        self.l = l
        self.minv = minv
        self.maxv = maxv
        self.fInteger = False
        self.precision = precision
        self.vec = []
        self.default = []
        for i in range(l):
            v = Att_FloatRange(fReadOnly, "%d" % (i+1), minv, maxv, vec[i], precision)
            v.setNotifier(self.update)
            self.vec.append(v)
            self.default.append(vec[i])

    def fix(self):
        for i in range(self.l):
            self.vec[i].fix()

    def setValue(self, v):
        if isinstance(v, Att_Vecs):
            for i in range(self.l):
                self.vec[i].v = v.vec[i].v
        else:
            for i in range(self.l):
                self.vec[i].v = v[i]
        self.fix()

    def update(self, object):
#        if hasattr(self,'notifier') and inspect.isroutine(self.notifier):
#            self.notifier(self)
        self.notify()

    def getListValue(self):
        return self.getValue(True)

    def getValue(self, forcevector=False):
        if not forcevector:
            if self.l == 3:
                return Vec3(self.vec[0].v,self.vec[1].v,self.vec[2].v)
            elif self.l == 4:
                return Vec4(self.vec[0].v,self.vec[1].v,self.vec[2].v,self.vec[3].v)

        ret = []
        for i in range(self.l):
            ret.append(self.vec[i].v)
        return ret

def Color2RGB(c):
    return (int(c[0] * 255),int(c[1] * 255),int(c[2] * 255))
def RGB2Color(rgb,alpha=1):
    return Vec4(float(float(rgb[0]) / 255.0),float(rgb[1] / 255.0),float(rgb[2] / 255.0),alpha)

class Att_color(Att_base):
    def __init__(self, fReadOnly, name, color):
        if name == None:
            name = "Color"
        Att_base.__init__(self, fReadOnly, name)
        self.color = color

    def getRGBColor(self):
        return Color2RGB(self.color)

    def getColor(self):
        return self.color

    def setRGBColor(self,rgb):
        if self.fReadOnly:
            return
        self.color = RGB2Color(rgb)
        self.notify()

    def setColor(self,c):
        if self.fReadOnly:
            return
        self.color = c
        self.notify()
