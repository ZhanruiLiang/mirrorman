import utils
import pygame
from copy import deepcopy
import os, sys
from OpenGL.GL import *
from utils import Timer

baseDir = "models"

class Object(object):
    def __init__(self):
        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.indices = []
        self.mtlname = "None"
        self.material = None

    def process(self):
        self.indices = range(len(self.vertices))
        self.indices = utils.convert_ctypes(
            self.indices, ctypes.c_uint, (len(self.indices), ))
        self.vertices = utils.convert_ctypes(
            self.vertices, ctypes.c_float, (len(self.vertices), 3))
        self.texcoords = utils.convert_ctypes(
            self.texcoords, ctypes.c_float, (len(self.texcoords), 2))
        self.normals = utils.convert_ctypes(
            self.normals, ctypes.c_float, (len(self.normals), 3))

    def draw(self):
        if self.material.texid != 0: glEnable(GL_TEXTURE_2D)
        else: glDisable(GL_TEXTURE_2D)

        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
        glMaterialfv(GL_FRONT, GL_AMBIENT, self.material.ambient)
        glMaterialfv(GL_FRONT, GL_DIFFUSE, self.material.ambient)
        glMaterialfv(GL_FRONT, GL_SPECULAR, self.material.specular)
        glMaterialfv(GL_FRONT, GL_SHININESS, self.material.shininess)
        glVertexPointer(3, GL_FLOAT, 0, self.vertices)
        glNormalPointer(GL_FLOAT, 0, self.normals)
        glTexCoordPointer(2, GL_FLOAT, 0, self.texcoords)
        glBindTexture(GL_TEXTURE_2D, self.material.texid)
        glDrawElements(GL_TRIANGLES, len(self.indices),
                       GL_UNSIGNED_INT, self.indices)



class Model(object):
    def __init__(self, filename):
        tm = Timer()
        self.objectList = []
        self.mtlname = "None"
        self.listname = 0
        vertices = []
        normals = []
        texcoords = []
        obj = Object()

        for line in open(os.path.join(baseDir, filename), "r"):
            if line.startswith('#'): continue
            v = line.split()
            if not v: continue

            if v[0] == 'usemtl':
                if obj.mtlname == "None":
                    obj.mtlname = v[1]
                else:
                    self.objectList.append(deepcopy(obj))
                    obj = Object()
                    obj.mtlname = v[1]
            elif v[0] == 'v':
                assert len(v) == 4
                v = map(float, v[1:4])
                vertices.append(v)
            elif v[0] == 'vn':
                assert len(v) == 4
                v = map(float, v[1:4])
                normals.append(v)
            elif v[0] == 'vt':
                assert len(v) == 3
                v = map(float, v[1:3])
                texcoords.append(v)
            elif v[0] == 'mtllib':
                self.mtlname = v[1]
            elif v[0] == 'f':
                assert len(v) == 4
                for i in range(1, 4):
                    temp = map(int, v[i].split('/'))
                    assert len(temp) == 3, "vertice, normal, texture"
                    obj.vertices.append(vertices[temp[0]-1])
                    obj.texcoords.append(texcoords[temp[1]-1])
                    obj.normals.append(normals[temp[2]-1])

        self.objectList.append(deepcopy(obj))
        for o in self.objectList:
            o.process()

        mtlReader = MaterialReader(self.mtlname)
        for obj in self.objectList:
            for mtl in mtlReader.materialList:
                if mtl.mtlname == obj.mtlname:
                    obj.material = mtl
                    break

        self.listname = glGenLists(1)
        glNewList(self.listname, GL_COMPILE)
        for obj in self.objectList:
            obj.draw()
        glEndList()

        print 'object {}, load time: {}'.format(filename, tm.tick())

    def draw(self):
        glCallList(self.listname)
        #for obj in self.objectList:
        #    obj.draw()

imagenameToTexid = {}

class Material(object):
    def __init__(self):
        self.ambient = (.2, .2, .2)
        self.diffuse = (.8, .8, .8)
        self.specular = (.2, .2, .2)
        self.shininess = 10.
        self.alpha = 1.
        self.texid = 0
        self.mtlname = "None"

class MaterialReader(object):
    def __init__ (self, filename):
        tm = Timer()
        self.materialList = []
        mtl = Material()

        for line in open(os.path.join(baseDir, filename), "r"):
            if line.startswith('#'): continue
            v = line.split()
            if not v: continue
            if v[0] == 'newmtl':
                if mtl.mtlname == 'None':
                    mtl.mtlname = v[1]
                else:
                    self.materialList.append(deepcopy(mtl))
                    mtl = Material()
                    mtl.mtlname = v[1]
            elif v[0] == 'Ka':
                mtl.ambient = map(float, v[1:4])
            elif v[0] == 'Kd':
                mtl.diffuse = map(float, v[1:4])
            elif v[0] == 'Ks':
                mtl.specular = map(float, v[1:4])
            elif v[0] == 'Ns':
                mtl.shininess = float(v[1])
            elif v[0] == 'd' or v[0] == 'Tr':
                self.alpha = float(v[1])
            elif v[0] == 'map_Kd':
                mtl.texid = glGenTextures(1)
                if imagenameToTexid.get(v[1]): continue
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

        self.materialList.append(deepcopy(mtl))
        print 'material {}, load time: {}'.format(filename, tm.tick())

if __name__ == '__main__':
    o = Model('robot.obj')
