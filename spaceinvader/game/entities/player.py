import pygame
from spaceinvader.game.assets import AssetLoader
from spaceinvader.game.constants import SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_START_LIVES, PLAYER_SPEED


class Player:
    def __init__(self):
        self.image    = AssetLoader.player_img
        self.x        = SCREEN_WIDTH // 2
        self.y        = SCREEN_HEIGHT - 95
        self.change_x = 0
        self.lives    = PLAYER_START_LIVES

    def move(self):
        self.x += self.change_x
        self.x = max(0, min(self.x, SCREEN_WIDTH - 100))

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, (self.x, self.y))

    def reset_position(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 95
