from OpenGL.GLU import *
import math

def distance(p1, p2):
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    return math.sqrt((x1-x2)**2+(y1-y2)**2+(z1-z2)**2)

class Camera:
    eyePos = None
    centerPos = None
    playerPos = None
    topHeight = 30

    stopThreshold = .1
    stepT = .05

    # dir = eyePos - centerPos
    dir = (0., -5., 6)

    def __init__(self, field):
        self.field = field
        w, h = field.size
        self.topPos = w/2. + .23, h/2. + .23, self.topHeight
        self.target = None
        self._nextCenterPos = None
        self.eyePos = (0., 0., 0.)
        self.centerPos = (0., 0., 0.)
        self.zoomRate = 0

    def zoom_in(self):
        self._zoom(-.05) 

    def zoom_out(self):
        self._zoom(.05) 

    def _zoom(self, rate):
        self.zoomRate += rate
        self.zoomRate = min(1, max(0, self.zoomRate))

    def trace_target(self, target):
        self.target = target

    def update(self):
        if self.target is not None:
            self._nextCenterPos = self.target.cur_pos() + (0,)
        if self._nextCenterPos and distance(self.centerPos, self._nextCenterPos) > .1:
            x1, y1, z1 = self.centerPos
            x2, y2, z2 = self._nextCenterPos
            t = self.stepT
            self.centerPos = x1 + t * (x2 - x1), y1 + t * (y2 - y1), z1 + t * (z2 - z1)
        else:
            self.centerPos = self._nextCenterPos
            self._nextCenterPos = None
        cx, cy, cz = self.centerPos
        dx, dy, dz = self.dir
        bx, by, bz = cx + dx, cy + dy, cz + dz
        tx, ty, tz = self.topPos
        tx = bx
        t = self.zoomRate
        self.eyePos = bx + t * (tx - bx), by + t * (ty - by), bz + t * (tz - bz)
        # print 'eye:', self.eyePos, 'center:', self.centerPos

    def mul_view_matrix(self):
        gluLookAt(*self.eyePos + self.centerPos + (0., 0., 1.))
