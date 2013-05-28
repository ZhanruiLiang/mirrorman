from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import config
import pygame
from utils import Timer


def init():
    pygame.display.init()

    glutInit()

class Hint(pygame.sprite.Sprite):
    def __init__(self, rect, text):
        pass

class Display(object):
    def __init__(self,fieldSize):
        tm = Timer()
        self.size = config.SCREEN_SIZE
        self.fieldSize = fieldSize
        self.screen = pygame.display.set_mode(config.SCREEN_SIZE, 
                pygame.HWSURFACE | pygame.OPENGL | pygame.DOUBLEBUF)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_RESCALE_NORMAL)
        glEnable(GL_TEXTURE_2D)


        #glEnable(GL_COLOR_MATERIAL)
        #glColorMaterial(GL_FRONT,GL_AMBIENT_AND_DIFFUSE)

        glClearColor(1., 1., 1., 1.)

        #glShadeModel(GL_FLAT)
        glShadeModel(GL_SMOOTH)

        # glMaterial(GL_FRONT, GL_AMBIENT, (0.8, 0.8, 0.8, 1.0))    
        # glMaterial(GL_FRONT, GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0))

        # glEnable(GL_BLEND)
        # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glLight(GL_LIGHT0, GL_AMBIENT, (.2, .2, .2, 1.))
        glLight(GL_LIGHT0, GL_DIFFUSE, (.6, .6, .6, 1.))
        glLight(GL_LIGHT0, GL_SPECULAR, (.2, .2, .2, 1.))
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (.2, .2, .2, 1.))
        
        w, h = self.size
        fieldw, fieldh = self.fieldSize
        self.lightPos = (float(fieldw)/2, float(fieldh)/2, 15, 1.)


        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        
        glLineWidth(2)
        self.reshape()
        glMatrixMode(GL_MODELVIEW)

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)

        self.sprites = []
        print 'Display init time:', tm.tick()

    def reshape(self):
        w, h = self.size
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(75, float(w)/h, .1, 5000)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        self.eyePos = (w * .5, (-0.3) * h, h*(1.2))
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
        glTranslate(self.lightPos[0],self.lightPos[1],self.lightPos[2])
        glutSolidCube(0.2)
        glPopMatrix()
        glLight(GL_LIGHT0, GL_POSITION, self.lightPos)
        pygame.display.flip()


    def __iter__(self):
        return iter(self.sprites)


