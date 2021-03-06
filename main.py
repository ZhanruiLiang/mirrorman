import sys
import objReader

if '-m' in sys.argv[1:]:
    objReader.make_dat()
    exit(0)

# import OpenGL_accelerate
import pygame
import config
import display
from display import Display, MenuDisplay
from sprites import Goal, Lights
from levels import Level, levels
from camera import Camera

clock = pygame.time.Clock()

def move((x, y), (dx, dy)):
    return x + dx, y + dy

display.init()

objReader.load_models()

class Game:
    def menu(self):
        items = [(level.name, lambda x=level: self.play(x())) for level in levels
            ] + [('quit', lambda: exit(0))]

        menu = MenuDisplay(items)
        self._quitMenu = False

        tm = pygame.time.Clock()
        while not self._quitMenu:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit(0)
                elif event.type == pygame.KEYDOWN:
                    key = event.key
                    if key == pygame.K_q:
                        exit(0)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        menu.click(event.pos)
                        self._quitMenu = True
                elif event.type == pygame.MOUSEMOTION:
                    menu.select(event.pos)
            menu.update()
            tm.tick(config.FPS)

    def move_player(self, player, direction):
        x0, y0 = player.pos
        x, y = move(player.pos, direction)
        canGo = True
        push = False
        item1 = self.field.get_sprite_at((x, y))
        if item1:
            push = True
            if isinstance(item1, Goal):
                player.move(direction)
                self.end_game(True)
                return
            if not item1.moveable:
                canGo = False
            else:
                item2 = self.field.get_sprite_at(move(item1.pos, direction))
                if item2:
                    canGo = False
                else:
                    item1.move(direction)
        if canGo:
            player.move(direction, push)
        else:
            player.push(direction)

    def load_level(self, level):
        self.display = Display()
        self.field = level.field
        self.player = level.player
        self.emitters = level.emitters
        # self.mirrors = level.mirrors
        # self.bombs = level.bombs

    def init_display(self):
        display = self.display
        #display.add(self.field)
        for sp in self.field:
            display.add(sp)
        lights = self.lights = Lights()
        display.add(lights)
        self.camera = Camera(self.field)
        self.camera.trace_target(self.player)
        display.set_camera(self.camera)

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
        timer = pygame.time.Clock()
        fcnt = 0

        while not self._quit:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._quit = True
                elif event.type == pygame.KEYDOWN:
                    key = event.key
                    if key == pygame.K_q:
                        self._quit = True
                    #elif key == pygame.K_r:
                    #    config.ENABLE_REFLECT = not config.ENABLE_REFLECT    
                    #elif key == pygame.K_s:
                    #    config.ENABLE_SHADOW = not config.ENABLE_SHADOW
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:
                        # scroll up, zoom in
                        self.camera.zoom_in()
                    elif event.button == 5:
                        # scroll down, zoom out
                        self.camera.zoom_out()
            # update logic
            if not self._ended and fcnt % config.DD == 0:
                # update player pos
                pressed = pygame.key.get_pressed()
                if self.player.is_ready():
                    for key in config.Dirs:
                        if pressed[key]:
                            direction = config.Dirs[key]
                            self.move_player(self.player, direction)
                            break
                    else:
                        self.player.rest()
                # recalculate lights
                for emitter in self.emitters:
                    emitter.calculate(self.field)
                    end = emitter.light.end
                    if end and not end.dying:
                        end.die()
                self.emitters = [x for x in self.emitters if x.alive]
                self.lights.redraw(self.emitters)
                for sp in display.sprites:
                    if hasattr(sp, 'update2'):
                        sp.update2()
                if self.player.dying:
                    self.end_game(False)
            # update display
            display.update(self.field)
            # tick
            timer.tick(config.FPS)
            clock.tick()
            if fcnt % config.FPS== 0: print clock.get_fps()
            fcnt += 1

game = Game()
while 1:
    game.menu()
