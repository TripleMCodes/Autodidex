"""
main.py — Space Invader entry point.

pygame.init(), screen creation, and asset loading all happen here,
inside main(), so that importing any game module never triggers them.
This is what allows SpaceInvaderWidget to safely `import space_invader`
without crashing at import time.
"""

import sys
import pygame
from pathlib import Path

from spaceinvader.game.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from spaceinvader.game.assets import AssetLoader
from spaceinvader.game.screens import show_start_screen
from spaceinvader.game.game import Game


def main():
    pygame.init()
    pygame.display.set_caption("Space Invasion OOP Deluxe")

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Load all assets now that pygame is initialised
    base_path = Path(__file__).parent
    AssetLoader.load(base_path)

    # Set window icon using the local asset (not the hardcoded D:/ path)
    pygame.display.set_icon(AssetLoader.icon_img)

    show_start_screen(screen)
    Game(screen).run()


if __name__ == "__main__":
    main()
