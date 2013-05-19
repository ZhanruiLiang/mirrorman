from sprites import Emitter, Bomb, Obstacle, Player, Mirror
from config import GRID_SIZE
import pygame

__meta__ = type

class Field(pygame.sprite.Sprite):
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
        for x in xrange(w):
            self.add_sprite(Obstacle(pos=(x, 0)))
            self.add_sprite(Obstacle(pos=(x, h-1)))
        for y in xrange(1, h-1):
            self.add_sprite(Obstacle(pos=(0, y)))
            self.add_sprite(Obstacle(pos=(w-1, y)))

        self.image = pygame.Surface((w * GRID_SIZE[0], h * GRID_SIZE[1]))
        self.image.fill((0xff, 0xff, 0xff, 0xff))
        self.rect = (0, 0)

    def add_sprite(self, sp):
        # unpack to check
        x, y = sp.pos
        assert (x, y) not in self._map, "{} already has {}".format((x, y), self._map[x, y])
        self._map[(x, y)] = sp

    def get_sprite_at(self, pos):
        x, y = pos
        return self._map.get((x, y), None)

    def update_sprite(self, sp, oldPos):
        x0, y0 = oldPos
        x, y = sp.pos
        assert self._map[x0, y0] == sp
        del self._map[x0, y0]
        self._map[x, y] = sp

    def remove_sprite_at(self, pos):
        x, y = pos
        del self._map[x, y]

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

class Level:
    """
    emitters: Emitter[]
    bombs: Bomb[]
    mirrors: Mirror[]
    player: Player
    field: Field
    """
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
        self.field.add_sprite(sp)

class Level_test(Level):
    def __init__(self):
        Level.__init__(self, 'test level', (12, 10))
        A = self.add

        A(Player(pos=(4, 4)))
        A(Bomb(pos=(5, 4)))
        A(Emitter(pos=(6, 4)))
        A(Emitter(pos=(6, 5)))
        A(Mirror(pos=(6, 6)))
        A(Mirror(pos=(8, 8), orient=(-1, -1)))
        A(Mirror(pos=(8, 4), orient=(-1, 1)))

        self.collect()

class Level_test_2(Level):
    def __init__(self):
        Level.__init__(self, 'test level 2', (12, 11))
        A = self.add

        A(Player(pos=(4, 6)))
        A(Emitter(pos=(2, 9), orient=(0, -1)))
        A(Mirror(pos=(2, 2), orient=(1, 1)))
        A(Mirror(pos=(9, 2), orient=(-1, 1)))
        A(Mirror(pos=(9, 6), orient=(-1, -1)))
        A(Mirror(pos=(2, 6), orient=(1, -1)))
        A(Mirror(pos=(4, 1), orient=(0, 1)))

        self.collect()

levels = [
    Level_test,
    Level_test_2,
]
