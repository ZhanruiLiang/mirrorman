from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import config
import pygame

def init():
    # glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    pygame.display.init()
    # pygame.init()

    glutInit()

class Hint(pygame.sprite.Sprite):
    def __init__(self, rect, text):
        pass

class Display(object):
    def __init__(self):
        self.size = config.SCREEN_SIZE

        self.screen = pygame.display.set_mode(config.SCREEN_SIZE, 
                pygame.HWSURFACE | pygame.OPENGL | pygame.DOUBLEBUF)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)

        glClearColor(1., 1., 1., 1.)

        glShadeModel(GL_FLAT)
        # glShadeModel(GL_SMOOTH)

        glMatrixMode(GL_MODELVIEW)
        # glMaterial(GL_FRONT, GL_AMBIENT, (0.8, 0.8, 0.8, 1.0))    
        # glMaterial(GL_FRONT, GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0))
        self.reshape()
        glLineWidth(2)

        # glEnable(GL_BLEND)
        # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        k = .5
        glLight(GL_LIGHT0, GL_AMBIENT, (k, k, k, 1.))
        # glLight(GL_LIGHT0, GL_DIFFUSE, (.9, .9, .9, .7))

        self.sprites = []

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
        self.lightPos = (0., 0., h * 2.)

        glLight(GL_LIGHT0, GL_POSITION, self.lightPos)

    def add(self, sp):
        self.sprites.append(sp)

    def hint(self, text):
        print text
        # self.add(Hint(((100, 100), (300, 100)), text))

    def update(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
        glLoadIdentity()
        gluLookAt(*self.eyePos + self.centerPos + (0., 0., 1.))

        glLight(GL_LIGHT0, GL_POSITION, self.lightPos)
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
        pygame.display.flip()
        self.sprites = [sp for sp in self.sprites if sp.alive]

    def __iter__(self):
        return iter(self.sprites)
