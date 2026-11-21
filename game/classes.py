import pygame
from pygame.math import Vector2

from . import content


class Ship:
    """Anything with health that can be hit: the player and every enemy.

    Subclasses set their starting stats as class attributes.
    """
    max_health = 1
    radius = 10
    color = "white"

    def __init__(self, pos: Vector2):
        self.pos = Vector2(pos)
        self.health = self.max_health

    @property
    def alive(self) -> bool:
        return self.health > 0

    def take_damage(self, amount: float):
        self.health = max(0, self.health - amount)

    def heal(self, amount: float):
        self.health = min(self.max_health, self.health + amount)

    def collides_with(self, other) -> bool:
        """other: anything with a pos and a radius (ship or projectile)."""
        return self.pos.distance_to(other.pos) < self.radius + other.radius


class Player(Ship):
    """Fixed at screen center. Only rotates and shoots."""
    max_health = 100
    radius = 20                             # hitbox for enemy contact
    color = (80, 200, 255)
    rotation_speed = 180                    # degrees / second
    # Shot stats: copied onto each projectile when fired, modified by upgrades.
    damage = 10
    shot_speed = 200                        # pixels / second
    shot_cooldown = 0.2                     # seconds between shots
    projectile_count = 1                    # projectiles per shot, fanned around the facing direction
    projectile_gap = 10                     # degrees between two projectiles of the same shot
    defense = 0                             # flat reduction of contact damage (min 1 damage taken)

    def __init__(self, center: Vector2):
        super().__init__(center)
        self.angle = -90                    # degrees, -90 = facing up
        self.cooldown_timer = 0.0
        self.upgrades: list[str] = []       # keys of content.UPGRADES picked so far

    @property
    def direction(self) -> Vector2:         # unit vector of facing direction
        return Vector2(1, 0).rotate(self.angle)

    def take_damage(self, amount: float):
        super().take_damage(max(1, amount - self.defense))

    def update(self, dt: float, rotation: int):
        """rotation: -1 to turn left, 1 to turn right, 0 to stay."""
        self.angle += rotation * self.rotation_speed * dt
        self.cooldown_timer -= dt

    def shoot(self) -> list["Projectile"]:
        """Returns the fired projectiles, none while the cooldown is running."""
        if self.cooldown_timer > 0:
            return []
        self.cooldown_timer = self.shot_cooldown
        projectiles = []
        for i in range(self.projectile_count):
            offset = (i - (self.projectile_count - 1) / 2) * self.projectile_gap
            direction = self.direction.rotate(offset)
            muzzle = self.pos + direction * self.radius
            projectiles.append(Projectile(muzzle, direction, self.damage, self.shot_speed))
        return projectiles

    def apply_upgrade(self, upgrade_key: str):
        upgrade = content.UPGRADES[upgrade_key]
        old_value = getattr(self, upgrade["stat"])
        if upgrade["operation"] == "multiply":
            new_value = old_value * upgrade["amount"]
        else:
            new_value = old_value + upgrade["amount"]
        setattr(self, upgrade["stat"], new_value)
        if upgrade["stat"] == "max_health":
            self.heal(new_value - old_value)   # heal the health gained
        self.upgrades.append(upgrade_key)


class Enemy(Ship):
    """Flies straight at the player and dies on contact.

    New enemy type: subclass it, set the stats below, override update() for a new
    behaviour, and register it in ENEMY_CLASSES.
    """
    speed = 0                               # pixels / second
    contact_damage = 0                      # health lost by the player on contact
    score = 0                               # multiplied by the cycle number

    def __init__(self, pos: Vector2, cycle: int = 1):
        growth = content.STAT_GROWTH_PER_CYCLE ** (cycle - 1)
        self.max_health = round(type(self).max_health * growth)
        super().__init__(pos)
        self.contact_damage = round(type(self).contact_damage * growth)
        self.score = type(self).score * cycle

    def update(self, dt: float, target: Ship):
        offset = target.pos - self.pos
        if offset.length() > 0:
            self.pos += offset.normalize() * self.speed * dt


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


# Names used in content.WAVES -> enemy class.
ENEMY_CLASSES = {"enemy": BasicEnemy, "elite": EliteEnemy, "boss": BossEnemy}


class Projectile:
    radius = 5

    def __init__(self, pos: Vector2, direction: Vector2, damage: float, speed: float):
        self.pos = Vector2(pos)
        self.direction = direction          # fixed at spawn, moves forward only
        self.damage = damage                # inherited from the shooter when fired
        self.speed = speed                  # inherited from the shooter when fired
        self.alive = True                   # False when it hits or leaves the screen

    def update(self, dt: float, bounds: pygame.Rect):
        self.pos += self.direction * self.speed * dt
        if not bounds.collidepoint(self.pos):
            self.alive = False


class WaveManager:
    """Spawner: tracks the current cycle/wave and which enemies are left to spawn."""
    def __init__(self, center: Vector2, spawn_radius: float):
        self.center = Vector2(center)
        self.spawn_radius = spawn_radius    # ring around the player where enemies appear
        self.cycle = 1                      # one cycle = every wave in content.WAVES
        self.wave_index = -1                # index in content.WAVES, -1 before the first wave
        self.spawn_queue: list[str] = []    # enemy names (keys of ENEMY_CLASSES) left to spawn
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
        self.upgrade_choices: list[str] = []    # keys of content.UPGRADES offered on the cycle summary
