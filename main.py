import pygame
import sys
import config
import display
from display import Display
from sprites import Goal, Lights
from levels import Level, levels
import shapes

def move((x, y), (dx, dy)):
    return x + dx, y + dy

display.init()


class Game:
    def move_player(self, player, direction):
        x0, y0 = player.pos
        x, y = move(player.pos, direction)
        item1 = self.field.get_sprite_at((x, y))
        canGo = True
        if item1:
            if isinstance(item1, Goal):
                self.end_game(True)
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
        self.display = Display()
        self.field = level.field
        self.player = level.player
        self.emitters = level.emitters
        # self.mirrors = level.mirrors
        # self.bombs = level.bombs

    def init_display(self):
        display = self.display
        display.add(self.field)
        for sp in self.field:
            display.add(sp)
        lights = self.lights = Lights()
        display.add(lights)

    def end_game(self, win):
        self._ended = True
        self._win = win
        if win:
            self.display.hint('You win. Press q to quit.')
        else:
            self.display.hint('You were killed by ray, press q to quit')

    def play(self, level):
        self.load_level(level)
        self.init_display()
        display = self.display
        self._quit = False
        self._win = False
        self._ended = False
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
                        self._quit = True
                    newDir = config.Dirs.get(key, None)
            # update logic
            if not self._ended and fcnt % config.DD == 0:
                # update player pos
                if newDir:
                    self.move_player(self.player, newDir)
                    newDir = None
                # recalculate lights
                onHeats = []

                for emitter in self.emitters:
                    emitter.calculate(self.field)
                    end = emitter.light.end
                    if end and not end.dying:
                        end.die()
                self.emitters = [x for x in self.emitters if x.alive]
                self.lights.redraw(self.emitters)
                for sp in display:
                    if hasattr(sp, 'update2'):
                        sp.update2()
                if self.player.dying:
                    self.end_game(False)
            # update display
            display.update()
            # tick
            timer.tick(config.FPS)
            fcnt += 1


game = Game()
game.play(levels[-1]())
