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

class cylindarShape:
    def __init__ (self):
        
        self.cylindarV = []
        self.cylindarN = []
        self.cylindarI = []

        splitNum = 20
        for i in range(splitNum):
            x = math.cos(2*PI*i/splitNum) / 2
            y = math.sin(2*PI*i/splitNum) / 2
            nx = math.cos(2*PI*(i+1)/splitNum) / 2
            ny = math.sin(2*PI*(i+1)/splitNum) / 2
            #rectangle
            self.cylindarV.append((x,y,.5))
            self.cylindarV.append((nx,ny,.5))
            self.cylindarV.append((nx,ny,-.5))
            self.cylindarV.append((x,y,.5))
            self.cylindarV.append((nx,ny,-.5))
            self.cylindarV.append((x,y,-.5))
            vc = calculateNormal((.0,.0,-1.),(nx-x,ny-y,.0))
            for j in range(6): self.cylindarN.append(vc)
            #upper triangle
            self.cylindarV.append((.0,.0,.5))
            self.cylindarV.append((x,y,.5))
            self.cylindarV.append((nx,ny,.5))
            vc = calculateNormal((x,y,.0),(nx,ny,.0))
            for j in range(3): self.cylindarN.append(vc)
            #lower triangle
            self.cylindarV.append((.0,.0,-.5))
            self.cylindarV.append((x,y,-.5))
            self.cylindarV.append((nx,ny,-.5))
            vc = calculateNormal((nx,ny,.0),(x,y,.0))
            for j in range(3): self.cylindarN.append(vc)

        self.cylindarI = range(len(self.cylindarV))
        self.init = False


    def draw(self):
        if self.init == False:
            glEnableClientState(GL_VERTEX_ARRAY)
            glEnableClientState(GL_NORMAL_ARRAY)
            glVertexPointer(3,GL_FLOAT,0,self.cylindarV)
            glNormalPointer(GL_FLOAT,0,self.cylindarN)
            self.init = True
        glDrawElements(GL_TRIANGLES,len(self.cylindarI),GL_UNSIGNED_BYTE,self.cylindarI)
