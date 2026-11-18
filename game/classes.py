import pygame
from pygame.math import Vector2


class Player:
    """Fixed at screen center. Only rotates and shoots."""
    def __init__(self, center: Vector2):
        self.pos = Vector2(center)          # never changes
        self.angle = -90                    # degrees, -90 = facing up
        self.rotation_speed = 180           # degrees / second
        self.max_health = 100
        self.health = self.max_health
        self.radius = 20                    # hitbox for enemy contact
        # Shot stats: copied onto each projectile when fired, modified by upgrades.
        self.damage = 1
        self.shot_speed = 600               # pixels / second
        self.shot_cooldown = 0.2            # seconds between shots
        self.cooldown_timer = 0.0
        self.upgrades: list[str] = []       # keys of content.UPGRADES picked so far

    @property
    def direction(self) -> Vector2:         # unit vector of facing direction
        return Vector2(1, 0).rotate(self.angle)


class Projectile:
    def __init__(self, pos: Vector2, direction: Vector2, damage: float, speed: float):
        self.pos = Vector2(pos)
        self.direction = direction          # fixed at spawn, moves forward only
        self.damage = damage                # inherited from the player when fired
        self.speed = speed                  # inherited from the player when fired
        self.radius = 5
        self.alive = True                   # False when it hits or leaves the screen


class Enemy:
    def __init__(self, kind: str, pos: Vector2, stats: dict):
        self.kind = kind                    # key of content.ENEMY_TYPES
        self.pos = Vector2(pos)
        self.health = stats["health"]
        self.speed = stats["speed"]
        self.contact_damage = stats["contact_damage"]   # health lost by the player, enemy dies on contact
        self.radius = stats["radius"]
        self.score_value = stats["score"]
        self.color = stats["color"]
        self.alive = True


class WaveManager:
    """Spawner: tracks the current cycle/wave and which enemies are left to spawn."""
    def __init__(self, center: Vector2, spawn_radius: float):
        self.center = Vector2(center)
        self.spawn_radius = spawn_radius    # ring around the player where enemies appear
        self.cycle = 1                      # one cycle = every wave in content.WAVES
        self.wave_index = -1                # index in content.WAVES, -1 before the first wave
        self.spawn_queue: list[str] = []    # enemy kinds left to spawn in the current wave
        self.spawn_delay = 0.5              # seconds between spawns
        self.spawn_timer = 0.0


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((1000, 700))
        self.clock = pygame.time.Clock()
        self.state = "playing"              # "playing" | "cycle_summary" | "game_over"
        self.player = Player(Vector2(self.screen.get_rect().center))
        self.enemies: list[Enemy] = []
        self.projectiles: list[Projectile] = []
        self.wave_manager = WaveManager(self.player.pos, spawn_radius=400)
        self.score = 0
        self.elapsed_time = 0.0             # stops at game over
        self.show_debug_grid = False
