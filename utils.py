import ctypes
from pygame.time import Clock

def convert_ctypes(a, type, shape):
    Arr = type
    for n in reversed(shape):
        Arr = Arr * n
    b = Arr()
    def assign(a, b, bShape):
        # assign a to b
        if len(bShape) == 1:
            for i in xrange(bShape[0]):
                b[i] = a[i]
        elif len(shape) == 2:
            for i in xrange(shape[0]):
                for j in xrange(shape[1]):
                    b[i][j] = a[i][j]
        else:
            for i in xrange(bShape[0]):
                assign(a[i], b[i], bShape[1:])
    assign(a, b, shape)
    return b

def eye_glmat4():
    a = (ctypes.c_float * 16)()
    a[0] = a[4] = a[8] = a[12] = 1
    return a

def mult_mat4_vec4(m4, v4):
    c = (ctypes.c_float * 4)()
    for i in xrange(4):
        c[i] = 0
        for k in xrange(4):
            c[i] += m4[4 * k + i] * v4[k]
    return c

Timer = Clock

if __name__ == '__main__':
    a = [[1, 2, 3],
         [2, 3, 4]]
    print convert_ctypes(a, ctypes.c_float, (2, 3))
    a = [[1, 2, 3]]
    print convert_ctypes(a, ctypes.c_float, (1, 3))
