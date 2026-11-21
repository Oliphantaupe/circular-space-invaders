"""Game design data: player and enemy stats, waves, cycle scaling and upgrades.

Tune the game here without touching the logic (game_logic.py).
Every class below only holds values; their behaviour is in game_logic.py.
"""
from pygame.math import Vector2


class Ship:
    """Anything with health that can be hit: the player and every enemy."""
    max_health = 1
    radius = 10                             # hitbox
    color = "white"

    def __init__(self, pos: Vector2):
        self.pos = Vector2(pos)
        self.health = self.max_health

    @property
    def alive(self) -> bool:
        return self.health > 0


class Player(Ship):
    """Moves with Z/Q/S/D, aims at the mouse and shoots."""
    max_health = 100
    radius = 20
    color = (80, 200, 255)
    movement_speed = 200                    # pixels / second
    # Shot stats: copied onto each projectile when fired, modified by upgrades.
    damage = 10
    shot_speed = 200                        # pixels / second
    shot_cooldown = 0.2                     # seconds between shots
    projectile_count = 1                    # projectiles per shot, fanned around the aim direction
    projectile_gap = 10                     # degrees between two projectiles of the same shot
    defense = 0                             # flat reduction of contact damage (min 1 damage taken)

    def __init__(self, pos: Vector2):
        super().__init__(pos)
        self.angle = -90                    # degrees, -90 = facing up
        self.cooldown_timer = 0.0
        self.upgrades: list[str] = []       # labels of the upgrades picked so far

    @property
    def direction(self) -> Vector2:         # unit vector of facing direction
        return Vector2(1, 0).rotate(self.angle)


class Enemy(Ship):
    """Flies straight at the player and dies on contact.

    Health and contact damage grow by STAT_GROWTH_PER_CYCLE each cycle, score is multiplied by the cycle.
    New enemy type: subclass Enemy, set its values and add it to ENEMY_CLASSES.
    """
    speed = 0                               # pixels / second
    contact_damage = 0                      # health lost by the player on contact
    score = 0                               # points per kill at cycle 1


class BasicEnemy(Enemy):
    max_health = 10
    speed = 10
    contact_damage = 10
    radius = 15
    score = 10
    color = "red"


class EliteEnemy(Enemy):
    max_health = 25
    speed = 8
    contact_damage = 20
    radius = 25
    score = 30
    color = "orange"


class BossEnemy(Enemy):
    max_health = 100
    speed = 6
    contact_damage = 60
    radius = 50
    score = 200
    color = "purple"


# Names used in WAVES -> enemy class.
ENEMY_CLASSES = {"enemy": BasicEnemy, "elite": EliteEnemy, "boss": BossEnemy}

# One cycle = all these waves in order. The game then starts the next, harder cycle.
WAVES = [
    {"enemy": 5},
    {"enemy": 7, "elite": 1},
    {"enemy": 6, "elite": 2},
    {"enemy": 8, "elite": 3},
    {"enemy": 5, "elite": 2, "boss": 1},
]

# Scaling between cycles: wave counts are multiplied by the cycle number,
# enemy health and contact damage by STAT_GROWTH_PER_CYCLE ** (cycle - 1).
STAT_GROWTH_PER_CYCLE = 1.5

SPAWN_RADIUS = 400                  # enemies appear on a ring this far from the player
SPAWN_DELAY = 0.5                   # seconds between two spawns

WAVE_END_HEAL = 0.20                # fraction of max health restored when a wave is cleared

UPGRADES_OFFERED = 3                # upgrades to choose from, picked with keys 1/2/3

# Upgrades: each one has a label and a list of effects.
# An effect changes one Player stat: "add" adds "amount" to it, "multiply" multiplies it by "amount".
# Player stats: max_health, damage, defense, projectile_count, projectile_gap, shot_speed,
# shot_cooldown (lower = faster fire), movement_speed.

# Small upgrade after each wave, from a popup at the bottom of the screen.
WAVE_UPGRADES = {
    "health": {"label": "Max health +10%", "effects": [
        {"stat": "max_health", "operation": "multiply", "amount": 1.10},
    ]},
    "attack": {"label": "Damage +15%", "effects": [
        {"stat": "damage", "operation": "multiply", "amount": 1.15},
    ]},
    "defense": {"label": "Defense +1", "effects": [
        {"stat": "defense", "operation": "add", "amount": 1},
    ]},
    "attack_speed": {"label": "Fire rate +10%", "effects": [
        {"stat": "shot_cooldown", "operation": "multiply", "amount": 1 / 1.10},
    ]},
    "move_speed": {"label": "Move speed +10%", "effects": [
        {"stat": "movement_speed", "operation": "multiply", "amount": 1.10},
    ]},
}

# Big upgrade at the end of each cycle, on the cycle summary screen.
CYCLE_UPGRADES = {
    "shotgunner": {"label": "Shotgunner: +2 projectiles, wider spread, slower shots", "effects": [
        {"stat": "projectile_count", "operation": "add", "amount": 2},
        {"stat": "projectile_gap", "operation": "add", "amount": 5},
        {"stat": "shot_speed", "operation": "multiply", "amount": 0.8},
    ]},
    "high_caliber": {"label": "High Caliber: damage x2, fire rate -33%", "effects": [
        {"stat": "damage", "operation": "multiply", "amount": 2.0},
        {"stat": "shot_cooldown", "operation": "multiply", "amount": 1.5},
    ]},
    "health": {"label": "Max health +30%", "effects": [
        {"stat": "max_health", "operation": "multiply", "amount": 1.30},
    ]},
    "attack": {"label": "Damage +40%", "effects": [
        {"stat": "damage", "operation": "multiply", "amount": 1.40},
    ]},
    "defense": {"label": "Defense +3", "effects": [
        {"stat": "defense", "operation": "add", "amount": 3},
    ]},
    "multishot": {"label": "Multishot +1", "effects": [
        {"stat": "projectile_count", "operation": "add", "amount": 1},
    ]},
    "attack_speed": {"label": "Fire rate +30%", "effects": [
        {"stat": "shot_cooldown", "operation": "multiply", "amount": 1 / 1.30},
    ]},
    "move_speed": {"label": "Move speed +30%", "effects": [
        {"stat": "movement_speed", "operation": "multiply", "amount": 1.30},
    ]},
}
