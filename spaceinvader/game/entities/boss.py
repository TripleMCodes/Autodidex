import math
import pygame
from spaceinvader.game.assets import AssetLoader
from spaceinvader.game.constants import SCREEN_WIDTH, BOSS_SHOOT_PROB


class Boss:
    COLLISION_RADIUS = 120

    def __init__(self, level: int):
        self.image       = AssetLoader.boss_img
        self.x           = SCREEN_WIDTH // 2 - 150
        self.y           = 30
        self.health      = 10 + 5 * (level // 3)
        self.change_x    = 4 + 0.5 * (level // 3)
        self.direction   = 1
        self.shoot_prob  = BOSS_SHOOT_PROB

    def move(self):
        self.x += self.change_x * self.direction
        if self.x <= 0 or self.x >= SCREEN_WIDTH - 300:
            self.direction *= -1

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, (self.x, self.y))

    def is_collision(self, bullet_x: int, bullet_y: int) -> bool:
        dist = math.sqrt((self.x + 150 - bullet_x) ** 2 + (self.y + 150 - bullet_y) ** 2)
        return dist < self.COLLISION_RADIUS

    @property
    def defeated(self) -> bool:
        return self.health <= 0
