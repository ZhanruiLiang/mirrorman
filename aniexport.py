import os
import bpy

C = bpy.context
D = bpy.data

def set_frame(i):
    bpy.context.scene.frame_current = i

frameStart = C.scene.frame_start
frameEnd = C.scene.frame_end

cwd = os.path.realpath('.')

def mat_to_str(mat):
    return ' '.join(map(str, [mat[j][i] for j in range(4) for i in range(4)]))

def export(filename, objs, start, end):
    set_frame(0)
    invMat = {obj.name: obj.matrix_world.inverted() for obj in objs}
    with open(filename, 'w') as outf:
        outf.write('n {}\n'.format(end - start + 1))
        for fi in range(start, end+1):
            set_frame(fi)
            for obj in objs:
                mat = obj.matrix_world * invMat[obj.name] 
                outf.write('f {objName} {frameID} {mat}\n'.format(
                    objName=obj.name, frameID=fi-start, mat=mat_to_str(mat),))
    print('exported to {}'.format(os.path.join(cwd, filename)))

export('animations/walk.ani', C.selected_objects, 0, 20)