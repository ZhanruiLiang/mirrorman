from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import FTGL
from sprites import Lights, cylindar, Item, Mirror
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

    glLight(GL_LIGHT0, GL_AMBIENT, (.5, .5, .5, 1.))
    glLight(GL_LIGHT0, GL_DIFFUSE, (.8, .8, .8, 1.))
    glLight(GL_LIGHT0, GL_SPECULAR, (.5, .5, .5, 1.))
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (.4, .4, .4, 1.))
    #if you want to adjust light intensity, edit here
    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, .1)
    
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

class MenuDisplay(object):
    BG_COLOR = (.3, .3, .3, 1.)
    BTN_COLOR = (.8, .8, .8, 1.)
    SELECTED_COLOR = (.9, .9, .5, 1.)
    FONT_COLOR = (.1, .1, .1, 1.)

    def __init__(self, menuItems):
        self.size = config.SCREEN_SIZE
        w, h = self.size
        self.items = menuItems
        self.selected = None
        self.reshape()

        self.font = FTGL.BitmapFont("FZCCHK.TTF")
        self.font.FaceSize(24, 72)

    def reshape(self):
        w, h = self.size
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, 1, 0, 1)

        glMatrixMode(GL_MODELVIEW)

        glDisable(GL_DEPTH_TEST)
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_LIGHTING)

        glClearColor(*self.BG_COLOR)

    def update(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # glDisable(GL_LIGHTING)
        # glDisable(GL_TEXTURE_2D)

        glLoadIdentity()

        for rect, item in self.rect_items():
            if item is self.selected:
                glColor4d(*self.SELECTED_COLOR)
            else:
                glColor4d(*self.BTN_COLOR)
            glBegin(GL_QUADS)
            x1, y1, x2, y2 = rect
            glVertex2d(x1, y1)
            glVertex2d(x2, y1)
            glVertex2d(x2, y2)
            glVertex2d(x1, y2)
            glEnd()

            #TODO
            glColor4fv((.0, .0, .0, 1,))
            glRasterPos3f ( (x1 + x2) * 2 / 5, (y1 + y2) / 2, 0);
            self.font.Render(item[0])
            #glutBitmapString(GLUT_BITMAP_HELVETICA_18, item[0]);

        pygame.display.flip()

    def rect_items(self):
        x, y = x0, y0 = 0.2, 0.95
        blockW, blockH = 0.6, 0.1
        sep = 0.04
        for item in self.items:
            rect = (x, y - blockH, x + blockW, y)
            yield rect, item
            x, y = x, y - blockH - sep

    def _convert_pos(self, screenPos):
        x, y = screenPos
        w, h = map(float, self.size)
        return x / w, (h - y) / h

    def select(self, pos):
        x, y = self._convert_pos(pos)
        self.selected = None
        for rect, item in self.rect_items():
            if rect[0] <= x <= rect[2] and rect[1] <= y <= rect[3]:
                self.selected = item
                break

    def click(self, pos):
        self.select(pos)
        if self.selected == None: return
        name, func = self.selected
        func()

class Display(object):
    def __init__(self):
        self._cnt = 0
        self.size = config.SCREEN_SIZE

        w, h = self.size
        self.lightPos = (-50.,-50., 150,  1.)

        self.sprites = []
        self.staticSprites = []
        self.reshape()
        self.init_shadow_matrix()

        self.staticDisplayListID = None
        self.camera = None

    def set_camera(self, camera):
        self.camera = camera

    def process_statics(self):
        # sprite in objs[sprite.model.objects[i]]
        objs = {} 
        for sp in self.staticSprites:
            if not sp.model: continue # dummay
            for obj in sp.model.objects.itervalues():
                if obj not in objs: objs[obj] = []
                objs[obj].append(sp)
        #print objs
        self.staticDisplayListID = glGenLists(1)
        glNewList(self.staticDisplayListID, GL_COMPILE)
        for obj, sprites in objs.iteritems():
            material = obj.material
            if material:
                glEnable(GL_TEXTURE_2D)
                glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
                
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
                ox, oy = sp.orient
                glRotated(math.degrees(math.atan2(oy, ox)), 0., 0., 1.)
                glDrawElements(GL_TRIANGLES, n, GL_UNSIGNED_INT, obj.indices)
                glPopMatrix()
        glDisable(GL_TEXTURE_2D)
        glEndList()

    def reshape(self):
        w, h = self.size
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(75, float(w)/h, .1, 5000)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        #self.eyePos = (w * .5, (-0.1) * h, h*(1.0))
        #self.centerPos = (w/2., h/2., 0.)
        

    def draw_sprites(self):
        if self.staticDisplayListID is None:
            self.process_statics()

        glCallList(self.staticDisplayListID)
        mirrorList = []
        for sp in self.sprites:
            if isinstance(sp, Mirror): 
                mirrorList.append(sp)
            else:
                glPushMatrix()
                x, y = sp.pos
                glTranslate(x, y, 0)
                sp.draw()
                glPopMatrix()

        # glDisable(GL_TEXTURE_2D)
        for mirror in mirrorList:
            glPushMatrix()
            x, y = mirror.pos
            glTranslate(x, y, 0)
            mirror.draw()
            glPopMatrix()

    def draw_reflected(self, field):
        #if config.ENABLE_REFLECT: 
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
        #glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glBlendFunc(GL_SRC_COLOR, GL_ONE_MINUS_SRC_COLOR)
        glColor4f(.1, .1, .1, .7)
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

    def draw_shadow(self, field):
        #if not config.ENABLE_SHADOW: return
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
        glDisable(GL_TEXTURE_2D)
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
        field.draw()

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
        self._cnt += 1
        self.sprites = [sp for sp in self.sprites if sp.alive]
        for sp in self.sprites:
            sp.update()
        self.lights.update()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT |
                    GL_STENCIL_BUFFER_BIT)
        glLoadIdentity()
        if self._cnt % 2 == 0:
            self.camera.update()

        gw, gh = config.GRID_SIZE
        gt = (gw + gh)/2
        glTranslate(gw/2., gh/2., 0)
        glScale(gw, gh, gt)
        self.camera.mul_view_matrix()

        glLight(GL_LIGHT0, GL_POSITION, self.lightPos)

        #self.draw_reflected(field)
        self.draw_sprites()
        self.draw_shadow(field)

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
