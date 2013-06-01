import pygame

GRID_SIZE = 80, 80
SCREEN_SIZE = 1000, 700
FPS = 30
DD = 3

Dirs = {
    pygame.K_LEFT: (-1, 0),
    pygame.K_RIGHT: (1, 0),
    pygame.K_UP: (0, 1),
    pygame.K_DOWN: (0, -1),
}

PLAYER_MODEL = 'robot.obj'
#PLAYER_MODEL = 'capsule.obj'
