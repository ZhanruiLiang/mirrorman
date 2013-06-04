import bpy
objs = bpy.data.objects.values()
def flip_names(objs):
    for x in objs:
        if x.name.endswith('.L.001'):
            x.name = x.name[:-6] + '.R'
flip_names(objs)