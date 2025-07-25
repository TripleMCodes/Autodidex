import pygame
import random
import math
import sys
from pathlib import Path

# ========== Initialize Pygame ==========
pygame.init()
pygame.display.set_caption("Space Invasion OOP Deluxe")

# ========== Constants ==========
SCREEN_WIDTH = 1390
SCREEN_HEIGHT = 700
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# ========== Screen & Icon ==========
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
icon = pygame.image.load("D:/ufo.png")
pygame.display.set_icon(icon)

# ========== Load Assets ==========
base_path = Path(__file__).parent
base_path = base_path / "spaceinvader" / "img"
boss = pygame.transform.scale(pygame.image.load(base_path / "—Pngtree—blue ufo alien spaceship_5455324.png"), (300, 300))
nuke =  pygame.transform.scale(pygame.image.load(base_path / "—Pngtree—nuclear bomb icon_7430380.png"), (50, 50))
background = pygame.transform.scale(pygame.image.load(base_path / "file-RctmKuWwQYXUGUgfoKRVCOF8.webp"), (SCREEN_WIDTH, SCREEN_HEIGHT))
player_img = pygame.transform.scale(pygame.image.load(base_path / ".trashed-1733155705-pngegg.bmp"), (100, 100))
enemy_img = pygame.transform.scale(pygame.image.load(base_path / "ufo.png"), (100, 100))
bullet_img = pygame.transform.scale(pygame.image.load(base_path / "bullet.png"), (32, 32))
heart_img = pygame.transform.scale(pygame.image.load(base_path / "pngimg.com - heart_PNG681.png"), (32, 32))

# ========== Fonts ==========
font = pygame.font.Font('freesansbold.ttf', 32)
big_font = pygame.font.Font('freesansbold.ttf', 64)
level_font = pygame.font.Font('freesansbold.ttf', 48)

# ========== Classes ==========
class Boss:
    def __init__(self, level):
        self.image = boss
        self.x = SCREEN_WIDTH // 2 - 150
        self.y = 30
        self.health = 10 + 5 * (level // 3)
        self.change_x = 4 + 0.5 * (level // 3)
        self.direction = 1
        self.shoot_prob = 0.02  # Boss shoots nukes more often

    def move(self):
        self.x += self.change_x * self.direction
        if self.x <= 0 or self.x >= SCREEN_WIDTH - 300:
            self.direction *= -1

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

    def is_collision(self, bullet_x, bullet_y):
        distance = math.sqrt((self.x + 150 - bullet_x) ** 2 + (self.y + 150 - bullet_y) ** 2)
        return distance < 120


class Nuke:
    def __init__(self, x, y):
        self.image = nuke
        self.x = x
        self.y = y
        self.change_y = 12
        self.state = "fire"

    def move(self):
        if self.state == "fire":
            self.y += self.change_y
            if self.y > SCREEN_HEIGHT:
                self.state = "ready"

    def draw(self):
        if self.state == "fire":
            screen.blit(self.image, (self.x, self.y))

    def is_collision(self, player_x, player_y):
        distance = math.sqrt((self.x - player_x) ** 2 + (self.y - player_y) ** 2)
        return distance < 60

class Player:
    def __init__(self):
        self.image = player_img
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 95
        self.change_x = 0
        self.lives = 3

    def move(self):
        self.x += self.change_x
        self.x = max(0, min(self.x, SCREEN_WIDTH - 100))

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

class Bullet:
    def __init__(self):
        self.image = bullet_img
        self.x = 0
        self.y = SCREEN_HEIGHT - 95
        self.change_y = 50
        self.state = "ready"

    def fire(self, x):
        if self.state == "ready":
            self.x = x + 35
            self.y = SCREEN_HEIGHT - 95
            self.state = "fire"

    def move(self):
        if self.state == "fire":
            self.y -= self.change_y
            if self.y <= 0:
                self.state = "ready"

    def draw(self):
        if self.state == "fire":
            screen.blit(self.image, (self.x, self.y))

class Enemy:
    def __init__(self, level):
        self.image = enemy_img
        self.x = random.randint(0, SCREEN_WIDTH - 100)
        self.y = random.randint(50, 100)
        self.change_x = 2 + 0.4 * (level - 1)   # Slower at start, increases with level
        self.change_y = 5 + 0.1 * (level - 1)   # Slower at start, increases with level
        self.shoot_prob = 0.002 + 0.0002 * level

    def move(self):
        self.x += self.change_x
        if self.x <= 0 or self.x >= SCREEN_WIDTH - 100:
            self.change_x *= -1
            self.y += self.change_y

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

    def is_collision(self, bullet_x, bullet_y):
        distance = math.sqrt((self.x - bullet_x) ** 2 + (self.y - bullet_y) ** 2)
        return distance < 27

class EnemyBullet:
    def __init__(self, x, y):
        self.image = bullet_img
        self.x = x
        self.y = y
        self.change_y = 15
        self.state = "fire"

    def move(self):
        if self.state == "fire":
            self.y += self.change_y
            if self.y > SCREEN_HEIGHT:
                self.state = "ready"

    def draw(self):
        if self.state == "fire":
            screen.blit(self.image, (self.x, self.y))

    def is_collision(self, player_x, player_y):
        distance = math.sqrt((self.x - player_x) ** 2 + (self.y - player_y) ** 2)
        return distance < 40

class UI:
    @staticmethod
    def show_score(score):
        score_text = font.render(f"Score: {score}", True, (217, 11, 214))
        screen.blit(score_text, (20, 20))

    @staticmethod
    def show_level(level):
        level_text = font.render(f"Level: {level}", True, (0, 255, 255))
        screen.blit(level_text, (1150, 20))

    @staticmethod
    def show_lives(lives):
        for i in range(lives):
            screen.blit(heart_img, (20 + i * 40, 60))

    @staticmethod
    def show_game_over():
        over_text = big_font.render("GAME OVER", True, BLACK)
        prompt_text = font.render("Press 'R' to Continue", True, (255, 255, 255))
        screen.blit(over_text, (559, 320))
        screen.blit(prompt_text, (SCREEN_WIDTH // 2 - prompt_text.get_width() // 2, 400))
        pygame.display.update()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        waiting = False

    @staticmethod
    def show_level_up():
        text = level_font.render("LEVEL UP!", True, (255, 255, 0))
        screen.blit(text, (580, 300))
        pygame.display.update()
        pygame.time.delay(1500)

def show_start_screen():
    waiting = True
    while waiting:
        screen.fill((0, 0, 0))
        title_text = big_font.render("SPACE INVADER", True, (255, 255, 0))
        prompt_text = font.render("Press 'S' to Start", True, (255, 255, 255))
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 200))
        screen.blit(prompt_text, (SCREEN_WIDTH // 2 - prompt_text.get_width() // 2, 350))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    waiting = False

class Game:
    def __init__(self):
        self.player = Player()
        self.bullet = Bullet()
        self.level = 1
        self.score = 0
        self.kills = 0
        self.kills_this_level = 0
        self.enemies = [Enemy(self.level) for _ in range(10)]
        self.enemy_bullets = []
        self.boss = None
        self.nukes = []
        self.boss_active = False

    def pause(self):
        paused = True
        pause_text = font.render("PAUSED - Press 'P' to Resume", True, (255, 255, 0))
        while paused:
            screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        paused = False

    def run(self):
        while True:
            screen.blit(background, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.player.change_x = -10
                    if event.key == pygame.K_RIGHT:
                        self.player.change_x = 10
                    if event.key == pygame.K_SPACE:
                        self.bullet.fire(self.player.x)
                    if event.key == pygame.K_p:
                        self.pause()

                if event.type == pygame.KEYUP:
                    if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                        self.player.change_x = 0

            self.player.move()
            self.bullet.move()

            # --- Enemy logic ---
            for enemy in self.enemies:
                enemy.move()
                if enemy.y > SCREEN_HEIGHT:
                    self.player.lives -= 1
                    enemy.y = random.randint(50, 100)

                # Enemy shooting logic
                if random.random() < enemy.shoot_prob:
                    bullet_x = enemy.x + 35
                    bullet_y = enemy.y + 80
                    self.enemy_bullets.append(EnemyBullet(bullet_x, bullet_y))

                if enemy.is_collision(self.bullet.x, self.bullet.y) and self.bullet.state == "fire":
                    self.bullet.state = "ready"
                    self.bullet.y = SCREEN_HEIGHT - 95
                    self.score += 1
                    self.kills += 1
                    self.kills_this_level += 1
                    enemy.x = random.randint(0, SCREEN_WIDTH - 100)
                    enemy.y = random.randint(50, 100)

                    kills_to_level = 10 + (self.level - 1) * 2  # 10 for level 1, 12 for level 2, 14 for level 3, etc.
                    if self.kills_this_level >= kills_to_level:
                        # level up logic
                        # If next level is a boss level, spawn boss and pause level up
                        if (self.level + 1) % 3 == 0:
                            self.level += 1
                            if self.level % 5 == 0:
                                self.player.lives += 1
                            UI.show_level_up()
                            self.boss = Boss(self.level)
                            self.boss_active = True
                            # Only five new enemies for boss level
                            self.enemies = [Enemy(self.level) for _ in range(5)]
                        else:
                            self.level += 1
                            if self.level % 5 == 0:
                                self.player.lives += 1
                            UI.show_level_up()
                            self.enemies.extend([Enemy(self.level) for _ in range(5)])

            # --- Enemy bullets logic ---
            for bullet in self.enemy_bullets:
                bullet.move()
                bullet.draw()
                if bullet.is_collision(self.player.x + 50, self.player.y + 50):  # Center of player
                    self.player.lives -= 1
                    bullet.state = "ready"

            # Remove bullets that are off screen or have hit
            self.enemy_bullets = [b for b in self.enemy_bullets if b.state == "fire"]

            # --- Boss logic ---
            if self.boss_active and self.boss:
                self.boss.move()
                self.boss.draw()
                # Boss shoots nukes at random
                if random.random() < self.boss.shoot_prob:
                    nuke_x = self.boss.x + 150
                    nuke_y = self.boss.y + 300
                    self.nukes.append(Nuke(nuke_x, nuke_y))
                # Player bullet hits boss
                if self.bullet.state == "fire" and self.boss.is_collision(self.bullet.x, self.bullet.y):
                    self.boss.health -= 1
                    self.bullet.state = "ready"
                    self.bullet.y = SCREEN_HEIGHT - 95
                    if self.boss.health <= 0:
                        self.boss_active = False
                        self.boss = None
                        self.score += 10  # Bonus for defeating boss
                        self.level += 1
                        if self.level % 5 == 0:
                            self.player.lives += 1
                        UI.show_level_up()
                        self.enemies.extend([Enemy(self.level) for _ in range(5)])

            # --- Nuke logic ---
            for nuke in self.nukes:
                nuke.move()
                nuke.draw()
                if nuke.is_collision(self.player.x + 50, self.player.y + 50):
                    self.player.lives -= 1
                    nuke.state = "ready"

            # Remove nukes that are off screen or have hit
            self.nukes = [n for n in self.nukes if n.state == "fire"]

            if self.player.lives <= 0:
                UI.show_game_over()
                # Restore player lives and continue (keep level, score, etc.)
                self.player.lives = 3
                # Optionally, you can also reset player position or other things here
                self.player.x = SCREEN_WIDTH // 2
                self.player.y = SCREEN_HEIGHT - 95
                continue  # Continue the game loop

            self.player.draw()
            self.bullet.draw()
            for enemy in self.enemies:
                enemy.draw()

            UI.show_score(self.score)
            UI.show_level(self.level)
            UI.show_lives(self.player.lives)

            pygame.display.flip()

def main():
    show_start_screen()
    Game().run()

# if __name__ == "__main__":
#     main()