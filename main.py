import pygame
import sys
import config
from levels import Level, levels
from lights import Lights

def move((x, y), (dx, dy)):
    return x + dx, y + dy

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode(config.SCREEN_SIZE, 0, 32)

    def move_player(self, player, direction):
        x0, y0 = player.pos
        x, y = move(player.pos, direction)
        item1 = self.field.get_sprite_at((x, y))
        canGo = True
        if item1:
            if not item1.moveable:
                canGo = False
            else:
                item2 = self.field.get_sprite_at(move(item1.pos, direction))
                if item2:
                    canGo = False
                else:
                    item1.move(direction)
                    self.field.update_sprite(item1, (x, y))
        if canGo:
            player.move(direction)
            self.field.update_sprite(player, (x0, y0))
            self._dirty = True

    def load_level(self, level):
        self.field = level.field
        self.player = level.player
        self.emitters = level.emitters
        # self.mirrors = level.mirrors
        # self.bombs = level.bombs

    def init_display(self):
        display = self.display = pygame.sprite.LayeredUpdates()
        display.add(self.field)
        for sp in self.field:
            display.add(sp)
        lights = self.lights = Lights(self.field.image.get_size())
        display.add(lights)

    def play(self, level):
        self.load_level(level)
        self.init_display()

        display = self.display
        self._quit = False
        self._win = False
        self._dirty = True
        timer = pygame.time.Clock()
        fcnt = 0
        newDir = None
        while not self._quit:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._quit = True
                elif event.type == pygame.KEYDOWN:
                    key = event.key
                    if key == pygame.K_q:
                        exit(0)
                    newDir = config.Dirs.get(key, None)
            if fcnt % config.DD == 0:
                # update player pos
                if newDir:
                    self.move_player(self.player, newDir)
                    newDir = None
                if self._dirty:
                    self._dirty = False
                    # recalculate lights
                    for emitter in self.emitters:
                        emitter.calculate(self.field)
                    self.lights.redraw(self.emitters)
            # update screen
            display.update()
            display.draw(self.screen)
            pygame.display.update()
            # tick
            timer.tick(config.FPS)
            fcnt += 1

pygame.display.init()
pygame.font.init()
game = Game()
game.play(levels[-1]())
