from enum import Enum

default_color_sky = (16, 200, 240)
default_color_ground = (0, 0, 0)
default_color_wall = (8, 30, 255)


class COLOR(Enum):
    SKY = 0
    GROUND = 1
    WALL = 2

    color_of = {
        SKY: default_color_sky,
        GROUND: default_color_ground,
        WALL: default_color_wall
    }
