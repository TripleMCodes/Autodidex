import math
import random
import pygame
from spaceinvader.game.assets import AssetLoader
from spaceinvader.game.constants import SCREEN_WIDTH, SCREEN_HEIGHT


class Enemy:
    COLLISION_RADIUS = 27

    def __init__(self, level: int):
        self.image       = AssetLoader.enemy_img
        self.x           = random.randint(0, SCREEN_WIDTH - 100)
        self.y           = random.randint(50, 100)
        self.change_x    = 2 + 0.4 * (level - 1)
        self.change_y    = 5 + 0.1 * (level - 1)
        self.shoot_prob  = 0.002 + 0.0002 * level

    def move(self):
        self.x += self.change_x
        if self.x <= 0 or self.x >= SCREEN_WIDTH - 100:
            self.change_x *= -1
            self.y        += self.change_y

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, (self.x, self.y))

    def respawn(self):
        """Reset to a random top position (called when enemy breaches the bottom)."""
        self.x = random.randint(0, SCREEN_WIDTH - 100)
        self.y = random.randint(50, 100)

    def is_collision(self, bullet_x: int, bullet_y: int) -> bool:
        dist = math.sqrt((self.x - bullet_x) ** 2 + (self.y - bullet_y) ** 2)
        return dist < self.COLLISION_RADIUS
