import utils
import pygame
import os, sys
from OpenGL.GL import *
from utils import Timer
import utils

baseDir = "models"

class Object(object):
    def __init__(self, name):
        self.name = name
        self.indices = []
        self.vdata = [] # GL_T2F_N3F_V3F
        self.material = None
        self.aniMat = utils.eye_glmat4()

    def convert(self):
        self.indices = utils.convert_ctypes(
                self.indices, ctypes.c_uint, (len(self.indices), ))
        print 'Object indices len:{}'.format(len(self.indices))
        self.vdata = utils.convert_ctypes(
                self.vdata, ctypes.c_float, (len(self.vdata), ))

    def draw(self):
        material = self.material
        if material: 
            glEnable(GL_TEXTURE_2D)
            glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
            
            glMaterialfv(GL_FRONT, GL_AMBIENT, material.ambient)
            glMaterialfv(GL_FRONT, GL_DIFFUSE, material.diffuse)
            glMaterialfv(GL_FRONT, GL_SPECULAR, material.specular)
            glMaterialfv(GL_FRONT, GL_SHININESS, material.shininess)
        else: glDisable(GL_TEXTURE_2D)

        if material:
            glBindTexture(GL_TEXTURE_2D, material.texid)
        glInterleavedArrays(GL_T2F_N3F_V3F, 0, self.vdata)
        # glMultMatrixf(self.aniMat)
        glDrawElements(GL_TRIANGLES, len(self.indices),
                       GL_UNSIGNED_INT, self.indices)

        # is these line needed ?
        # glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
        # glDisable(GL_TEXTURE_2D)

class Model(object):
    def __init__(self, filename):
        tm = Timer()
        self.objects = {}
        self.mtllib = None
        self.vertices = []
        self.texcoords = []
        self.normals = []

        lineID = 0
        for line in open(os.path.join(baseDir, filename), "r"):
            lineID += 1
            # print lineID
            if line.startswith('#'): continue
            v = line.split()
            if not v: continue

            if v[0] == 'o':
                obj = Object(v[1])
                self.objects[obj.name] = obj
            elif v[0] == 'usemtl':
                obj.material = self.mtllib.get(v[1])
            elif v[0] == 'v':
                assert len(v) == 4
                v = map(float, v[1:4])
                self.vertices.append(v)
            elif v[0] == 'vn':
                assert len(v) == 4
                v = map(float, v[1:4])
                self.normals.append(v)
            elif v[0] == 'vt':
                assert len(v) == 3
                v = map(float, v[1:3])
                self.texcoords.append(v)
            elif v[0] == 'mtllib':
                self.mtllib = MaterialLib(v[1])
            elif v[0] == 'f':
                assert len(v) == 4
                indices = map(lambda x:map(int, x.split('/')), v[1:])
                self.add_face(obj, indices)

        for obj in self.objects.itervalues():
            obj.convert()

        self.listname = glGenLists(1)
        glNewList(self.listname, GL_COMPILE)
        for obj in self.objects.itervalues():
            obj.draw()
        glEndList()

        print 'object {}, load time: {}'.format(filename, tm.tick())

    def add_face(self, obj, indices):
        assert len(indices) == 3, 'please use triangle faces'
        # each index tuple: (v, t, n)
        for vi, ti, ni in indices:
            obj.indices.append(len(obj.indices))
            obj.vdata.extend(
                self.texcoords[ti-1] + self.normals[ni-1] + self.vertices[vi-1])

    def draw(self):
        # glCallList(self.listname)
        for obj in self.objects.itervalues():
           obj.draw()

imagenameToTexid = {}

class Material(object):
    def __init__(self, name):
        self.name = name
        self.ambient = (.2, .2, .2)
        self.diffuse = (.8, .8, .8)
        self.specular = (.2, .2, .2)
        self.shininess = 10.
        self.alpha = 1.
        self.texid = 0

    def convert(self):
        self.ambient = utils.convert_ctypes(self.ambient, ctypes.c_float, (3,))
        self.diffuse = utils.convert_ctypes(self.diffuse, ctypes.c_float, (3,))
        self.specular = utils.convert_ctypes(self.specular, ctypes.c_float, (3,))

class MaterialLib(object):
    def __init__(self, filename):
        tm = Timer()
        materials = self.materials = {}

        for line in open(os.path.join(baseDir, filename), "r"):
            if line.startswith('#'): continue
            v = line.split()
            if not v: continue
            if v[0] == 'newmtl':
                name = v[1]
                mtl = Material(name)
                materials[name] = mtl
            elif v[0] == 'Ka':
                mtl.ambient = map(float, v[1:4])
            elif v[0] == 'Kd':
                mtl.diffuse = map(float, v[1:4])
            elif v[0] == 'Ks':
                mtl.specular = map(float, v[1:4])
            elif v[0] == 'Ns':
                mtl.shininess = float(v[1])
            elif v[0] == 'd' or v[0] == 'Tr':
                mtl.alpha = float(v[1])
            elif v[0] == 'map_Kd':
                mtl.texid = glGenTextures(1)
                if v[1] in imagenameToTexid: continue
                imagenameToTexid[v[1]] = mtl.texid
                image = pygame.image.load(os.path.join(baseDir, v[1]))
                w, h = image.get_rect().size
                image = pygame.image.tostring(image, 'RGBA', 1)
                glBindTexture(GL_TEXTURE_2D, mtl.texid)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,
                                GL_LINEAR)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER,
                                GL_LINEAR)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S,
                                GL_MIRRORED_REPEAT)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T,
                                GL_MIRRORED_REPEAT)
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h,
                             0, GL_RGBA, GL_UNSIGNED_BYTE, image)

        for material in materials.itervalues():
            material.convert()
        print 'mtllib {}, load time: {}'.format(filename, tm.tick())

    def get(self, name, default=None):
        return self.materials.get(name, default)

if __name__ == '__main__':
    o = Model('robot.obj')
