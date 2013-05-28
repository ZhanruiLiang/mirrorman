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
        else:
            for i in xrange(bShape[0]):
                assign(a[i], b[i], bShape[1:])
    assign(a, b, shape)
    return b

Timer = Clock

if __name__ == '__main__':
    a = [[1, 2, 3],
         [2, 3, 4]]
    print convert_ctypes(a, ctypes.c_float, (2, 3))
    a = [[1, 2, 3]]
    print convert_ctypes(a, ctypes.c_float, (1, 3))
