# ── Screen ────────────────────────────────────────────────────────────────────
SCREEN_WIDTH  = 1390
SCREEN_HEIGHT = 700

# ── Colours ────────────────────────────────────────────────────────────────────
WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
YELLOW = (255, 255, 0)
CYAN   = (0,   255, 255)
SCORE_COLOUR = (217, 11, 214)

# ── Player ─────────────────────────────────────────────────────────────────────
PLAYER_SPEED      = 10
PLAYER_START_LIVES = 3
PLAYER_SIZE       = (100, 100)

# ── Bullet ─────────────────────────────────────────────────────────────────────
BULLET_SIZE       = (32, 32)
BULLET_SPEED      = 50        # pixels per frame, upward
ENEMY_BULLET_SPEED = 15       # pixels per frame, downward

# ── Enemy ──────────────────────────────────────────────────────────────────────
ENEMY_SIZE         = (100, 100)
ENEMY_COUNT_START  = 10
ENEMY_COUNT_ADD    = 5        # enemies added per level-up
ENEMY_COUNT_BOSS   = 5        # enemies during a boss level
KILLS_BASE         = 10       # kills needed on level 1
KILLS_INCREMENT    = 2        # extra kills needed per level

# ── Boss ───────────────────────────────────────────────────────────────────────
BOSS_SIZE          = (300, 300)
BOSS_SCORE_BONUS   = 10
BOSS_SHOOT_PROB    = 0.02

# ── Nuke ───────────────────────────────────────────────────────────────────────
NUKE_SIZE  = (50, 50)
NUKE_SPEED = 12

# ── Progression ────────────────────────────────────────────────────────────────
LEVEL_EVERY_N_KILLS  = 3      # boss spawns when (level % 3 == 0)
LIFE_BONUS_EVERY     = 5      # extra life every N levels
LUMENS_PER_LEVEL_UP  = 10     # lumen reward on level up (if integrated)

# ── Font sizes ─────────────────────────────────────────────────────────────────
FONT_SMALL  = 32
FONT_BIG    = 64
FONT_LEVEL  = 48
