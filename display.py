from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from sprites import Lights, cylindar, Item
import config
import pygame
import math
from utils import Timer
import utils

def init():
    tm = Timer()
    global screen
    pygame.display.init()

    glutInit()

    screen = pygame.display.set_mode(config.SCREEN_SIZE, 
            pygame.HWSURFACE | pygame.OPENGL | pygame.DOUBLEBUF)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_RESCALE_NORMAL)
    glEnable(GL_TEXTURE_2D)

    glShadeModel(GL_SMOOTH)

    glClearColor(*config.BACK_COLOR)

    glLight(GL_LIGHT0, GL_AMBIENT, (.2, .2, .2, 1.))
    glLight(GL_LIGHT0, GL_DIFFUSE, (.8, .8, .8, 1.))
    glLight(GL_LIGHT0, GL_SPECULAR, (.3, .3, .3, 1.))
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (.2, .2, .2, 1.))
    
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    
    glLineWidth(1)
    glMatrixMode(GL_MODELVIEW)

    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glEnableClientState(GL_TEXTURE_COORD_ARRAY)

    print 'Display init time:', tm.tick()

class Hint(pygame.sprite.Sprite):
    def __init__(self, rect, text):
        pass

class Display(object):
    def __init__(self):
        self.size = config.SCREEN_SIZE

        w, h = self.size
        self.lightPos = (-50.,-50., 150,  1.)

        self.sprites = []
        self.staticSprites = []
        self.reshape()
        self.init_shadow_matrix()

        self.staticDisplayListID = None

    def process_statics(self):
        # sprite in objs[sprite.model.objects[i]]
        objs = {} 
        for sp in self.staticSprites:
            if not sp.model: continue # dummay
            for obj in sp.model.objects.itervalues():
                if obj not in objs: objs[obj] = []
                objs[obj].append(sp)
        print objs
        self.staticDisplayListID = glGenLists(1)
        glNewList(self.staticDisplayListID, GL_COMPILE)
        for obj, sprites in objs.iteritems():
            material = obj.material
            if material:
                glEnable(GL_TEXTURE_2D)
                glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
                
                glMaterialfv(GL_FRONT, GL_AMBIENT, material.ambient)
                glMaterialfv(GL_FRONT, GL_DIFFUSE, material.diffuse)
                glMaterialfv(GL_FRONT, GL_SPECULAR, material.specular)
                glMaterialfv(GL_FRONT, GL_SHININESS, material.shininess)
                glBindTexture(GL_TEXTURE_2D, material.texid)
            else: glDisable(GL_TEXTURE_2D)
            glInterleavedArrays(GL_T2F_N3F_V3F, 0, obj.vdata)
            n = len(obj.indices)
            for sp in sprites:
                glPushMatrix()
                x, y = sp.pos
                glTranslate(x, y, 0)
                glDrawElements(GL_TRIANGLES, n, GL_UNSIGNED_INT, obj.indices)
                glPopMatrix()
        glEndList()

    def reshape(self):
        w, h = self.size
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(75, float(w)/h, .1, 5000)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        self.eyePos = (w * .5, (-0.1) * h, h*(1.0))
        self.centerPos = (w/2., h/2., 0.)

    def draw_sprites(self):
        if self.staticDisplayListID is None:
            self.process_statics()
        glCallList(self.staticDisplayListID)

        for sp in self.sprites:
            glPushMatrix()

            x, y = sp.pos
            glTranslate(x, y, 0)
            sp.draw()

            glPopMatrix()

    def draw_reflected(self, field):
        glClearStencil(0)
        glDisable(GL_DEPTH_TEST)
        glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE)
        glEnable(GL_STENCIL_TEST)
        glStencilOp(GL_REPLACE, GL_REPLACE, GL_REPLACE)
        glStencilFunc(GL_ALWAYS, 1, 0xffffffff)
        glPushMatrix()
        field.draw()
        glPopMatrix()
        glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
        glEnable(GL_DEPTH_TEST)
        glStencilFunc(GL_EQUAL, 1, 0xffffffff)
        glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)

        glPushMatrix()
        glScalef(1.0, 1.0, -1.0)
        glLight(GL_LIGHT0, GL_POSITION, self.lightPos)
        self.draw_sprites()
        glDisable(GL_NORMALIZE)
        glPopMatrix()

        glLight(GL_LIGHT0, GL_POSITION, self.lightPos)
        glDisable(GL_STENCIL_TEST)

        glEnable(GL_BLEND)
        glDisable(GL_LIGHTING)
        glBlendEquation(GL_FUNC_ADD)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glPushMatrix()
        field.draw()
        glPopMatrix()
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)

    def init_shadow_matrix(self):
        l = list(self.lightPos)
        factor = math.sqrt(l[0]**2 + l[1]**2 + l[2]**2)
        l[0] /= factor
        l[1] /= factor
        l[2] /= factor
        l[3] = 0
        n = (0, 0, 1, 0)
        dot = l[0]*n[0] + l[1]*n[1] + l[2]*n[2] + l[3]*n[3]
        shadowMat = [dot-l[0]*n[0],-l[1]*n[0],-l[2]*n[0],-l[3]*n[0],
                     -l[0]*n[1],dot-l[1]*n[1],-l[2]*n[1],-l[3]*n[1],
                     -l[0]*n[2],-l[1]*n[2],dot-l[2]*n[2],-l[3]*n[2],
                     -l[0]*n[3],-l[1]*n[3],-l[2]*n[3],dot-l[3]*n[3]]
        self.shadowMat = utils.convert_ctypes(
            shadowMat, ctypes.c_float, (len(shadowMat), ))

    def draw_shadow(self):
        #draw shadow stencil
        glClearStencil(0)
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE)
        glEnable(GL_STENCIL_TEST)
        # print 'glIsEnabled(GL_STENCIL_TEST)', glIsEnabled(GL_STENCIL_TEST)
        glStencilOp(GL_REPLACE, GL_REPLACE, GL_REPLACE)
        glStencilFunc(GL_ALWAYS, 1, 0xffffffff)

        glPushMatrix()
        glMultMatrixf(self.shadowMat)
        for sp in self.sprites:
            if not isinstance(sp, Lights):
                glPushMatrix()
                x, y = sp.pos
                glTranslate(x, y, 0)
                sp.draw()
                glPopMatrix()
        glPopMatrix()

        #draw shadow
        glEnable(GL_STENCIL_TEST)
        glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
        glEnable(GL_DEPTH_TEST)
        glStencilFunc(GL_EQUAL, 1, 0xffffffff)
        glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)

        glColor4f(*config.SHADOW_COLOR)
        glPushMatrix()
        glScale(1., 1., 0.0001)
        glutSolidCube(1000)
        glPopMatrix()
        glDisable(GL_STENCIL_TEST)

        glEnable(GL_LIGHTING)

    def add(self, sp):
        if isinstance(sp, Lights):
            self.lights = sp
        elif sp.moveable:
            self.sprites.append(sp)
        else:
            self.staticSprites.append(sp)

    def hint(self, text):
        print text
        # self.add(Hint(((100, 100), (300, 100)), text))

    def update(self, field):
        self.sprites = [sp for sp in self.sprites if sp.alive]
        for sp in self.sprites:
            sp.update()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT |
                    GL_STENCIL_BUFFER_BIT)
        glLoadIdentity()
        gluLookAt(*self.eyePos + self.centerPos + (0., 0., 1.))

        gw, gh = config.GRID_SIZE
        gt = (gw + gh)/2
        glTranslate(gw/2., gh/2., 0)
        glScale(gw, gh, gt)
        glLight(GL_LIGHT0, GL_POSITION, self.lightPos)
        
        # self.draw_shadow()
        self.draw_sprites()
        self.draw_reflected(field)

        # draw lights
        glPushMatrix()
        # glTranslate(0, 0, 0)
        self.lights.draw()
        glPopMatrix()

        #see light location
        #glPushMatrix()
        #glTranslate(self.lightPos[0],self.lightPos[1],
        #            self.lightPos[2])
        #glutSolidCube(0.2)
        #glPopMatrix()

        pygame.display.flip()
