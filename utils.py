import ctypes
from pygame.time import Clock
import numpy

def convert_ctypes(a, type, shape):
    Arr = type
    for n in reversed(shape):
        Arr = Arr * n
    b = Arr()
    def assign(a, b):
        for i, x in enumerate(a):
            try: 
                iter(x)
                assign(x, b[i])
            except: 
                b[i] = x
    assign(a, b)
    return b

Timer = Clock

if __name__ == '__main__':
    a = [[1, 2, 3],
         [2, 3, 4]]
    print convert_ctypes(a, ctypes.c_float, (2, 3))
    a = [[1, 2, 3]]
    print convert_ctypes(a, ctypes.c_float, (1, 3))
