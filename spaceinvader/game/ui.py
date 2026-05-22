import sys
import pygame
from spaceinvader.game.assets import AssetLoader
from spaceinvader.game.constants import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK


class UI:
    """
    Stateless HUD renderer.  Every method receives the surface to draw on
    so nothing here touches a global `screen` object.

    Fixed: show_level used a hardcoded x=1150 which broke on different
    screen widths.  Now computed relative to SCREEN_WIDTH.
    """

    @staticmethod
    def show_score(screen: pygame.Surface, score: int):
        text = AssetLoader.font.render(f"Score: {score}", True, (217, 11, 214))
        screen.blit(text, (20, 20))

    @staticmethod
    def show_level(screen: pygame.Surface, level: int):
        text = AssetLoader.font.render(f"Level: {level}", True, (0, 255, 255))
        # Right-align: was hardcoded 1150, now computed
        x = SCREEN_WIDTH - text.get_width() - 20
        screen.blit(text, (x, 20))

    @staticmethod
    def show_lives(screen: pygame.Surface, lives: int):
        for i in range(lives):
            screen.blit(AssetLoader.heart_img, (20 + i * 40, 60))

    @staticmethod
    def show_game_over(screen: pygame.Surface):
        over_text   = AssetLoader.big_font.render("GAME OVER", True, BLACK)
        prompt_text = AssetLoader.font.render("Press 'R' to Continue", True, (255, 255, 255))
        screen.blit(over_text,   (SCREEN_WIDTH // 2 - over_text.get_width() // 2, 320))
        screen.blit(prompt_text, (SCREEN_WIDTH // 2 - prompt_text.get_width() // 2, 400))
        pygame.display.update()
        # Wait for R key
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    waiting = False

    @staticmethod
    def show_level_up(screen: pygame.Surface):
        text = AssetLoader.level_font.render("LEVEL UP!", True, (255, 255, 0))
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 300))
        pygame.display.update()
        pygame.time.delay(1500)

    @staticmethod
    def show_pause(screen: pygame.Surface):
        text = AssetLoader.font.render("PAUSED — Press 'P' to Resume", True, (255, 255, 0))
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2))
        pygame.display.flip()
