import os, sys
import ctypes
import utils

baseDir = "animations"

class Animation(object):
    """
    Animation file format:
    'ts' timeStep # time between frames, in second
    'n' totalFrames 
    'f' objName frameID matrix... # frames counts from 0
    """
    def __init__(self, filename, model):
        self.model = model
        fullpath = os.path.join(baseDir, filename)
        invMats = {}
        self.data = {}
        lineID = 0
        for line in open(fullpath, 'r'):
            line = line.split()
            lineID += 1
            opr = line[0]
            if opr == 'f':
                objName = line[1]
                frameID = int(line[2])
                mat = utils.convert_ctypes(map(float, line[3:]), 
                        ctypes.c_float, (16,))
                self.data[objName, frameID] = mat
            elif opr == 'ts':
                self.timeStep = float(line[1])
            elif opr == 'n':
                self.nFrames = int(line[1])
            else:
                print 'In line {}, unknown command "{}"'.format(lineID, opr)

        for objName, invMat in invMats.iteritems():
            obj = model

        self.start()

    def step(self):
        fi = self.frame
        data = self.data
        for name, obj in self.model.objects.iteritems():
            obj.aniMat = data[name, fi]
        self.frame = (self.frame + 1) % self.nFrames

    def start(self):
        self.frame = 0
