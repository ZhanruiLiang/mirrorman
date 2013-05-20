import pygame
from config import GRID_SIZE

__meta__ = type

def alpha(color, a):
    if len(color) == 3:
        r, g, b = color
    else:
        r, g, b, _ = color
    return (r, g, b, a)

class Sprite(pygame.sprite.Sprite):
    """
    pos
    orient
    reflective
    moveable
    layer
    dieTime
    restTime

    image
    rect
    """
    color = (154, 189, 225, 255)
    reflective = False
    moveable = True
    layer = 10
    dieTime = 10
    field = None

    def __init__(self, pos=(0, 0), orient=(1, 0)):
        super(Sprite, self).__init__()
        self.pos = pos
        self.orient = orient
        self.image = None
        self.rect = None
        self.restTime = None

    def update(self):
        if self.image is None:
            self.image = image = pygame.Surface(GRID_SIZE).convert_alpha()
            image.fill(self.color)
            x, y = self.pos
            self.rect = pygame.Rect((0, 0), GRID_SIZE)
            self.rect.topleft = x * GRID_SIZE[0], y * GRID_SIZE[1]

    def move(self, direction):
        x, y = self.pos
        dx, dy = direction
        self.pos = x, y = x + dx, y + dy
        self.rect.topleft = x * GRID_SIZE[0], y * GRID_SIZE[1]

    @property
    def dying(self):
        return self.restTime is not None

    def die(self):
        if not self.dying:
            self.restTime = self.dieTime

    def update2(self):
        if self.dying:
            self.restTime -= 1
            if self.restTime == 0:
                self.kill()
                self.field.remove_sprite(self)
            elif self.restTime % 2:
                self.image.fill(self.color)
            else:
                self.image.fill(alpha(self.color, 0x88))

class Player(Sprite):
    color = (69, 161, 17, 0xff)

class Mirror(Sprite):
    color = (168, 255, 235, 0xff)
    reflective = True

    def update(self):
        if self.image is None:
            Sprite.update(self)
            ox, oy = self.orient
            d = (ox*ox + oy*oy)**.5
            w2 = self.rect.width / 2
            ox *= w2 / d
            oy *= w2 / d
            p1 = (int(w2-oy), int(w2+ox))
            p2 = (int(w2+oy), int(w2-ox))
            pygame.draw.line(self.image, (0, 0, 0, 0xff), p1, p2, 3)

class Emitter(Sprite):
    color = (147, 17, 161, 0xff)
    MAX_LENGTH = 1000
    def calculate(self, field):
        x, y = self.pos
        dx, dy = self.orient
        alive = True
        light = self.light = Light()
        light.nodes.append((x, y))
        vis = {(x, y)}
        cnt = 0 
        item = None
        while alive and cnt < self.MAX_LENGTH:
            cnt += 1
            p1 = x1, y1 = x + dx, y + dy
            item = field.get_sprite_at(p1)
            if item:
                if item.reflective:
                    nx, ny = item.orient
                    nLen2 = nx * nx + ny * ny
                    proj2 = 2 * (nx * dx + ny * dy)
                    tx2 = proj2 * nx / nLen2
                    ty2 = proj2 * ny / nLen2
                    dx, dy = dx - tx2, dy - ty2
                else:
                    alive = False
                light.nodes.append(p1)
                if p1 in vis: break
                vis.add(p1)
            x, y = p1
        light.end = item

class Goal(Sprite):
    color = (0xff, 0, 0, 0xff)

class Light:
    def __init__(self):
        self.nodes = []

    def die(self):
        pass

class Bomb(Sprite):
    color = (226, 56, 58, 0xff)

class Obstacle(Sprite):
    moveable = False
    color = (74, 80, 72, 0xff)

    def die(self):
        pass
