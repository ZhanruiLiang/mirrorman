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

    glClearColor(1., 1., 1., 1.)

    #glShadeModel(GL_FLAT)
    glShadeModel(GL_SMOOTH)

    # glEnable(GL_BLEND)
    # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

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


    def add(self, sp):
        self.sprites.append(sp)

    def hint(self, text):
        print text
        # self.add(Hint(((100, 100), (300, 100)), text))

    def update(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
        glLoadIdentity()
        gluLookAt(*self.eyePos + self.centerPos + (0., 0., 1.))

        glPushMatrix()
        gw, gh = config.GRID_SIZE
        gt = gw + gh
        glTranslate(gw/2., gh/2., 0)
        glScale(gw, gh, gt)

        for sp in self.sprites:
            if sp.alive:
                sp.update()
                glPushMatrix()
                x, y = sp.pos
                glTranslate(x, y, 0)
                sp.draw()
                glPopMatrix()

        self.sprites = [sp for sp in self.sprites if sp.alive]

        #see light location
        glPushMatrix()
        glLight(GL_LIGHT0, GL_POSITION, self.lightPos)
        glTranslate(*self.lightPos[:3])
        glColor3d(.5, .5, .0)
        glutSolidCube(0.2)
        glPopMatrix()

        glPopMatrix()

        pygame.display.flip()

    def __iter__(self):
        return iter(self.sprites)


