import pygame
from screeninfo import get_monitors

import Game_Rendering
import Maze_Objects


class Game:
    width, height = 800, 600

    def __init__(self):
        self.walls = pygame.sprite.Group()
        self.screen = None
        self.clock = None
        monitor = get_monitors()[0]
        self.width, self.height = monitor.width, monitor.height
        self.maze_gen = Maze_Objects.Maze_Generator(group=self.walls, width=self.width, height=self.height)

    def main(self):
        pygame.init()
        self.clock = pygame.time.Clock()

        self.screen = pygame.display.set_mode([self.width, self.height])
        # clock = pygame.time.Clock()
        dt = 0

        player = Maze_Objects.Maze_Player(self.screen)
        maze = self.maze_gen.generate()
        engine = Game_Rendering.Engine(self.screen, player, self.walls)
        pygame.mouse.set_visible(False)

        running = True
        while running:
            # poll for events
            # pygame.QUIT event means the user clicked X to close your window
            for event in pygame.event.get():
                # if event.type == pygame.QUIT:
                #     running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        continue

            engine.animate(dt)

            # limits FPS to 60
            # dt is delta time in seconds since last frame, used for framerate-
            # independent physics.
            dt = self.clock.tick(20) / 1000

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.main()
