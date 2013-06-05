import utils
import pygame
import os, sys
from OpenGL.GL import *
from OpenGL.GLUT import *
from utils import Timer
import utils
import config

_objID = 0
class Object(object):
    def __init__(self, name, vdata, material):
        """
        vdata: GL_T2F_N3F_V3F
        """
        global _objID
        self.objID = _objID
        _objID += 1 

        self.vdata = utils.convert_ctypes(vdata, ctypes.c_float, (len(vdata), ))
        self.indices = utils.convert_ctypes(
                range(len(vdata)/8), ctypes.c_uint, (len(vdata)/8, ))
        self.name = name
        self.material = material
        # self.aniMat = utils.eye_glmat4()

    def __hash__(self):
        return hash(self.objID)

    def draw(self):
        material = self.material
        resetLight = False
        if material: 
            glEnable(GL_TEXTURE_2D)
            if material.alpha < 1-1e-8:
                glDisable(GL_LIGHTING)
                glDisable(GL_TEXTURE_2D)
                glEnable(GL_BLEND)
                resetLight = True
                # glBlendEquation(GL_FUNC_ADD)
                glBlendEquation(GL_MAX)
                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                d = material.diffuse
                glColor4f(d[0], d[1], d[2], material.alpha)
            glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
            
            glMaterialfv(GL_FRONT, GL_AMBIENT, material.ambient)
            glMaterialfv(GL_FRONT, GL_DIFFUSE, material.diffuse)
            glMaterialfv(GL_FRONT, GL_SPECULAR, material.specular)
            glMaterialfv(GL_FRONT, GL_SHININESS, material.shininess)
            
        else: glDisable(GL_TEXTURE_2D)

        if material:
            glBindTexture(GL_TEXTURE_2D, material.texid)
        glPushMatrix()
        glInterleavedArrays(GL_T2F_N3F_V3F, 0, self.vdata)
        # glMultMatrixf(self.aniMat)
        glDrawElements(GL_TRIANGLES, len(self.indices),
                       GL_UNSIGNED_INT, self.indices)
        glPopMatrix()
        glDisable(GL_BLEND)
        glDisable(GL_TEXTURE_2D)
        if resetLight:
            glEnable(GL_LIGHTING)


class Model(object):
    def __iter__(self):
        for obj in self.objects.itervalues():
            yield obj

    def __init__(self, filename):
        self.objects = {}

    def draw(self):
        for obj in self:
           obj.draw()
