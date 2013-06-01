from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from sprites import Lights, cylindar
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

    glClearColor(0., 0., 0., 1.)

    glLight(GL_LIGHT0, GL_AMBIENT, (.2, .2, .2, 1.))
    glLight(GL_LIGHT0, GL_DIFFUSE, (.8, .8, .8, 1.))
    glLight(GL_LIGHT0, GL_SPECULAR, (.2, .2, .2, 1.))
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (.2, .2, .2, 1.))
    
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    
    glLineWidth(2)
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
        self.lightPos = (-50.,-50., 120,  1.)

        self.sprites = []
        self.reshape()

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

    def drawSprites(self):
        for sp in self.sprites:
            glPushMatrix()
            x, y = sp.pos
            glTranslate(x, y, 0)
            sp.draw()
            glPopMatrix()

    def drawReflectedSpritesAndField(self, field):
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
        self.drawSprites()
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

    def mulShadowMatrix(self):
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
        glMultMatrixf(shadowMat)

    def drawShadow(self):
        #draw shadow stencil
        glClearStencil(0)
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE)
        glEnable(GL_STENCIL_TEST)
        glStencilOp(GL_REPLACE, GL_REPLACE, GL_REPLACE)
        glStencilFunc(GL_ALWAYS, 1, 0xffffffff)

        glPushMatrix()
        for sp in self.sprites:
            if not (type(sp) is Lights):
                glPushMatrix()
                x, y = sp.pos
                glTranslate(x, y, 0)
                self.mulShadowMatrix()
                sp.draw()
                glPopMatrix()
        glPopMatrix()

        #draw shadow
        glEnable(GL_STENCIL_TEST)
        glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
        glEnable(GL_DEPTH_TEST)
        glStencilFunc(GL_EQUAL, 1, 0xffffffff)
        glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)

        glColor4f(.0, .0, .0, .8)
        glPushMatrix()
        glScale(1., 1., 0.0001)
        glutSolidCube(1000)
        glPopMatrix()
        glDisable(GL_STENCIL_TEST)

        glEnable(GL_LIGHTING)

    def add(self, sp):
        self.sprites.append(sp)

    def hint(self, text):
        print text
        # self.add(Hint(((100, 100), (300, 100)), text))

    def update(self, field):
        self.sprites = [sp for sp in self.sprites if sp.alive]
        for sp in self.sprites:
            sp.update()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT |\
                    GL_STENCIL_BUFFER_BIT);
        glLoadIdentity()
        gluLookAt(*self.eyePos + self.centerPos + (0., 0., 1.))

        gw, gh = config.GRID_SIZE
        gt = gw + gh
        glTranslate(gw/2., gh/2., 0)
        glScale(gw, gh, gt)
        glLight(GL_LIGHT0, GL_POSITION, self.lightPos)
        
        self.drawShadow()
        self.drawSprites()
        self.drawReflectedSpritesAndField(field)

        #see light location
        #glPushMatrix()
        #glTranslate(self.lightPos[0],self.lightPos[1],
        #            self.lightPos[2])
        #glutSolidCube(0.2)
        #glPopMatrix()

        pygame.display.flip()
        
    def __iter__(self):
        return iter(self.sprites)


