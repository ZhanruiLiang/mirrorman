import math
from OpenGL.GL import *
from OpenGL.GLUT import *
import utils
import ctypes
import config

PI = math.acos(-1.0)


def calculateNormal(vA, vB):
    vC = (vA[1]*vB[2]-vA[2]*vB[1],
          vA[2]*vB[0]-vA[0]*vB[2],
          vA[0]*vB[1]-vA[1]*vB[0])
    factor = math.sqrt(vC[0]**2 + vC[1]**2 + vC[2]**2)

    vC = [i/factor for i in vC]
    return vC

class CubeShape:
    def __init__(self):
        self.listID = glGenLists(1)

        glNewList(self.listID, GL_COMPILE)

        glBegin(GL_QUADS)
        #front
        glNormal3fv((1., .0, .0))
        glVertex3fv((.5, -.5, -.5))
        glVertex3fv((.5, .5, -.5))
        glVertex3fv((.5, .5, .5))
        glVertex3fv((.5, -.5, .5))
        #left
        glNormal3fv((0., -1., .0))
        glVertex3fv((-.5, -.5, -.5))
        glVertex3fv((-.5, -.5, .5))
        glVertex3fv((.5, -.5, .5))
        glVertex3fv((.5, -.5, -.5))
        #back
        glNormal3fv((-1., 0., 0.))
        glVertex3fv((-.5, -.5, -.5))
        glVertex3fv((-.5, .5, -.5))
        glVertex3fv((-.5, .5, .5))
        glVertex3fv((-.5, -.5, .5))
        #right
        glNormal3fv((1., 0., 0.))
        glVertex3fv((.5, .5, -.5))
        glVertex3fv((-.5, .5, -.5))
        glVertex3fv((-.5, .5, .5))
        glVertex3fv((.5, .5, .5))
        #top
        glNormal3fv((0., 0., 1.))
        glVertex3fv((.5, -.5, .5))
        glVertex3fv((-.5, -.5, .5))
        glVertex3fv((-.5, .5, .5))
        glVertex3fv((.5, .5, .5))
        #down
        glNormal3fv((0., 0., -1.))
        glVertex3fv((.5, -.5, -.5))
        glVertex3fv((-.5, -.5, -.5))
        glVertex3fv((-.5, .5, -.5))
        glVertex3fv((.5, .5, -.5))
        glEnd()
        glEndList()

    def draw(self):
        glCallList(self.listID)


class cylindarShape:
    def __init__ (self):
        cylindarV = []
        cylindarN = []

        splitNum = 20
        for i in range(splitNum):
            x = math.cos(2*PI*i/splitNum) / 2
            y = math.sin(2*PI*i/splitNum) / 2
            nx = math.cos(2*PI*(i+1)/splitNum) / 2
            ny = math.sin(2*PI*(i+1)/splitNum) / 2
            #rectangle
            cylindarV.append((x, y, .5))
            cylindarV.append((nx, ny, .5))
            cylindarV.append((nx, ny, -.5))
            cylindarV.append((x, y, .5))
            cylindarV.append((nx, ny, -.5))
            cylindarV.append((x, y, -.5))
            vc = calculateNormal((.0, .0, -1.), (nx-x, ny-y, .0))
            for j in range(6): cylindarN.append(vc)
            #upper triangle
            cylindarV.append((.0, .0, .5))
            cylindarV.append((x, y, .5))
            cylindarV.append((nx, ny, .5))
            vc = calculateNormal((x, y, .0), (nx, ny, .0))
            for j in range(3): cylindarN.append(vc)
            #lower triangle
            cylindarV.append((.0, .0, -.5))
            cylindarV.append((x, y, -.5))
            cylindarV.append((nx, ny, -.5))
            vc = calculateNormal((nx, ny, .0), (x, y, .0))
            for j in range(3): cylindarN.append(vc)

        self.cylindarV = utils.convert_ctypes(cylindarV, 
                ctypes.c_float, (len(cylindarV), 3))
        self.cylindarN = utils.convert_ctypes(cylindarN, 
                ctypes.c_float, (len(cylindarN), 3))
        self.cylindarI = utils.convert_ctypes(range(len(cylindarV)),
                ctypes.c_uint, (len(cylindarV), ))

    def draw(self):
        glDisable(GL_TEXTURE_2D)
        glVertexPointer(3, GL_FLOAT, 0, self.cylindarV)
        glNormalPointer(GL_FLOAT, 0, self.cylindarN)
        glDrawElements(GL_TRIANGLES, len(self.cylindarI), GL_UNSIGNED_INT, self.cylindarI)
