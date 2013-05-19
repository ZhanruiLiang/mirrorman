import pygame
from config import GRID_SIZE

__meta__ = type

class Lights(pygame.sprite.Sprite):
    layer = 20
    def __init__(self, surfaceSize):
        super(Lights, self).__init__()
        self.size = surfaceSize
        self.image = pygame.Surface(surfaceSize).convert_alpha()
        self.rect = (0, 0)

    def redraw(self, emitters):
        gw, gh = GRID_SIZE
        image = self.image
        image.fill((0, 0, 0, 0))
        for emitter in emitters:
            light = emitter.light
            ps = []
            for p in light.nodes:
                x = gw/2 + gw * p[0]
                y = gh/2 + gh * p[1]
                ps.append((x, y))
            pygame.draw.lines(image, emitter.color, False, ps, 4)
            for p in ps:
                pygame.draw.circle(image, emitter.color, p, 5)
