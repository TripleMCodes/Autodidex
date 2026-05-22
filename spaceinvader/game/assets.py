"""
AssetLoader
-----------
All pygame asset loading is deferred behind load().
This means importing this module never calls pygame — only
calling AssetLoader.load() does, which is safe to do after
pygame.init() inside main() or Game.__init__().

Fixes the critical bug where `import space_invader` crashed
SpaceInvaderWidget at import time because pygame.image.load()
ran unconditionally at module scope.
"""

import pygame
from pathlib import Path
from spaceinvader.game.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    PLAYER_SIZE, ENEMY_SIZE, BOSS_SIZE, BULLET_SIZE, NUKE_SIZE,
    FONT_SMALL, FONT_BIG, FONT_LEVEL,
)


class AssetLoader:
    """
    Loads and stores all game assets.
    Call AssetLoader.load(base_path) once after pygame.init().
    Access assets via the class attributes afterwards.
    """

    # Images
    background:  pygame.Surface
    player_img:  pygame.Surface
    enemy_img:   pygame.Surface
    boss_img:    pygame.Surface
    bullet_img:  pygame.Surface
    nuke_img:    pygame.Surface
    heart_img:   pygame.Surface
    icon_img:    pygame.Surface

    # Fonts
    font:       pygame.font.Font
    big_font:   pygame.font.Font
    level_font: pygame.font.Font

    _loaded = False

    @classmethod
    def load(cls, base_path: Path):
        if cls._loaded:
            return

        img_path = base_path / "img"

        def _img(filename, size):
            return pygame.transform.scale(
                pygame.image.load(img_path / filename), size
            )

        cls.background = _img("background.webp", (SCREEN_WIDTH, SCREEN_HEIGHT))
        cls.player_img  = _img("player.bmp",           PLAYER_SIZE)
        cls.enemy_img   = _img("ufo.png",                                   ENEMY_SIZE)
        cls.boss_img    = _img("boss.png", BOSS_SIZE)
        cls.bullet_img  = _img("bullet.png",                                BULLET_SIZE)
        cls.nuke_img    = _img("nuke.png",    NUKE_SIZE)
        cls.heart_img   = _img("heart.png",             (32, 32))

        icon_file = img_path / "ufo.png"
        cls.icon_img = pygame.image.load(icon_file)

        # Fonts
        cls.font       = pygame.font.Font("freesansbold.ttf", FONT_SMALL)
        cls.big_font   = pygame.font.Font("freesansbold.ttf", FONT_BIG)
        cls.level_font = pygame.font.Font("freesansbold.ttf", FONT_LEVEL)

        cls._loaded = True
