import random

import pygame


class Maze_Player(pygame.sprite.Sprite):
    def __init__(self, screen, color="white"):
        super().__init__()
        self.image = pygame.Surface([60, 60])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = [screen.get_width() / 2, screen.get_height() / 2]
        self.speed = 300

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)


class Maze_Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill("blue")
        self.rect = self.image.get_rect()
        self.rect.topleft = [x, y]


class Maze_Generator:
    def __init__(self, group=pygame.sprite.Group(), width=800, height=600):
        self.walls = group
        self.width = width
        self.height = height

    def generate(self):
        wall_size = 60 * 2

        for i in range(0, self.width, wall_size):
            for j in range(0, self.height, wall_size):
                if random.randint(1, 6) == 1:
                    self.walls.add(Maze_Wall(i, j, wall_size, wall_size))
