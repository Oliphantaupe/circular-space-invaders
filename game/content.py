"""Game design data: player and enemy stats, waves, cycle scaling and upgrades.

Tune the game here without touching the logic (game_logic.py).
Every class below only holds values; their behaviour is in game_logic.py.
"""
from pygame.math import Vector2


class Ship:
    """Anything with health that can be hit: the player and every enemy."""
    health_point = 1                        # max health at spawn (max_health_point keeps it)
    attack_damage = 0                       # player: damage per projectile, enemy: damage on contact
    movement_speed = 0                      # pixels / second
    size = 10                               # hitbox radius in pixels
    shape = "circle"                        # "circle" or "triangle" (triangle points where the ship faces)
    color = "white"

    def __init__(self, position: Vector2):
        self.position = Vector2(position)
        self.max_health_point = self.health_point
        self.angle = 0                      # degrees, 0 = facing right, 90 = facing down

    @property
    def alive(self) -> bool:
        return self.health_point > 0

    @property
    def direction(self) -> Vector2:         # unit vector of facing direction
        return Vector2(1, 0).rotate(self.angle)


class Player(Ship):
    """Moves with Z/Q/S/D, aims at the mouse and shoots."""
    health_point = 100
    attack_damage = 10                      # copied onto each projectile when fired
    movement_speed = 200
    size = 20
    shape = "triangle"
    color = (80, 200, 255)
    # Shot stats, modified by upgrades.
    attack_delay = 0.2                      # seconds between shots
    projectile_amount = 1                   # projectiles per shot, fanned around the aim direction
    projectile_spread = 10                  # degrees between two projectiles of the same shot
    projectile_speed = 200                  # pixels / second
    defense_amount = 0                      # flat reduction of damage taken (min 1 damage taken)

    def __init__(self, position: Vector2):
        super().__init__(position)
        self.angle = -90                    # facing up
        self.cooldown_timer = 0.0
        self.upgrades: list[str] = []       # labels of the upgrades picked so far


class Enemy(Ship):
    """Flies straight at the player and dies on contact.

    health_point and attack_damage grow by STAT_GROWTH_PER_CYCLE each cycle, score is multiplied by the cycle.
    New enemy type: subclass Enemy, set its values and add it to ENEMY_CLASSES.
    """
    score = 0                               # points per kill at cycle 1


class BasicEnemy(Enemy):
    health_point = 10
    attack_damage = 10
    movement_speed = 10
    size = 15
    score = 10
    color = "red"


class EliteEnemy(Enemy):
    health_point = 25
    attack_damage = 20
    movement_speed = 8
    size = 25
    score = 30
    color = "orange"


class BossEnemy(Enemy):
    health_point = 100
    attack_damage = 60
    movement_speed = 6
    size = 50
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
# Player stats: max_health_point, attack_damage, defense_amount, attack_delay (lower = faster fire),
# projectile_amount, projectile_spread, projectile_speed, movement_speed.

# Small upgrade after each wave, from a popup at the bottom of the screen.
WAVE_UPGRADES = {
    "health": {"label": "Max health +10%", "effects": [
        {"stat": "max_health_point", "operation": "multiply", "amount": 1.10},
    ]},
    "attack": {"label": "Damage +15%", "effects": [
        {"stat": "attack_damage", "operation": "multiply", "amount": 1.15},
    ]},
    "defense": {"label": "Defense +1", "effects": [
        {"stat": "defense_amount", "operation": "add", "amount": 1},
    ]},
    "attack_speed": {"label": "Fire rate +10%", "effects": [
        {"stat": "attack_delay", "operation": "multiply", "amount": 1 / 1.10},
    ]},
    "move_speed": {"label": "Move speed +10%", "effects": [
        {"stat": "movement_speed", "operation": "multiply", "amount": 1.10},
    ]},
}

# Big upgrade at the end of each cycle, on the cycle summary screen.
CYCLE_UPGRADES = {
    "shotgunner": {"label": "Shotgunner: +2 projectiles, wider spread, slower shots", "effects": [
        {"stat": "projectile_amount", "operation": "add", "amount": 2},
        {"stat": "projectile_spread", "operation": "add", "amount": 5},
        {"stat": "projectile_speed", "operation": "multiply", "amount": 0.8},
    ]},
    "high_caliber": {"label": "High Caliber: damage x2, fire rate -33%", "effects": [
        {"stat": "attack_damage", "operation": "multiply", "amount": 2.0},
        {"stat": "attack_delay", "operation": "multiply", "amount": 1.5},
    ]},
    "health": {"label": "Max health +30%", "effects": [
        {"stat": "max_health_point", "operation": "multiply", "amount": 1.30},
    ]},
    "attack": {"label": "Damage +40%", "effects": [
        {"stat": "attack_damage", "operation": "multiply", "amount": 1.40},
    ]},
    "defense": {"label": "Defense +3", "effects": [
        {"stat": "defense_amount", "operation": "add", "amount": 3},
    ]},
    "multishot": {"label": "Multishot +1", "effects": [
        {"stat": "projectile_amount", "operation": "add", "amount": 1},
    ]},
    "attack_speed": {"label": "Fire rate +30%", "effects": [
        {"stat": "attack_delay", "operation": "multiply", "amount": 1 / 1.30},
    ]},
    "move_speed": {"label": "Move speed +30%", "effects": [
        {"stat": "movement_speed", "operation": "multiply", "amount": 1.30},
    ]},
}
