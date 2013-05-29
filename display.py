from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import config
import pygame
from utils import Timer


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

     #glShadeModel(GL_FLAT)
    glShadeModel(GL_SMOOTH)

    glClearColor(0., 0., 0., 1.)

    glLight(GL_LIGHT0, GL_AMBIENT, (.2, .2, .2, 1.))
    glLight(GL_LIGHT0, GL_DIFFUSE, (.6, .6, .6, 1.))
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
        self.lightPos = (5., 5., 0.,  1.)

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
            sp.update()
            glPushMatrix()
            x, y = sp.pos
            glTranslate(x, y, 0)
            sp.draw()
            glPopMatrix()

    def drawReflectedSpritesAndGround(self):
        glDisable(GL_DEPTH_TEST)
        glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE)
        glEnable(GL_STENCIL_TEST)
        glStencilOp(GL_REPLACE, GL_REPLACE, GL_REPLACE)
        glStencilFunc(GL_ALWAYS, 1, 0xffffffff)
        glPushMatrix()
        glScale(1., 1., 0.001)
        glutSolidCube(100)
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
        glColor4f(0, 0.79, 1., .4)
        glPushMatrix()
        glScale(1., 1., 0.001)
        glTranslate(5,5,0)
        glutSolidCube(14)
        glPopMatrix()
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)


    def add(self, sp):
        self.sprites.append(sp)

    def hint(self, text):
        print text
        # self.add(Hint(((100, 100), (300, 100)), text))

    def update(self):
        self.sprites = [sp for sp in self.sprites if sp.alive]

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT |\
                    GL_STENCIL_BUFFER_BIT);
        glLoadIdentity()
        gluLookAt(*self.eyePos + self.centerPos + (0., 0., 1.))

        gw, gh = config.GRID_SIZE
        gt = gw + gh
        glTranslate(gw/2., gh/2., 0)
        glScale(gw, gh, gt)
        glLight(GL_LIGHT0, GL_POSITION, self.lightPos)

        self.drawReflectedSpritesAndGround()
        self.drawSprites()


        #see light location
        glPushMatrix()
        glTranslate(self.lightPos[0],self.lightPos[1],self.lightPos[2])
        glutSolidCube(0.2)
        glPopMatrix()

        pygame.display.flip()


    def __iter__(self):
        return iter(self.sprites)


