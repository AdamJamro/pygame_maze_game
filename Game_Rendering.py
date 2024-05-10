import math
import random

import pygame
from pygame import Vector2

import Maze_Objects
import graphic_assets
from graphic_assets import COLOR


def get_line_at_point(center: pygame.math.Vector2, curr_direction: pygame.math.Vector2):
    return get_line_from_points(center, center + curr_direction)


def get_line_from_points(center: pygame.math.Vector2, curr_direction: pygame.math.Vector2):
    if curr_direction.x - center.x == 0:
        return center.x, None

    steepness = (curr_direction.y - center.y) / (curr_direction.x - center.x)
    y_intercept = center.y - steepness * center.x
    return steepness, y_intercept


def lines_are_parallel(line1, line2):
    return line1[0] == line2[0]


def get_intersection_dist(center: pygame.math.Vector2, curr_direction: pygame.math.Vector2, obstacle: pygame.surface):
    center = Vector2(center)
    curr_direction = Vector2(curr_direction)
    # ray_line = get_line_at_point(Vector2(center), Vector2(curr_direction))
    candidate = float("inf")

    if abs(curr_direction.x) < 0.005:
        if (obstacle.rect.left < center.x < obstacle.rect.right and
                (dy := center.y - obstacle.rect.topleft[1]) * curr_direction.y < 0):
            candidate1 = dy ** 2
            candidate2 = (center.y - obstacle.rect.bottomleft[1]) ** 2
            candidate = min(candidate1, candidate2)

        # print(candidate1, candidate2)
        return None if candidate == float("inf") else math.sqrt(candidate)

    if abs(curr_direction.length()) < 0.01:
        return None  # maybe raise an error

        # top line
    y_intersect = obstacle.rect.topleft[1]
    t = (y_intersect - center.y) / curr_direction.y
    if (t > 0 and
            obstacle.rect.topleft[0] < (x_intersect := center.x + curr_direction.x * t) < obstacle.rect.topright[0]):
        candidate = min(candidate, (x_intersect - center.x) ** 2 + (y_intersect - center.y) ** 2)
        # bottom line
    y_intersect = obstacle.rect.bottomleft[1]
    t = (y_intersect - center.y) / curr_direction.y
    if (t > 0 and
            obstacle.rect.bottomleft[0] < (x_intersect := center.x + curr_direction.x * t) < obstacle.rect.bottomright[
                0]):
        candidate = min(candidate, (x_intersect - center.x) ** 2 + (y_intersect - center.y) ** 2)
        # left line
    x_intersect = obstacle.rect.topleft[0]
    t = (x_intersect - center.x) / curr_direction.x
    if (t > 0 and
            obstacle.rect.topleft[1] < (y_intersect := center.y + curr_direction.y * t) < obstacle.rect.bottomleft[1]):
        candidate = min(candidate, (x_intersect - center.x) ** 2 + (y_intersect - center.y) ** 2)
    # right line
    x_intersect = obstacle.rect.topright[0]
    t = (x_intersect - center.x) / curr_direction.x
    if (t > 0 and
            obstacle.rect.topright[1] < (y_intersect := center.y + curr_direction.y * t) < obstacle.rect.bottomright[
                1]):
        candidate = min(candidate, (x_intersect - center.x) ** 2 + (y_intersect - center.y) ** 2)

    return None if candidate == float("inf") else math.sqrt(candidate)


class Engine:

    # px_density is the sqrt of the amount of actual pxs used to render one virtual px
    def __init__(self, screen: pygame.Surface, player: Maze_Objects.Maze_Player, obstacles, px_density: int = 6):
        self.screen = screen
        self.width, self.height = screen.get_width(), screen.get_height()
        self.center_point = (self.width / 2, self.height / 2)
        self.player = player
        self.obstacles = obstacles
        self.px_density = px_density
        self.resolution = (int(screen.get_width() / self.px_density), int(screen.get_height() / self.px_density))
        self.ray_length = 350
        self.max_obj_height = self.resolution[1]

    def render_scene(self, dt):
        # fill the screen with a color to wipe away anything from last frame
        self.screen.fill("black")
        self.update_movement(self.player, dt)
        px_arr = pygame.PixelArray(self.screen)
        pxs_to_render = self.ray_trace(self.player, self.obstacles)
        for i in range(0, px_arr.shape[0], self.px_density):
            for j in range(0, px_arr.shape[1], self.px_density):
                px_arr[i, j] = graphic_assets.color_of[  # pxs_to_render[i][j]
                    pxs_to_render[int(math.floor(i / self.px_density))][int(math.floor(j / self.px_density))]
                ]

        px_arr.close()
        # self.px_arr.transpose()

        self.screen.blit(self.player.image, self.player.rect.topleft)
        for wall in self.obstacles:
            self.screen.blit(wall.image, wall.rect)

        # flip() the display to put your work on screen
        pygame.display.flip()

    def ray_trace(self, player: Maze_Objects.Maze_Player, obstacles: pygame.sprite.Group) \
            -> list[list[graphic_assets.COLOR]]:
        curr_direction: Vector2 = player.direction.copy()
        curr_direction.rotate_ip(-player.vision_range / 2)

        delta_angle = player.vision_range / self.resolution[0]
        pxs_arr: list[list[graphic_assets.COLOR]] = []
        for i in range(self.resolution[0]):
            min_distance = float("inf")
            for obstacle_sprite in obstacles:
                if (intersection_dist := get_intersection_dist(player.rect.center, curr_direction,
                                                               obstacle_sprite)) is not None:
                    min_distance = min(min_distance, intersection_dist)

            obstacle_height = int(math.ceil(
                # self.max_obj_height * math.exp(-min_distance / self.ray_length / 2)
                self.max_obj_height * (1 - min_distance / self.ray_length)
            )) if 0 < min_distance < self.ray_length else 0
            # obstacle_height = self.resolution[1] // 3
            tmp = abs(self.resolution[1] - obstacle_height) / 2
            tmp = int(math.ceil(tmp))

            pxs_arr.append(
                [graphic_assets.COLOR.SKY for _ in range(tmp)] +
                [graphic_assets.COLOR.WALL for _ in range(obstacle_height)] +
                [graphic_assets.COLOR.GROUND for _ in range(tmp)]
            )
            curr_direction.rotate_ip(delta_angle)

        return pxs_arr

    def update_movement(self, sprite, dt):
        old_x, old_y = sprite.rect.x, sprite.rect.y

        keys = pygame.key.get_pressed()
        mouse = pygame.mouse
        mouse_movement = mouse.get_rel()
        total_movement = pygame.math.Vector2(0, 0)
        if keys[pygame.K_w]:
            total_movement += sprite.direction.x, sprite.direction.y
        if keys[pygame.K_s]:
            total_movement -= sprite.direction.x, sprite.direction.y
        if keys[pygame.K_a]:
            total_movement += sprite.direction.y, -sprite.direction.x
        if keys[pygame.K_d]:
            total_movement += -sprite.direction.y, sprite.direction.x
        if (horizontal_movement := mouse_movement[0]) != 0:
            sprite.change_direction(horizontal_movement * sprite.turning_speed * dt)
        mouse.set_pos(self.center_point)

        if total_movement.length() == 0:
            return

        total_movement.scale_to_length(sprite.speed * dt)
        new_x = old_x + total_movement[0]
        new_y = old_y + total_movement[1]

        if new_x < 0 or new_x > self.width - sprite.rect.width or new_y < 0 or new_y > self.height - sprite.rect.height:
            return

        for wall_sprite in self.obstacles:
            if wall_sprite.rect.colliderect(new_x, new_y, sprite.rect.width, sprite.rect.height):
                return

        sprite.rect.topleft = new_x, new_y
