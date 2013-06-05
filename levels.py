from sprites import Sprite, Emitter, Bomb, Obstacle, Player, Mirror, Goal
from sprites import *
from config import GRID_SIZE
import config
import pygame

__meta__ = type

class Field(Sprite):
    """
    obstacles: Obstacle[]
    size: (int, int)

    get_sprite_at(pos)
    update_sprite(sp)
    add_sprite(sp)
    remove_sprite_at(pos)
    remove_sprite(sp)
    """

    def __init__(self, size):
        super(Field, self).__init__()
        w, h = size
        self._map = {}
        self.size = size
        self.pos = w/2., h/2.
        for x in xrange(1, w-1):
            self.add_sprite(Obstacle(pos=(x, 0), orient=(0, 1)))
            self.add_sprite(Obstacle(pos=(x, h-1), orient=(0, -1)))
        for y in xrange(1, h-1):
            self.add_sprite(Obstacle(pos=(0, y), orient=(1, 0)))
            self.add_sprite(Obstacle(pos=(w-1, y), orient=(-1, 0)))
        self.add_sprite(ObstacleCorner(pos=(0, 0), orient=(1, 1)))
        self.add_sprite(ObstacleCorner(pos=(w-1, 0), orient=(-1, 1)))
        self.add_sprite(ObstacleCorner(pos=(w-1, h-1), orient=(-1, -1)))
        self.add_sprite(ObstacleCorner(pos=(0, h-1), orient=(1, -1)))
        self.init_texture()

    def init_texture(self):
        image = pygame.image.load(config.FIELD_PIC_PATH)
        w, h = image.get_rect().size
        image = pygame.image.tostring(image, 'RGBA', 1)
        self.texid = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texid)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,
                        GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER,
                        GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S,
                        GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T,
                        GL_REPEAT)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA,
                     GL_UNSIGNED_BYTE, image)

    def add_sprite(self, sp):
        # unpack to check
        x, y = sp.pos
        assert (x, y) not in self._map, "{} already has {}".format((x, y), self._map[x, y])
        self._map[(x, y)] = sp
        sp.field = self

    def get_sprite_at(self, pos):
        x, y = pos
        return self._map.get((x, y), None)

    def update_sprite(self, sp, oldPos):
        x0, y0 = oldPos
        if self._map[x0, y0] is sp:
            del self._map[x0, y0]
        x, y = sp.pos
        self._map[x, y] = sp

    def remove_sprite_at(self, pos):
        x, y = pos
        try: del self._map[x, y]
        except: pass

    def remove_sprite(self, sp):
        x, y = sp.pos
        assert self._map[x, y] == sp
        del self._map[x, y]

    def __iter__(self):
        w, h = self.size
        for x in xrange(w):
            for y in xrange(h):
                sp = self._map.get((x, y), None)
                if sp: yield sp

    def draw(self):
        w, h = self.size
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texid)
        glColor4fv((.8, .8, .8, .7))
        glBegin(GL_QUADS)
        #glTexCoord2f(.0, .0)
        #glVertex3f(-14., -14., .0)
        #glTexCoord2f(0., float(90)/15)
        #glVertex3f(-14., 90., .0)
        #glTexCoord2f(float(90)/15, float(90)/15)
        #glVertex3f(90., 90., .0)
        #glTexCoord2f(float(90)/15, 0.)
        #glVertex3f(90., -14., .0)
        glNormal3fv((0., 0., 1.))
        glTexCoord2f(.0, .0)
        glVertex3f(-20., -20., .0)
        glTexCoord2f(0., 8.)
        glVertex3f(-20., 60., .0)
        glTexCoord2f(8., 8.)
        glVertex3f(60., 60., .0)
        glTexCoord2f(8., 0.)
        glVertex3f(60., -20., .0)


        #glTexCoord2f(.0, .0)
        #glVertex3f(-1., -1., .0)
        #glTexCoord2f(.0, float(h)/15)
        #glVertex3f(-1., h, .0)
        #glTexCoord2f(float(w)/15, float(h)/15)
        #glVertex3f(w, h, .0)
        #glTexCoord2f(float(w)/15, .0)
        #glVertex3f(w, -1., .0)
        glEnd()
        #glScale(self.size[0], self.size[1], 0.01)
        #glDisable(GL_LIGHTING)
        #glColor3d(.6, .6, .5)
        #glutSolidCube(1)
        #glEnable(GL_LIGHTING)

class Level:
    """
    emitters: Emitter[]
    bombs: Bomb[]
    mirrors: Mirror[]
    player: Player
    field: Field
    """
    name = 'abstract level'
    def __init__(self, name, fieldSize):
        self.name = name
        self.emitters = []
        self.field = Field(fieldSize)

    def collect(self):
        types = {
            Emitter: self.emitters,
        }
        for item in self.field:
            for typ, lst in types.iteritems():
                if isinstance(item, typ):
                    lst.append(item)
                    break
            if isinstance(item, Player):
                self.player = item
    def add(self, sp):
        if isinstance(sp, Goal):
            self.field.remove_sprite_at(sp.pos)
        self.field.add_sprite(sp)

class Level_test_2(Level):
    name = 'test level 2'
    def __init__(self):
        Level.__init__(self, 'test level 2', (12, 11))
        A = self.add

        A(Player(pos=(4, 7)))
        A(Emitter(pos=(2, 9), orient=(0, -1)))
        A(Emitter(pos=(9, 8), orient=(-1, 0)))
        A(Obstacle(pos=(6, 1)))
        A(Obstacle(pos=(7, 1)))
        A(Obstacle(pos=(8, 1)))
        A(Mirror(pos=(2, 2), orient=(1, 1)))
        A(Mirror(pos=(9, 2), orient=(-1, 1)))
        A(Mirror(pos=(9, 6), orient=(-1, -1)))
        A(Mirror(pos=(4, 3), orient=(0, 1)))
        A(Goal(pos=(5, 0), orient=(0, 1)))

        self.collect()

class Level_test_3(Level):
    name = 'test level 3'
    def __init__(self):
        Level.__init__(self, 'test level 3', (20, 20))
        A = self.add

        A(Player(pos=(10, 2)))
        A(Emitter(pos=(5, 15), orient=(-1, 0)))
        A(Emitter(pos=(15, 15), orient=(0, 1)))
        A(Emitter(pos=(15, 5), orient=(1, 0)))
        A(Emitter(pos=(5, 5), orient=(0, -1)))
        # A(Obstacle(pos=(6, 1)))
        # A(Mirror(pos=(4, 3), orient=(0, 1)))
        A(Mirror(pos=(3, 15), orient=(1, 1)))
        A(Mirror(pos=(15, 18), orient=(1, -1)))
        A(Mirror(pos=(18, 5), orient=(-1, -1)))
        A(Mirror(pos=(5, 3), orient=(-1, 1)))

        A(Goal(pos=(5, 0), orient=(0, 1)))

        self.collect()

class Level_test_4(Level):
    name = 'test level 4'
    def __init__(self):
        Level.__init__(self, 'test level 4', (9, 9))
        A = self.add
        A(Player(pos=(5,4)))
        A(Emitter(pos=(7, 7), orient=(0, -1)))

        A(Mirror(pos=(7, 1), orient=(-1, 1)))
        A(Mirror(pos=(1, 1), orient=(1, 1)))
        A(Mirror(pos=(1, 7), orient=(1, -1)))
        A(Mirror(pos=(6, 7), orient=(-1, -1)))
        A(Mirror(pos=(6, 2), orient=(-1, 1)))
        A(Mirror(pos=(2, 2), orient=(1, 1)))
        A(Mirror(pos=(2, 4), orient=(1, -1)))
        A(Mirror(pos=(4, 4), orient=(1, -1)))

        A(Mirror(pos=(4, 5), orient=(1, -1)))

        A(Goal(pos=(0, 3), orient=(-1, 0)))
        self.collect()

class Level_test_5(Level):
    name = 'test level 5'
    def __init__(self):
        Level.__init__(self, 'test level 5', (7, 10))
        A = self.add
        A(Emitter(pos=(1, 6), orient=(0, -1)))
        A(Emitter(pos=(2, 7), orient=(0, -1)))
        A(Emitter(pos=(3, 6), orient=(0, -1)))
        A(Emitter(pos=(4, 5), orient=(0, -1)))

        A(Mirror(pos=(1, 3), orient=(1, 1)))
        A(Mirror(pos=(2, 4), orient=(-1, 1)))
        A(Mirror(pos=(3, 3), orient=(1, 1)))
        A(Mirror(pos=(4, 2), orient=(1, 1)))

        A(Player(pos=(1, 1)))
        A(Goal(pos=(6, 2), orient=(1, 0)))

        self.collect()

class Level_test_6(Level):
    name = 'test level 6'
    def __init__(self):
        Level.__init__(self, 'test level 6', (14, 10))
        A = self.add
        A(Player(pos=(5, 1)))

        A(Emitter(pos=(5, 8), orient=(1, 0)))
        
        A(Mirror(pos=(8, 5), orient=(-1, 1)))
        A(Mirror(pos=(9, 4), orient=(-1, 1)))
        A(Mirror(pos=(3, 5), orient=(1, -1)))
        A(Mirror(pos=(3, 3), orient=(1, 1)))
        A(Mirror(pos=(11, 3), orient=(-1, -1)))
        A(Mirror(pos=(11, 2), orient=(-1, 1)))
        A(Mirror(pos=(2, 2), orient=(1, -1)))
        A(Mirror(pos=(8, 6), orient=(-1, -1)))
        A(Mirror(pos=(4, 6), orient=(1, 1)))
        A(Mirror(pos=(4, 7), orient=(1, -1)))
        A(Mirror(pos=(7, 7), orient=(-1, 1)))
        A(Mirror(pos=(7, 8), orient=(-1, -1)))
        A(Goal(pos=(6, 9), orient=(0, 1)))

        self.collect()

levels = [
    Level_test_2,
    Level_test_3,
    Level_test_4,
    Level_test_5,
    Level_test_6
]
