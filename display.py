import pygame

def init():
    pygame.display.init()
    pygame.font.init()

init()

class Hint(pygame.sprite.Sprite):
    layer = 30
    font = pygame.font.SysFont('', 20)
    def __init__(self, rect, text):
        super(Hint, self).__init__()
        rect = self.rect = pygame.Rect(rect)
        image = self.image = pygame.Surface(rect.size).convert_alpha()
        image.fill((0, 0, 0, 0x88))
        image.blit(self.font.render(text, 0, (0xff, 0xff, 0xff)), (0, 0))

class Display(pygame.sprite.LayeredUpdates):
    def hint(self, text):
        self.add(Hint(((100, 100), (300, 100)), text))
