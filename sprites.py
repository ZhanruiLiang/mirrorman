import pygame
import math
import random
from config import GRID_SIZE, FPS, DD, DPT, SINGLE_ANIMATION
import config
from OpenGL.GL import *
from OpenGL.GLUT import *
from objReader import Model
from animation import Animation, Animation2
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
    modelName = None

    def __init__(self, pos=(0, 0), orient=(1, 0)):
        super(Item, self).__init__(pos)
        self.orient = orient
        self.restTime = None
        if self.modelName:
            self.model = Model.load(self.modelName)
        else:
            self.model = None
        self._pt = 0
        self._nextPos = pos

    def move(self, direction):
        x, y = self.pos
        dx, dy = direction
        self._nextPos = x + dx, y + dy
        self._pt = 0

    def kill(self):
        self.alive = False

    @property
    def dying(self):
        return self.restTime is not None

    def die(self):
        if not self.dying:
            self.restTime = self.dieTime

    def cur_pos(self):
        if self._nextPos == self.pos:
            return self.pos
        x1, y1 = self.pos
        x2, y2 = self._nextPos
        t = self._pt
        return x1 + t * (x2 - x1), y1 + t * (y2 - y1)

    def update2(self):
        if self.dying:
            self.restTime -= 1
            if self.restTime == 0:
                self.kill()
                self.field.remove_sprite(self)
        if self.pos != self._nextPos and self._pt < 1:
            self._pt += DPT
            if self._pt >= 1-1e-8:
                oldPos  = self.pos
                self.pos = self._nextPos
                self.field.update_sprite(self, oldPos)
                self._pt = 0

    def setMaterial(self, color):
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, color)
        glMaterialfv(GL_FRONT, GL_SPECULAR, color)
        glMaterialf(GL_FRONT, GL_SHININESS, .5)

    def draw(self):
        if self._pt > 0:
            x1, y1 = self._nextPos
            x0, y0 = self.pos
            dx, dy = x1 - x0, y1 - y0
            t = self._pt
            glTranslated(dx * t, dy * t, 0)
        ox, oy = self.orient
        glRotated(math.degrees(math.atan2(oy, ox)), 0., 0., 1.)
        if self.model:
            self.model.draw()
        else:
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
    def __init__(self, pos=(0, 0), orient=(1, 0)):
        super(AnimatedItem, self).__init__(pos, orient)
        self.animations = {}
        self.animation = None

    def load_animation(self, aniName, aniPath, type=1):
        if type == 1:
            ani = Animation(aniPath, self)
        elif type == 2:
            ani = Animation2(aniPath, self)
        self.animations[aniName] = ani
        # if not self.animation: self.animation = ani

    def update(self):
        super(AnimatedItem, self).update()
        if self.animation:
            self.animation.step()

    def switch(self, aniName):
        self.animation = self.animations[aniName]

    def draw(self):
        if self._pt > 0:
            x1, y1 = self._nextPos
            x0, y0 = self.pos
            dx, dy = x1 - x0, y1 - y0
            t = self._pt
            glTranslated(dx * t, dy * t, 0)
        ox, oy = self.orient
        glRotated(math.degrees(math.atan2(oy, ox)), 0., 0., 1.)
        self.animation.draw()

class Mirror(Item):
    color = glcolor(168, 255, 235, 0xff)
    reflective = True
    modelName = 'mirror.obj'

    def draw1(self):
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
    modelName = 'emitter.obj'
    def calculate(self, field):
        x, y = self.pos
        dx, dy = self.orient
        alive = True
        light = self.light = Light()
        light.nodes.append(self.cur_pos())
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
                light.nodes.append(item.cur_pos())
                if (p1, (dx, dy)) in vis: break
                vis.add((p1, (dx, dy)))
            x, y = p1
        light.end = item

class Light:
    color = glcolor(0, 0x91, 0xe5, 0x88)
    def __init__(self):
        self.nodes = []

    def die(self):
        pass

class Bomb(Item):
    color = glcolor(226, 56, 58, 0xff)

class Obstacle(Item):
    moveable = False
    color = glcolor(74, 80, 72, 0xff)
    modelName = 'wall.obj'

    def die(self):
        pass

class ObstacleCorner(Obstacle):
    modelName = 'wall-corner.obj'

class Goal(Obstacle):
    color = glcolor(0xff, 0, 0, 0xff)
    modelName = None

class Lights(Sprite):
    curDisplace = .5
    curDetail = .10
    curNum = 2
    def __init__(self):
        super(Lights, self).__init__()

    def drawLighting(self, p1, p2, displace):
        height = 1.5
        if displace < self.curDetail:
            glBegin(GL_LINES)
            glVertex3d(p1[0], p1[1], height)
            glVertex3d(p2[0], p2[1], height)
            glEnd()
        else:
            midx = (p1[0] + p2[0]) / 2
            midy = (p1[1] + p2[1]) / 2
            midx += (random.random() - .5) * displace
            midy += (random.random() - .5) * displace
            self.drawLighting(p1, (midx, midy), displace/2)
            self.drawLighting(p2, (midx, midy), displace/2)

    def redraw(self, emitters):
        gw, gh = GRID_SIZE
        self.lights = []
        for emitter in emitters:
            light = emitter.light
            self.lights.append(light)

    def draw(self):
        glDisable(GL_LIGHTING)
        glDisable(GL_TEXTURE_2D)
        for light in self.lights:
            glColor4fv(light.color)
            for i in xrange(0, len(light.nodes) - 1):
                for j in xrange(0, self.curNum):
                    self.drawLighting(light.nodes[i], light.nodes[i+1], self.curDisplace)
            
            #glBegin(GL_LINE_STRIP)
            #for p in light.nodes:
                #x, y = p
                #glVertex3d(x, y, .5)
            #glEnd()
        glEnable(GL_LIGHTING)

class Player(AnimatedItem):
    color = glcolor(69, 161, 17, 0xff)
    # modelName = 'robot.obj'
    modelName = 'mirrorman/mirrorman.obj'

    ST_REST, ST_WALKING, ST_PUSHING = 0, 1, 2

    def __init__(self, pos=(0, 0), orient=(1, 0)):
        super(Player, self).__init__(pos, orient)
        # self.load_animation('walk', 'walk.ani')
        # self.switch('walk')
        self.load_animation('rest', 'mirrorman/rest', type=2)
        if SINGLE_ANIMATION:
            self.animations['push'] = self.animations['rest']
            self.animations['walk'] = self.animations['rest']
        else:
            self.load_animation('push', 'mirrorman/push', type=2)
            self.load_animation('walk', 'mirrorman/walk', type=2)
        self.state = None
        self.rest()

    def push(self, direction):
        self.orient = direction
        if self.state != self.ST_PUSHING:
            self.state = self.ST_PUSHING
            self.switch('push')

    def rest(self):
        if self.state != self.ST_REST:
            self.state = self.ST_REST
            self.switch('rest')

    def move(self, direction, push=False):
        if not push:
            if self.state != self.ST_WALKING:
                self.state = self.ST_WALKING
                self.switch('walk')
        else:
            self.push(direction)
        self.orient = direction
        super(Player, self).move(direction)

    def update2(self):
        if self.state != self.ST_REST and self.pos != self._nextPos and self._pt < 1:
            self._pt += DPT
            if self._pt >= 1-1e-8:
                oldPos  = self.pos
                self.pos = self._nextPos
                self.field.update_sprite(self, oldPos)
                self._pt = 0

    def is_ready(self):
        return self._pt == 0

