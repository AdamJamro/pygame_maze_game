import pygame
from screeninfo import get_monitors

import Maze_Objects


class Game:
    width, height = 800, 600

    def __init__(self):
        self.walls = None
        self.screen = None
        monitor = get_monitors()[0]
        self.width, self.height = monitor.width, monitor.height
        self.clock = pygame.time.Clock()

    def main(self):
        pygame.init()

        self.screen = pygame.display.set_mode([self.width, self.height])
        # clock = pygame.time.Clock()
        dt = 0

        player = Maze_Objects.Maze_Player(self.screen)
        self.walls = pygame.sprite.Group()
        maze = maze_generator(self.walls)
        self.walls.add(Maze_Objects.Maze_Wall(100, 100, 60, 60))

        running = True
        while running:
            # poll for events
            # pygame.QUIT event means the user clicked X to close your window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # fill the screen with a color to wipe away anything from last frame
            self.screen.fill("purple")

            self.update_movement(player, dt)
            self.screen.blit(player.image, player.rect.topleft)
            for wall in self.walls:
                self.screen.blit(wall.image, wall.rect)

            # flip() the display to put your work on screen
            pygame.display.flip()

            # limits FPS to 60
            # dt is delta time in seconds since last frame, used for framerate-
            # independent physics.
            dt = self.clock.tick(60) / 1000

        pygame.quit()

    def update_movement(self, sprite, dt):
        old_x, old_y = sprite.rect.x, sprite.rect.y

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            sprite.rect.y = max(0, sprite.rect.y - sprite.speed * dt)
        if keys[pygame.K_s]:
            sprite.rect.y = min(self.height - sprite.rect.height, sprite.rect.y + sprite.speed * dt)
        if keys[pygame.K_a]:
            sprite.rect.x = max(0, sprite.rect.x - sprite.speed * dt)
        if keys[pygame.K_d]:
            sprite.rect.x = min(self.width - sprite.rect.width, sprite.rect.x + sprite.speed * dt)

        new_x, new_y = sprite.rect.x, sprite.rect.y
        for wall_sprite in self.walls:
            if wall_sprite.rect.colliderect(new_x, new_y, sprite.rect.width, sprite.rect.height):
                sprite.rect.x, sprite.rect.y = old_x, old_y
                break


if __name__ == "__main__":
    game = Game()
    game.main()
