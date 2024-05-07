import pygame


class Maze_Player(pygame.sprite.Sprite):
    def __init__(self, screen):
        super().__init__()
        self.image = pygame.Surface([60, 60])
        self.image.fill("red")
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
