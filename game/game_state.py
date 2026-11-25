"""A game in progress: the wave spawner and the game itself (player, enemies, projectiles, rules).

Ship stats come from game_class.py; waves, upgrades and enemy scaling from game_content.py.
Input and screens (upgrade choice, game over) are in screens.py.
"""
import math
import random

from . import game_content
from .game_class import Player, Projectile, UI
from .geometry import angle_towards, collides, move, point_at

SPAWN_RADIUS = 400          # enemies appear on a ring this far from the player
SPAWN_DELAY = 0.5           # seconds between two enemies of a wave
WAVE_END_HEAL = 0.20        # fraction of max health restored when a wave is cleared
PROJECTILE_SIZE = 5         # projectile hitbox radius in pixels


def origin():
    """Position given to game_content.scale_wave: the real one is chosen when the enemy appears."""
    return [0, 0]


def enemy_classes():
    """Every enemy class used in game_content.waves, in order of appearance."""
    classes = []
    for wave in game_content.waves:
        for enemy_class in wave:
            if enemy_class not in classes:
                classes.append(enemy_class)
    return classes


def scaled_enemy(enemy_class, cycle):
    """One enemy with the stats it has in this cycle."""
    return game_content.scale_wave({enemy_class: 1}, cycle, origin)[0]


class WaveManager:
    """Tracks the current cycle and wave, and releases the wave's enemies one by one."""
    def __init__(self):
        self.cycle = 1                      # one cycle = every wave in game_content.waves
        self.wave_index = 0                 # index in game_content.waves
        self.spawn_queue = []               # enemies of the current wave not on screen yet
        self.spawn_timer = 0.0
        self.fill_spawn_queue()

    def fill_spawn_queue(self):
        wave = game_content.waves[self.wave_index]
        self.spawn_queue = game_content.scale_wave(wave, self.cycle, origin)
        random.shuffle(self.spawn_queue)
        self.spawn_timer = 0.0

    def is_last_wave(self):
        return self.wave_index == len(game_content.waves) - 1

    def next_wave(self):
        self.wave_index += 1
        self.fill_spawn_queue()

    def next_cycle(self):
        self.cycle += 1
        self.wave_index = 0
        self.fill_spawn_queue()

    def release_enemies(self, dt, target):
        """Returns the enemies that appear now (one every SPAWN_DELAY seconds), on a ring around target."""
        self.spawn_timer -= dt
        if not self.spawn_queue or self.spawn_timer > 0:
            return []
        enemy = self.spawn_queue.pop()
        enemy.position = point_at(target, random.uniform(0, 360), SPAWN_RADIUS)
        enemy.angle = angle_towards(enemy.position, target)
        self.spawn_timer = SPAWN_DELAY
        return [enemy]


class Game:
    def __init__(self, assets, bounds):
        """bounds: pygame.Rect of the window, the player and projectiles stay inside it."""
        self.assets = assets
        self.bounds = bounds
        self.player = Player(list(bounds.center))
        self.player.angle = -90             # facing up
        self.max_health_point = self.player.health_point    # health_point is the current health
        self.shot_timer = 0.0               # seconds until the player can shoot again
        self.enemies = []
        self.projectiles = []
        self.wave_manager = WaveManager()
        self.ui = UI(life=self.player.health_point)
        self.show_debug_grid = False

    # --- Player health and upgrades ---

    def damage_player(self, amount):
        """Defense is a flat reduction, the player always loses at least 1 health point."""
        player = self.player
        player.health_point = max(0, player.health_point - max(1, amount - player.defense_amount))

    def heal_player(self, amount):
        self.player.health_point = min(self.max_health_point, self.player.health_point + amount)

    def upgrade_player(self, upgrade):
        """Applies an upgrade from game_content. Upgrades multiply health_point (the current health),
        so the max health is multiplied by the same factor."""
        health_before = self.player.health_point
        game_content.apply_upgrade(self.player, upgrade)
        if health_before > 0:
            self.max_health_point *= self.player.health_point / health_before

    def is_player_dead(self):
        return self.player.health_point <= 0

    # --- Player actions ---

    def move_player(self, direction, dt):
        """direction: (x, y), each -1, 0 or 1. The player stays inside the window."""
        player = self.player
        x, y = direction
        if x != 0 or y != 0:
            player.position[0] += x / math.hypot(x, y) * player.movement_speed * dt   # same speed diagonally
            player.position[1] += y / math.hypot(x, y) * player.movement_speed * dt
        player.position[0] = max(self.bounds.left + player.size, min(self.bounds.right - player.size, player.position[0]))
        player.position[1] = max(self.bounds.top + player.size, min(self.bounds.bottom - player.size, player.position[1]))

    def aim_player(self, target):
        if math.dist(target, self.player.position) > 0:
            self.player.angle = angle_towards(self.player.position, target)

    def shoot(self):
        """Fires projectile_amount projectiles, projectile_spread degrees apart, centered on the aim.
        Does nothing until attack_delay seconds have passed since the last shot."""
        if self.shot_timer > 0:
            return
        player = self.player
        amount = int(player.projectile_amount)
        for i in range(amount):
            projectile = Projectile(player)
            projectile.angle = player.angle + (i - (amount - 1) / 2) * player.projectile_spread
            move(projectile, projectile.angle, player.size)     # start at the edge of the ship
            self.projectiles.append(projectile)
        self.shot_timer = player.attack_delay
        self.assets.play_sound("shoot")

    # --- Waves ---

    def is_wave_cleared(self):
        return not self.wave_manager.spawn_queue and not self.enemies

    def end_wave(self):
        self.heal_player(WAVE_END_HEAL * self.max_health_point)
        self.ui.wave += 1               # total waves since the start of the game

    # --- World ---

    def update(self, dt):
        """Moves everything, resolves collisions and releases enemies. Player input is applied before."""
        self.shot_timer -= dt
        self.update_projectiles(dt)
        self.update_enemies(dt)
        self.handle_collisions()
        self.enemies += self.wave_manager.release_enemies(dt, self.player.position)
        self.ui.time += dt
        self.ui.life = self.player.health_point

    def update_projectiles(self, dt):
        on_screen = []
        for projectile in self.projectiles:
            move(projectile, projectile.angle, projectile.speed * dt)
            if self.bounds.collidepoint(projectile.position):
                on_screen.append(projectile)
        self.projectiles = on_screen

    def update_enemies(self, dt):
        for enemy in self.enemies:
            enemy.angle = angle_towards(enemy.position, self.player.position)
            move(enemy, enemy.angle, enemy.movement_speed * dt)

    def handle_collisions(self):
        """Enemies die when they touch the player, player projectiles damage enemies and disappear."""
        player = self.player
        used_projectiles = []
        surviving_enemies = []
        for enemy in self.enemies:
            if collides(enemy.position, enemy.size, player.position, player.size):
                self.damage_player(enemy.attack_damage)
                continue
            for projectile in self.projectiles:
                if projectile.is_player and projectile not in used_projectiles \
                        and collides(enemy.position, enemy.size, projectile.position, PROJECTILE_SIZE):
                    used_projectiles.append(projectile)
                    enemy.health_point -= projectile.attack_damage
                    break
            if enemy.health_point > 0:
                surviving_enemies.append(enemy)
            else:
                self.ui.score += enemy.score * self.wave_manager.cycle
                self.assets.play_sound("enemy_killed")
        self.enemies = surviving_enemies
        self.projectiles = [projectile for projectile in self.projectiles if projectile not in used_projectiles]
