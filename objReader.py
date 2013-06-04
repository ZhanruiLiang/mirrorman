import re
import gzip
import cPickle
import config
import os, sys
from OpenGL.GL import *
from OpenGL.GLUT import *
from models import Model, Object
from utils import Timer
import utils
import pygame

baseDir = config.MODEL_DIR

class _Object(object):
    def __init__(self, name):
        self.name = name
        self.material = None
        self.vdata = []

imageNameToTexid = {}

class Material(object):
    def __init__(self, name):
        self.name = name
        self.ambient = (.2, .2, .2)
        self.diffuse = (.8, .8, .8)
        self.specular = (.2, .2, .2)
        self.shininess = 10.
        self.alpha = 1.
        self.texid = 0
        self._converted = False

    def convert(self):
        if self._converted: return
        self._converted = True
        self.ambient = utils.convert_ctypes(self.ambient, ctypes.c_float, (3,))
        self.diffuse = utils.convert_ctypes(self.diffuse, ctypes.c_float, (3,))
        self.specular = utils.convert_ctypes(self.specular, ctypes.c_float, (3,))

        imageName = self.imageName
        if imageName in imageNameToTexid: 
            self.texid = imageNameToTexid[imageName]
            return
        self.texid = glGenTextures(1)
        imageNameToTexid[imageName] = self.texid
        image = pygame.image.load(imageName)
        w, h = image.get_rect().size
        image = pygame.image.tostring(image, 'RGBA', 1)
        glBindTexture(GL_TEXTURE_2D, self.texid)
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


def convert_model_data(subpath):
    tm = Timer()
    fullpath = os.path.join(baseDir, subpath)

    objects = {}
    mtllib = None
    vertices = []
    texcoords = [[0, 0]]
    normals = []
    mtlBaseDir = os.path.split(fullpath)[0]

    lineID = 0
    for line in open(fullpath, "r"):
        lineID += 1
        # print lineID
        if line.startswith('#'): continue
        v = line.split()
        if not v: continue

        if v[0] == 'o' or v[0] == 'g':
            name = v[1].split('_')[0]
            obj = _Object(name)
            objects[obj.name] = obj
        elif v[0] == 'usemtl':
            materialName = v[1]
            obj.material = mtllib.get(materialName)
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
            mtllib = MaterialLib.load(os.path.realpath(
                os.path.join(mtlBaseDir, v[1])))
        elif v[0] == 'f':
            indices = v[1:]
            assert len(indices) == 3, 'please use triangle faces'
            # each index tuple: (v, t, n)
            for x in indices:
                x = x.split('/')
                vi, ti, ni = map(int, x)
                obj.vdata.extend(
                    texcoords[ti] + normals[ni-1] + vertices[vi-1])
    data = {
        'objects': objects,
        'mtllib': mtllib,
    }
    print 'convert {}, time: {}ms'.format(subpath, tm.tick())
    return data

materialLibs = {}

class MaterialLib(object):
    def __iter__(self):
        for mtl in self.materials.itervalues():
            yield mtl

    def __init__(self, filepath):
        materials = self.materials = {}
        baseDir = os.path.split(filepath)[0]

        for line in open(filepath, "r"):
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
                mtl.shininess = min(128., float(v[1]))
            elif v[0] == 'd' or v[0] == 'Tr':
                mtl.alpha = float(v[1])
            elif v[0] == 'map_Kd':
                mtl.imageName = os.path.join(baseDir, v[1])

    @staticmethod
    def load(filepath):
        if filepath in materialLibs:
            return materialLibs[filepath]
        x = MaterialLib(filepath)
        materialLibs[filepath] = x 
        return x

    def get(self, name, default=None):
        return self.materials.get(name, default)

extractPattern = re.compile(r'.+_(?P<num>\d+)\.obj$')

def extract_num(filename):
    mch = extractPattern.match(filename)
    if mch:
        return int(mch.group('num'))
    else:
        return None

def make_dat():
    data = {}
    tm = Timer()
    for subpath in config.MODEL_SUBPATHS:
        if subpath.endswith(os.path.sep):
            for f in os.listdir(os.path.join(baseDir, subpath)):
                if extract_num(f) is not None:
                    fpath = os.path.join(subpath, f)
                    data[fpath] = convert_model_data(fpath)
                    # break # dummy
        else:
            data[subpath] = convert_model_data(subpath)
    print 'total convert time: {}ms'.format(tm.tick())
    if config.GZIP_LEVEL is not None:
        print 'compressing...'
        outf = gzip.open(config.DAT_PATH, 'wb', config.GZIP_LEVEL)
    else:
        print 'writing...'
        outf = open(config.DAT_PATH, 'wb')
    cPickle.dump(data, outf, -1)
    outf.close()
    print 'write {}, time: {}ms'.format(config.DAT_PATH, tm.tick())

def load_models():
    tm = Timer()
    if config.GZIP_LEVEL is not None:
        infile = gzip.open(config.DAT_PATH, 'rb', config.GZIP_LEVEL)
    else:
        infile = open(config.DAT_PATH, 'rb')
    # data = infile.read()
    modeldatas = cPickle.loads(infile.read())
    infile.close()
    print 'load dat time: {}ms'.format(tm.tick())
    for filepath, data in modeldatas.iteritems():
        objects = data['objects']
        mtllib = data['mtllib']
        for mtl in mtllib:
            mtl.convert()
        model = Model(filepath)
        for obj in objects.itervalues():
            model.objects[obj.name] = Object(obj.name, obj.vdata, obj.material)
        Model._models[filepath] = model
