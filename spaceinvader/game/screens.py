import sys
import pygame
from spaceinvader.game.assets import AssetLoader
from spaceinvader.game.constants import SCREEN_WIDTH, SCREEN_HEIGHT


def show_start_screen(screen: pygame.Surface):
    """Block until the player presses S."""
    clock = pygame.time.Clock()
    while True:
        screen.fill((0, 0, 0))
        title  = AssetLoader.big_font.render("SPACE INVADER", True, (255, 255, 0))
        prompt = AssetLoader.font.render("Press 'S' to Start", True, (255, 255, 255))
        screen.blit(title,  (SCREEN_WIDTH // 2 - title.get_width()  // 2, 200))
        screen.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, 350))
        pygame.display.flip()
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                return


def run_pause_loop(screen: pygame.Surface):
    """Block until the player presses P again."""
    text = AssetLoader.font.render("PAUSED — Press 'P' to Resume", True, (255, 255, 0))
    clock = pygame.time.Clock()
    while True:
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2))
        pygame.display.flip()
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                return
