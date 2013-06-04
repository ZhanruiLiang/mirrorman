import pygame
import os

GRID_SIZE = 80, 80
SCREEN_SIZE = 1000, 700
FPS = 60
DD = 3
SINGLE_ANIMATION = 0
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
