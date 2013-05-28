import utils
import pygame
import os
from OpenGL.GL import *
from utils import Timer

baseDir = "models"

class Model(object):
    def __init__(self, filename):
        tm = Timer()
        vertices = []
        normals = []
        texcoords = []
        self.mtlName = ''
        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.indices = []
        self.material = None

        for line in open(os.path.join(baseDir, filename), "r"):
            if line.startswith('#'): continue
            v = line.split()
            if not v: continue
            if v[0] == 'v':
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
                self.mtlName = v[1]
            elif v[0] == 'f':
                assert len(v) == 4, "use triangle face please!"
                for i in range(1, 4):
                    temp = map(int, v[i].split('/'))
                    assert len(temp) == 3, "face must have vertice, normal, texture index"
                    self.vertices.append(vertices[temp[0]-1])
                    self.texcoords.append(texcoords[temp[1]-1])
                    self.normals.append(normals[temp[2]-1])
        print 'obj: {}, load time {}'.format(filename, tm.tick())
        self.indices = range(len(self.vertices))
        self.indices = utils.convert_ctypes(
            self.indices, ctypes.c_uint, (len(self.indices), ))
        self.vertices = utils.convert_ctypes(
            self.vertices, ctypes.c_float, (len(self.vertices), 3))
        self.texcoords = utils.convert_ctypes(
            self.texcoords, ctypes.c_float, (len(self.texcoords), 2))
        self.normals = utils.convert_ctypes(
            self.normals, ctypes.c_float, (len(self.normals), 3))
        print 'type convertion time {}'.format(tm.tick())

        self.material = Material(self.mtlName)
    
class Material(object):
    def __init__ (self, filename):
        tm = Timer()

        self.ambient = (.0, .0, .0)
        self.diffuse = (1., 1., 1.)
        self.specular = (.0, .0, .0)
        self.shininess = 10.
        self.texW = 0
        self.texH = 0
        self.image = None

        for line in open(os.path.join(baseDir, filename), "r"):
            if line.startswith('#'): continue
            v = line.split()
            if not v: continue
            if v[0] == 'Ka':
                self.ambient = map(float, v[1:4])
            elif v[0] == 'Kd':
                self.diffuse = map(float, v[1:4])
            elif v[0] == 'Ks':
                self.specular = map(float, v[1:4])
            elif v[0] == 'Ns':
                self.shininess = float(v[1])
            elif v[0] == 'map_Kd':
                self.texid = glGenTextures(1)
                print self.texid
                image = pygame.image.load(os.path.join(baseDir, v[1]))
                self.texW, self.texH = image.get_rect().size
                self.image = pygame.image.tostring(image, 'RGBA', 1)
                #self.image = utils.convert_ctypes(
                #    self.image, ctypes.c_uint, (len(self.image), ))
                glBindTexture(GL_TEXTURE_2D, self.texid)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,
                                GL_LINEAR)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER,
                                GL_LINEAR)
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA,
                             self.texW, self.texH, 0, GL_RGBA,
                             GL_UNSIGNED_BYTE, self.image)
        print 'material {}, load time: {}'.format(filename, tm.tick())

