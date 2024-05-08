import pygame
import Maze_Objects
import graphic_assets


def get_line_at_point(center: pygame.math.Vector2, curr_direction: pygame.math.Vector2):
    return get_line_from_points(center, center + curr_direction)


def get_line_from_points(center, curr_direction):
    if curr_direction.x - center.x == 0:
        return center.x, None

    steepness = (curr_direction.y - center.y) / (curr_direction.x - center.x)
    y_intercept = center.y - steepness * center.x
    return steepness, y_intercept


def lines_are_parallel(line1, line2):
    return line1[0] == line2[0]


def get_intersection(center, curr_direction, obstacle: pygame.surface):
    ray_line = get_line_from_points(center, curr_direction)
    wall_lines = [
        get_line_from_points(obstacle.rect.topleft, obstacle.rect.bottomleft),
        get_line_from_points(obstacle.rect.bottomleft, obstacle.rect.bottomright),
        get_line_from_points(obstacle.rect.bottomright, obstacle.rect.topright),
        get_line_from_points(obstacle.rect.topright, obstacle.rect.topleft)
    ]

    if ray_line[1] is None:
        x = ray_line[0]
        for wall_line in wall_lines:
            if obstacle.rect.topleft.x < x < obstacle.rect.topright.x:
                candidate1 = pygame.math.Vector2(x, obstacle.rect.topleft.y)
                candidate2 = pygame.math.Vector2(x, obstacle.rect.bottomleft.y)
                return candidate1 if candidate1.length() <= candidate2.length() else candidate2

    for wall_line in wall_lines:
        if lines_are_parallel(ray_line, wall_line):
            continue
        if wall_line[1] is None:
            x = wall_line[0]
            if ray_line[0] == x:
                return pygame.math.Vector2(x, ray_line[0] * x + ray_line[1])
            continue


class Engine:

    # px_density is the sqrt of the amount of actual pxs used to render one virtual px
    def __init__(self, screen: pygame.Surface, player: Maze_Objects.Maze_Player, obstacles, px_density: int = 1):
        self.screen = screen
        self.width, self.height = screen.get_width(), screen.get_height()
        self.center_point = (self.width / 2, self.height / 2)
        self.player = player
        self.obstacles = obstacles
        self.px_density = px_density
        self.resolution = (int(screen.get_width() / px_density), int(screen.get_height() / px_density))
        # self.ray_length = 1000
        self.px_arr = pygame.PixelArray(self.screen)

    def animate(self, dt):
        # fill the screen with a color to wipe away anything from last frame
        self.screen.fill("black")
        self.update_movement(self.player, dt)

        pxs_to_render = self.ray_trace(self.player, self.obstacles)

        for i in range(0, self.px_arr.shape[0], self.px_density):
            for j in range(0, self.px_arr.shape[1], self.px_density):
                self.px_arr[i][j] = (255, 255, 255)

        # self.screen.blit(self.player.image, self.player.rect.topleft)
        # for wall in self.obstacles:
        #     self.screen.blit(wall.image, wall.rect)

        # flip() the display to put your work on screen
        pygame.display.flip()

    def ray_trace(self, player: Maze_Objects.Maze_Player, obstacles) -> list[list[tuple[graphic_assets.COLOR]]]:
        curr_direction = player.direction.rotate(player.vision_range / 2)
        delta_angle = player.vision_range / self.resolution[0]
        for i in range(self.resolution[0]):
            min_distance = float("inf")
            for obstacle_sprite in obstacles:
                if (intersection := get_intersection(curr_direction, obstacle_sprite)) is not None:
                    obstacle_distance = min(min_distance, (intersection - player.rect.center).length())

            curr_direction.rotate_ip(delta_angle)

        return []

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
