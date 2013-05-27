import math
from OpenGL.GL import *
from OpenGL.GLUT import *

PI = math.acos(-1.0)


def calculateNormal(vA, vB):
    vC = (vA[1]*vB[2]-vA[2]*vB[1],
          vA[2]*vB[0]-vA[0]*vB[2],
          vA[0]*vB[1]-vA[1]*vB[0])
    factor = math.sqrt(vC[0]**2 + vC[1]**2 + vC[2]**2)

    vC = [i/factor for i in vC]
    return vC

_cylindarX = []
_cylindarY = []
_cylindarUTriNor = []
_cylindarDTriNor = []
_cylindarRecNor = []
def cylindar():
    splitNum = 3

    if len(_cylindarX) == 0 or len(_cylindarY) == 0 or \
            len(_cylindarUTriNor) == 0 or len(_cylindarRecNor) == 0:
        for i in xrange(splitNum):
            x = math.cos(2*PI*i/splitNum) / 2
            y = math.sin(2*PI*i/splitNum) / 2
            nx = math.cos(2*PI*(i+1)/splitNum) / 2
            ny = math.sin(2*PI*(i+1)/splitNum) / 2
            _cylindarX.append(x)
            _cylindarY.append(y)
            #rectangle normal
            vA = (.0,.0,-1.)
            vB = (nx-x,ny-y,.0)
            vC = calculateNormal(vA,vB)
            _cylindarRecNor.append(vC[:])
            #upper triangle normal
            vA = (x,y,.0)
            vB = (nx-x,ny-y,.0)
            vC = calculateNormal(vA,vB)
            _cylindarUTriNor.append(vC[:])
            #lower triangle normal
            vA = (nx,ny,.0)
            vB = (x,y,.0)
            vC = calculateNormal(vA,vB)
            _cylindarDTriNor.append(vC[:])
        _cylindarX.append(_cylindarX[0])
        _cylindarY.append(_cylindarY[0])

    for i in xrange(splitNum):
        x, y = _cylindarX[i], _cylindarY[i]
        nx, ny = _cylindarX[i+1], _cylindarY[i+1]
        #draw rectangle
        #glNormal3fv(_cylindarRecNor[i])
        glBegin(GL_QUADS)
        glVertex3f(x,y,.5)
        glVertex3f(nx,ny,.5)
        glVertex3f(nx,ny,-.5)
        glVertex3f(x,y,-.5)
        glEnd()
        #draw upper triangle
        #glNormal3fv(_cylindarUTriNor[i])
        glBegin(GL_TRIANGLES)
        glVertex3f(.0,.0,.5)
        glVertex3f(x,y,.5)
        glVertex3f(nx,ny,.5)
        glEnd()
        #draw lower triangle
        #glNormal3fv(_cylindarDTriNor[i])
        glBegin(GL_TRIANGLES)
        glVertex3f(.0,.0,-.5)
        glVertex3f(x,y,-.5)
        glVertex3f(nx,ny,-.5)
        glEnd()
