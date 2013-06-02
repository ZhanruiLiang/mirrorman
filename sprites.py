import pygame
import math
from config import GRID_SIZE, FPS
from OpenGL.GL import *
from OpenGL.GLUT import *
from objReader import Model
from animation import Animation
import shapes

__meta__ = type

cylindar = shapes.cylindarShape()

def alpha(color, a):
    if len(color) == 3:
        r, g, b = color
    else:
        r, g, b, _ = color
    return (r, g, b, a)

def glcolor(r, g, b, a):
    return float(r)/255., float(g)/255., float(b)/255., float(a)/255.

class Sprite(object):
    """
    pos
    alive

    draw()
    update()
    kill()
    """
    def __init__(self, pos=(0, 0)):

        self.pos = pos
        self.alive = True

    def update(self):
        pass

    def draw(self):
        pass

class Item(Sprite):
    """
    pos
    orient
    reflective
    moveable
    dieTime
    restTime

    """
    color = glcolor(154, 189, 225, 255)
    reflective = False
    moveable = True
    dieTime = 10
    field = None

    def __init__(self, pos=(0, 0), orient=(1, 0)):
        super(Item, self).__init__(pos)
        self.orient = orient
        self.restTime = None

    def move(self, direction):
        x, y = self.pos
        dx, dy = direction
        self.pos = x, y = x + dx, y + dy

    def kill(self):
        self.alive = False

    @property
    def dying(self):
        return self.restTime is not None

    def die(self):
        if not self.dying:
            self.restTime = self.dieTime

    def update2(self):
        if self.dying:
            self.restTime -= 1
            if self.restTime == 0:
                self.kill()
                self.field.remove_sprite(self)

    def setMaterial(self, color):
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, color)
        glMaterialfv(GL_FRONT, GL_SPECULAR, color)
        glMaterialf(GL_FRONT, GL_SHININESS, .5)

    def draw(self):
        glTranslate(0, 0, .5)
        glScalef(0.8,0.8,1)
        if self.dying:
            if self.restTime % 2:
                color = self.color
            else:
                color = (.3, .2, .2, .2)
        else:
            color = self.color
        self.setMaterial(color)
        cylindar.draw()

class AnimatedItem(Item):
    def __init__(self, modelName, pos=(0, 0), orient=(1, 0)):
        super(AnimatedItem, self).__init__(pos, orient)
        self.animations = {}
        self.animation = None
        self.model = Model(modelName+'.obj')

    def load_animation(self, aniName):
        ani = Animation(aniName+'.ani', self.model)
        self.animations[aniName] = ani
        if not self.animation:
            self.animation = ani

    def update(self):
        super(AnimatedItem, self).update()
        self.animation.step()

    def draw(self):
        self.model.draw()

class Player(AnimatedItem):
    color = glcolor(69, 161, 17, 0xff)

    def __init__(self, pos=(0, 0), orient=(1, 0)):
        super(Player, self).__init__('robot', pos, orient)
        self.load_animation('walk')

    def move(self, direction):
        dx, dy = direction
        self.orient = (dx, dy)
        super(Player, self).move(direction)

class Mirror(Item):
    color = glcolor(168, 255, 235, 0xff)
    reflective = True

    def draw(self):
        angle = math.degrees(math.atan2(self.orient[1], self.orient[0]))

        # draw mirror base
        self.setMaterial((.2,.0,.0,.5))
        #glColor4f(0., 0., 0., 0.)
        glPushMatrix()
        glTranslate(.0, .0, .1)
        glScale(1., 1., .2)
        glutSolidCube(1)
        glPopMatrix()
        # draw mirror
        #glColor4fv(self.color)
        if self.dying:
            if self.restTime % 2:
                color = self.color
            else:
                color = (.3, .2, .2, .2)
        else:
            color = self.color
        self.setMaterial(color)
        glPushMatrix()
        glTranslate(0, 0, .5)
        glRotate(angle, 0, 0, 1)
        glScale(0.1, 1, 1)
        glutSolidCube(1)
        glPopMatrix()

class Emitter(Item):
    color = glcolor(147, 17, 161, 0xff)
    MAX_LENGTH = 1000
    def calculate(self, field):
        x, y = self.pos
        dx, dy = self.orient
        alive = True
        light = self.light = Light()
        light.nodes.append((x, y))
        vis = {((x, y), (dx, dy))}
        cnt = 0 
        item = None
        while alive and cnt < self.MAX_LENGTH:
            cnt += 1
            p1 = x1, y1 = x + dx, y + dy
            item = field.get_sprite_at(p1)
            if item:
                if item.reflective:
                    nx, ny = item.orient
                    nLen2 = nx * nx + ny * ny
                    proj2 = 2 * (nx * dx + ny * dy)
                    tx2 = proj2 * nx / nLen2
                    ty2 = proj2 * ny / nLen2
                    dx, dy = dx - tx2, dy - ty2
                else:
                    alive = False
                light.nodes.append(p1)
                if (p1, (dx, dy)) in vis: break
                vis.add((p1, (dx, dy)))
            x, y = p1
        light.end = item

class Goal(Item):
    color = glcolor(0xff, 0, 0, 0xff)

class Light:
    color = glcolor(0xee, 0, 0, 0x88)
    def __init__(self):
        self.nodes = []

    def die(self):
        pass

class Bomb(Item):
    color = glcolor(226, 56, 58, 0xff)

class Obstacle(Item):
    moveable = False
    color = glcolor(74, 80, 72, 0xff)

    def die(self):
        pass

class Lights(Sprite):
    def __init__(self):
        super(Lights, self).__init__()

    def redraw(self, emitters):
        gw, gh = GRID_SIZE
        self.lights = []
        for emitter in emitters:
            light = emitter.light
            self.lights.append(light)

    def draw(self):
        glDisable(GL_LIGHTING)
        for light in self.lights:
            glColor4fv(light.color)
            glBegin(GL_LINE_STRIP)
            for p in light.nodes:
                x, y = p
                glVertex3d(x, y, .5)
                
            glEnd()
        glEnable(GL_LIGHTING)
