from OpenGL.GLU import *

class Camera:
    eyePos = None
    centerPos = None
    playerPos = None

    minWidth = 4.
    minHeight = 3.
    maxWidth = 20.
    maxHeight = 15.

    width = 8.
    height = 6.
    ratio = 8./6.

    def __init__(self, playerPos):
        self.centerPos = (playerPos[0] + .5, playerPos[1] + .5, 0)
        self.eyePos = (playerPos[0] + .5, 
                       playerPos[1] + .5 - self.width/2,
                       self.height)
        self.playerPos = playerPos

    def update(self, playerPos):
        self.centerPos = (playerPos[0] + .5, playerPos[1] + .5, 0)
        self.eyePos = (playerPos[0] + .5, 
                       playerPos[1] + .5 - self.width/2,
                       self.height)
        self.playerPos = playerPos

    def mul_view_matrix(self):
        gluLookAt(*self.eyePos + self.centerPos + (0., 0., 1.))
    
    #your mouse scroll event here
    def adjust(self, rate):
        self.width -= rate
        self.height -= rate / self.ratio
        if self.width <= self.minWidth: self.width = self.minWidth
        if self.height <= self.minHeight: self.height = self.minHeight
        if self.width >= self.maxWidth: self.width = self.maxWidth
        if self.height >= self.maxHeight: self.height = self.maxHeight
        self.eyePos = (self.playerPos[0] + .5, 
                       self.playerPos[1] + .5 - self.width / 2,
                       self.height)
