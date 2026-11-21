"""Runtime game state: projectiles, wave spawner and the game itself.

Player and enemy classes (design values) are in content.py.
"""
import pygame
from pygame.math import Vector2

from . import content


class Projectile:
    size = 5                                # hitbox radius in pixels

    def __init__(self, position: Vector2, direction: Vector2, attack_damage: float, speed: float):
        self.position = Vector2(position)
        self.direction = direction          # fixed at spawn, moves forward only
        self.attack_damage = attack_damage  # inherited from the shooter when fired
        self.speed = speed                  # inherited from the shooter when fired
        self.alive = True                   # False when it hits or leaves the screen


class WaveManager:
    """Spawner: tracks the current cycle/wave and which enemies are left to spawn."""
    def __init__(self):
        self.cycle = 1                      # one cycle = every wave in content.WAVES
        self.wave_index = -1                # index in content.WAVES, -1 before the first wave
        self.spawn_queue: list[str] = []    # enemy names (keys of content.ENEMY_CLASSES) left to spawn
        self.spawn_timer = 0.0


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((1000, 700))
        self.clock = pygame.time.Clock()
        self.state = "playing"              # "playing" | "wave_upgrade" | "cycle_summary" | "game_over"
        self.player = content.Player(Vector2(self.screen.get_rect().center))
        self.enemies: list[content.Enemy] = []
        self.projectiles: list[Projectile] = []
        self.wave_manager = WaveManager()
        self.score = 0
        self.elapsed_time = 0.0             # stops at game over
        self.show_debug_grid = False
        self.cycle_upgrade_choices: list[dict] = []     # content.CYCLE_UPGRADES offered on the cycle summary
        self.wave_upgrade_choices: list[dict] = []      # content.WAVE_UPGRADES offered in the wave popup
