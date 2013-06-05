import pygame
import os

GRID_SIZE = 80, 80
SCREEN_SIZE = 1000, 700
FPS = 40
DD = 3
# ANIMATION_CUT = 5
ANIMATION_CUT = None
DPT = 0.1

Dirs = {
    pygame.K_LEFT: (-1, 0),
    pygame.K_RIGHT: (1, 0),
    pygame.K_UP: (0, 1),
    pygame.K_DOWN: (0, -1),
}

PLAYER_MODEL = 'robot.obj'
#PLAYER_MODEL = 'capsule.obj'

# FIELD_PIC_PATH = os.path.join("pictures", "71.jpg")
FIELD_PIC_PATH = os.path.join("pictures", "window4.jpg")
# FIELD_PIC_PATH = os.path.join("models", "MarbleUTexture.jpg")

SHADOW_COLOR = (.1, .1, .1, 1)
BACK_COLOR = (0., 0., 0., 1)
MIRROR_COLOR = (.5, .0, .5, .5)

MODEL_DIR = 'models/'
MODEL_SUBPATHS = [
        'emitter.obj',
        'emitter-explode/',
        'mirror.obj',
        'wall.obj',
        'wall-corner.obj',
        'exit.obj',
        'mirrorman/mirrorman.obj',
        'mirrorman/die/',
        'mirrorman/push/',
        'mirrorman/rest/',
        'mirrorman/walk/',
        ]
DAT_PATH = 'models/models.dat'
GZIP_LEVEL = 3
