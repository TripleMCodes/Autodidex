import pygame
from spaceinvader.game.assets import AssetLoader
from spaceinvader.game.constants import SCREEN_HEIGHT, BULLET_SPEED


class Bullet:
    def __init__(self):
        self.image    = AssetLoader.bullet_img
        self.x        = 0
        self.y        = SCREEN_HEIGHT - 95
        self.change_y = BULLET_SPEED
        self.state    = "ready"

    def fire(self, player_x: int):
        if self.state == "ready":
            self.x     = player_x + 35
            self.y     = SCREEN_HEIGHT - 95
            self.state = "fire"

    def reset(self):
        self.state = "ready"
        self.y     = SCREEN_HEIGHT - 95

    def move(self):
        if self.state == "fire":
            self.y -= self.change_y
            if self.y <= 0:
                self.reset()

    def draw(self, screen: pygame.Surface):
        if self.state == "fire":
            screen.blit(self.image, (self.x, self.y))

    @property
    def active(self) -> bool:
        return self.state == "fire"
