import random
import sys
import pygame

from spaceinvader.game.assets import AssetLoader
from spaceinvader.game.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    ENEMY_COUNT_START, ENEMY_COUNT_ADD, ENEMY_COUNT_BOSS,
    KILLS_BASE, KILLS_INCREMENT,
    BOSS_SCORE_BONUS, LIFE_BONUS_EVERY,
)
from spaceinvader.game.ui import UI
from spaceinvader.game.screens import run_pause_loop

from spaceinvader.game.entities.player import Player
from spaceinvader.game.entities.bullet import Bullet
from spaceinvader.game.entities.enemy import Enemy
from spaceinvader.game.entities.enemy_bullet import EnemyBullet
from spaceinvader.game.entities.boss import Boss
from spaceinvader.game.entities.nuke import Nuke


class Game:
    """
    Main game loop.

    Bug fixes vs original:
    - kills_this_level is reset to 0 on every level-up (was never reset,
      causing every subsequent kill to trigger another level-up cascade).
    - screen is passed in, not a module-level global.
    - All assets accessed via AssetLoader, not module-level names.
    - Nuke loop variable no longer shadows the `nuke` image asset.
    """

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.clock  = pygame.time.Clock()

        self.player  = Player()
        self.bullet  = Bullet()
        self.level   = 1
        self.score   = 0
        self.kills   = 0
        self.kills_this_level = 0    # BUG FIX: was never reset on level-up

        self.enemies       = [Enemy(self.level) for _ in range(ENEMY_COUNT_START)]
        self.enemy_bullets: list[EnemyBullet] = []
        self.boss:          Boss | None = None
        self.nukes:         list[Nuke]  = []
        self.boss_active    = False

    # ------------------------------------------------------------------
    # Level progression
    # ------------------------------------------------------------------
    def _kills_needed(self) -> int:
        return KILLS_BASE + (self.level - 1) * KILLS_INCREMENT

    def _maybe_award_life(self):
        if self.level % LIFE_BONUS_EVERY == 0:
            self.player.lives += 1

    def _level_up(self):
        self.level += 1
        self.kills_this_level = 0    # BUG FIX: reset the counter on every level-up
        self._maybe_award_life()
        UI.show_level_up(self.screen)

    def _spawn_boss_level(self):
        self._level_up()
        self.boss        = Boss(self.level)
        self.boss_active = True
        self.enemies     = [Enemy(self.level) for _ in range(ENEMY_COUNT_BOSS)]

    def _spawn_normal_level(self):
        self._level_up()
        self.enemies.extend([Enemy(self.level) for _ in range(ENEMY_COUNT_ADD)])

    # ------------------------------------------------------------------
    # Update methods
    # ------------------------------------------------------------------
    def _update_enemies(self):
        for enemy in self.enemies:
            enemy.move()

            # Enemy reaches bottom → player loses a life, enemy respawns
            if enemy.y > SCREEN_HEIGHT:
                self.player.lives -= 1
                enemy.respawn()
                continue           # don't check shooting / collision this frame

            # Enemy fires
            if random.random() < enemy.shoot_prob:
                self.enemy_bullets.append(
                    EnemyBullet(enemy.x + 35, enemy.y + 80)
                )

            # Player bullet hits enemy
            if self.bullet.active and enemy.is_collision(self.bullet.x, self.bullet.y):
                self.bullet.reset()
                self.score += 1
                self.kills += 1
                self.kills_this_level += 1
                enemy.respawn()

                if self.kills_this_level >= self._kills_needed():
                    if (self.level + 1) % 3 == 0:
                        self._spawn_boss_level()
                    else:
                        self._spawn_normal_level()

    def _update_enemy_bullets(self):
        player_cx = self.player.x + 50
        player_cy = self.player.y + 50
        for b in self.enemy_bullets:
            b.move()
            b.draw(self.screen)
            if b.is_collision(player_cx, player_cy):
                self.player.lives -= 1
                b.state = "ready"
        self.enemy_bullets = [b for b in self.enemy_bullets if b.active]

    def _update_boss(self):
        if not (self.boss_active and self.boss):
            return
        self.boss.move()
        self.boss.draw(self.screen)

        # Boss fires nukes
        if random.random() < self.boss.shoot_prob:
            self.nukes.append(Nuke(self.boss.x + 150, self.boss.y + 300))

        # Player bullet hits boss
        if self.bullet.active and self.boss.is_collision(self.bullet.x, self.bullet.y):
            self.boss.health -= 1
            self.bullet.reset()
            if self.boss.defeated:
                self.boss_active = False
                self.boss        = None
                self.score      += BOSS_SCORE_BONUS
                self._level_up()
                self.enemies.extend([Enemy(self.level) for _ in range(ENEMY_COUNT_ADD)])

    def _update_nukes(self):
        player_cx = self.player.x + 50
        player_cy = self.player.y + 50
        for n in self.nukes:
            n.move()
            n.draw(self.screen)
            if n.is_collision(player_cx, player_cy):
                self.player.lives -= 1
                n.state = "ready"
        self.nukes = [n for n in self.nukes if n.active]

    def _handle_game_over(self):
        UI.show_game_over(self.screen)
        self.player.lives = 3
        self.player.reset_position()

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------
    def run(self):
        while True:
            self.screen.blit(AssetLoader.background, (0, 0))

            # ---- Events ----
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.player.change_x = -10
                    elif event.key == pygame.K_RIGHT:
                        self.player.change_x = 10
                    elif event.key == pygame.K_SPACE:
                        self.bullet.fire(self.player.x)
                    elif event.key == pygame.K_p:
                        run_pause_loop(self.screen)
                if event.type == pygame.KEYUP:
                    if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        self.player.change_x = 0

            # ---- Update ----
            self.player.move()
            self.bullet.move()
            self._update_enemies()
            self._update_enemy_bullets()
            self._update_boss()
            self._update_nukes()

            # ---- Game over check ----
            if self.player.lives <= 0:
                self._handle_game_over()
                continue

            # ---- Draw ----
            self.player.draw(self.screen)
            self.bullet.draw(self.screen)
            for enemy in self.enemies:
                enemy.draw(self.screen)

            UI.show_score(self.screen, self.score)
            UI.show_level(self.screen, self.level)
            UI.show_lives(self.screen, self.player.lives)

            pygame.display.flip()
            self.clock.tick(60)
