import math
import pygame
from spaceinvader.game.assets import AssetLoader
from spaceinvader.game.constants import SCREEN_HEIGHT, NUKE_SPEED


class Nuke:
    """
    Boss projectile that falls toward the player.

    The original named the loaded image asset `nuke` at module level,
    then used `nuke` as the loop variable in `for nuke in self.nukes`.
    This shadowed the asset mid-loop, corrupting the image reference.
    Fixed by loading the image through AssetLoader (nuke_img) instead.
    """

    COLLISION_RADIUS = 60

    def __init__(self, x: int, y: int):
        self.image    = AssetLoader.nuke_img   # was: nuke (module-level name collision)
        self.x        = x
        self.y        = y
        self.change_y = NUKE_SPEED
        self.state    = "fire"

    def move(self):
        if self.state == "fire":
            self.y += self.change_y
            if self.y > SCREEN_HEIGHT:
                self.state = "ready"

    def draw(self, screen: pygame.Surface):
        if self.state == "fire":
            screen.blit(self.image, (self.x, self.y))

    def is_collision(self, player_cx: int, player_cy: int) -> bool:
        dist = math.sqrt((self.x - player_cx) ** 2 + (self.y - player_cy) ** 2)
        return dist < self.COLLISION_RADIUS

    @property
    def active(self) -> bool:
        return self.state == "fire"
