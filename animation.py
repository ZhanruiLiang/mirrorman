import os, sys
import utils

baseDir = "animations"

class Animation(object):
    """
    Animation file format:
    'ts' timeStep # time between frames, in second
    'n' totalFrames 
    'i' objName invMatrix
    'f' objName frameID matrix... # frames counts from 0
    """
    def __init__(self, filename, model):
        fullpath = os.path.join(baseDir, filename)
        invMats = {}
        lineID = 0
        for line in open(fullpath, 'r'):
            line = line.split()
            lineID += 1
            opr = line[0]
            if opr == 'f':
                objName = line[1]
                frameID = int(line[2])
                mat = utils.convert(line[3:], c_float, (16,))
            elif opr == 'ts':
                self.timeStep = float(line[1])
            elif opr == 'n':
                self.nFrames = int(line[1])
            elif opr == 'i':
                objName = line[1]
                mat = utils.convert(line[2:], c_float, (16,))
                invMats[objName] = mat
            else:
                print 'In line {}, unknown command "{}"'.format(lineID, opr)

        for objName, invMat in invMats.iteritems():
            obj = model
