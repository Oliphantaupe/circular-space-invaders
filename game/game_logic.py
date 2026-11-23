"""Game behaviour: cycles and waves, upgrades, movement, shooting and collisions.

Ship stats, waves, upgrades and enemy scaling come from game_class.py and game_content.py.
"""
import math
import random

import pygame

from . import assets
from . import game_content
from .game_class import Projectile

SPAWN_RADIUS = 400          # enemies appear on a ring this far from the player
SPAWN_DELAY = 0.5           # seconds between two enemies of a wave
WAVE_END_HEAL = 0.20        # fraction of max health restored when a wave is cleared
UPGRADES_OFFERED = 3        # upgrades to choose from, picked with keys 1/2/3
PROJECTILE_SIZE = 5         # projectile hitbox radius in pixels

MOVE_KEYS = {               # key -> (x, y) movement (Z/Q/S/D on AZERTY, plus arrows)
    pygame.K_z: (0, -1), pygame.K_UP: (0, -1),
    pygame.K_s: (0, 1), pygame.K_DOWN: (0, 1),
    pygame.K_q: (-1, 0), pygame.K_LEFT: (-1, 0),
    pygame.K_d: (1, 0), pygame.K_RIGHT: (1, 0),
}


# --- Geometry ----------------------------------------------------------------

def point_at(start, angle, distance):
    """Position distance pixels away from start in the direction of angle (degrees, 0 = right, 90 = down)."""
    return [start[0] + math.cos(math.radians(angle)) * distance,
            start[1] + math.sin(math.radians(angle)) * distance]


def move(thing, angle, distance):
    """Moves a ship or projectile."""
    thing.position = point_at(thing.position, angle, distance)


def angle_towards(start, target):
    """Angle in degrees from position start to position target."""
    return math.degrees(math.atan2(target[1] - start[1], target[0] - start[0]))


def collides(first_position, first_size, second_position, second_size):
    return math.dist(first_position, second_position) < first_size + second_size


def random_ring_position(center):
    """Random point at SPAWN_RADIUS pixels from center."""
    return point_at(center, random.uniform(0, 360), SPAWN_RADIUS)


# --- Player health -------------------------------------------------------------

def damage_player(game, amount):
    """Defense is a flat reduction, the player always loses at least 1 health point."""
    player = game.player
    player.health_point = max(0, player.health_point - max(1, amount - player.defense_amount))


def heal_player(game, amount):
    game.player.health_point = min(game.max_health_point, game.player.health_point + amount)


def upgrade_player(game, upgrade):
    """Applies an upgrade from game_content. Upgrades multiply health_point (the current health),
    so the max health is multiplied by the same factor."""
    health_before = game.player.health_point
    game_content.apply_upgrade(game.player, upgrade)
    if health_before > 0:
        game.max_health_point *= game.player.health_point / health_before


# --- Enemies, waves and cycles ---------------------------------------------------

def origin():
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
    """One enemy with the stats it has in this cycle (scaled by game_content.spawn_wave)."""
    return game_content.spawn_wave({enemy_class: 1}, cycle, origin)[0]


def start_next_wave(game):
    wave_manager = game.wave_manager
    if wave_manager.wave_index >= 0:    # a wave was just cleared (-1 means the cycle is starting)
        heal_player(game, WAVE_END_HEAL * game.max_health_point)
        game.ui.wave += 1               # total waves since the start of the game
    wave_manager.wave_index += 1
    if wave_manager.wave_index == len(game_content.waves):
        game.cycle_upgrade_choices = random.sample(game_content.cycle_upgrades, UPGRADES_OFFERED)
        game.state = "cycle_summary"
        return
    if wave_manager.wave_index > 0:     # the last wave of a cycle gives the cycle upgrade instead
        game.wave_upgrade_choices = random.sample(game_content.wave_upgrades, UPGRADES_OFFERED)
        game.state = "wave_upgrade"

    def spawn_position():
        return random_ring_position(game.player.position)

    wave = game_content.waves[wave_manager.wave_index]
    wave_manager.spawn_queue = game_content.spawn_wave(wave, wave_manager.cycle, spawn_position)
    random.shuffle(wave_manager.spawn_queue)
    wave_manager.spawn_timer = 0.0


def pick_wave_upgrade(game, choice):
    """choice: index in game.wave_upgrade_choices."""
    upgrade_player(game, game.wave_upgrade_choices[choice])
    game.state = "playing"


def start_next_cycle(game, choice):
    """choice: index in game.cycle_upgrade_choices."""
    upgrade_player(game, game.cycle_upgrade_choices[choice])
    game.wave_manager.cycle += 1
    game.wave_manager.wave_index = -1   # the wave manager starts wave 0 on the next update
    game.state = "playing"


def update_wave_manager(game, dt):
    wave_manager = game.wave_manager
    if not wave_manager.spawn_queue:
        if not game.enemies:
            start_next_wave(game)
        return
    wave_manager.spawn_timer -= dt
    if wave_manager.spawn_timer <= 0:
        enemy = wave_manager.spawn_queue.pop()
        # The player may have moved since the wave was created: spawn around where they are now.
        enemy.position = random_ring_position(game.player.position)
        enemy.angle = angle_towards(enemy.position, game.player.position)
        game.enemies.append(enemy)
        wave_manager.spawn_timer = SPAWN_DELAY


# --- Player ----------------------------------------------------------------

def shoot(game):
    """Fires projectile_amount projectiles, projectile_spread degrees apart, centered on the aim."""
    player = game.player
    amount = int(player.projectile_amount)
    for i in range(amount):
        projectile = Projectile(player)
        projectile.angle = player.angle + (i - (amount - 1) / 2) * player.projectile_spread
        move(projectile, projectile.angle, player.size)     # start at the edge of the ship
        game.projectiles.append(projectile)
    game.shot_timer = player.attack_delay
    assets.play_sound("shoot")


def move_player(game, dt):
    player = game.player
    keys = pygame.key.get_pressed()
    x, y = 0, 0
    for key, (key_x, key_y) in MOVE_KEYS.items():
        if keys[key]:
            x += key_x
            y += key_y
    if x != 0 or y != 0:
        player.position[0] += x / math.hypot(x, y) * player.movement_speed * dt   # same speed diagonally
        player.position[1] += y / math.hypot(x, y) * player.movement_speed * dt
    bounds = game.screen.get_rect()
    player.position[0] = max(bounds.left + player.size, min(bounds.right - player.size, player.position[0]))
    player.position[1] = max(bounds.top + player.size, min(bounds.bottom - player.size, player.position[1]))


def aim_player(game):
    mouse = pygame.mouse.get_pos()
    if math.dist(mouse, game.player.position) > 0:
        game.player.angle = angle_towards(game.player.position, mouse)


def update_player(game, dt):
    move_player(game, dt)
    aim_player(game)
    game.shot_timer -= dt
    wants_to_shoot = pygame.key.get_pressed()[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]
    if wants_to_shoot and game.shot_timer <= 0:
        shoot(game)


# --- World -----------------------------------------------------------------

def update_projectiles(game, dt):
    bounds = game.screen.get_rect()
    on_screen = []
    for projectile in game.projectiles:
        move(projectile, projectile.angle, projectile.speed * dt)
        if bounds.collidepoint(projectile.position):
            on_screen.append(projectile)
    game.projectiles = on_screen


def update_enemies(game, dt):
    for enemy in game.enemies:
        enemy.angle = angle_towards(enemy.position, game.player.position)
        move(enemy, enemy.angle, enemy.movement_speed * dt)


def handle_collisions(game):
    """Enemies die when they touch the player, player projectiles damage enemies and disappear."""
    player = game.player
    used_projectiles = []
    surviving_enemies = []
    for enemy in game.enemies:
        if collides(enemy.position, enemy.size, player.position, player.size):
            damage_player(game, enemy.attack_damage)
            continue
        for projectile in game.projectiles:
            if projectile.is_player and projectile not in used_projectiles \
                    and collides(enemy.position, enemy.size, projectile.position, PROJECTILE_SIZE):
                used_projectiles.append(projectile)
                enemy.health_point -= projectile.attack_damage
                break
        if enemy.health_point > 0:
            surviving_enemies.append(enemy)
        else:
            game.ui.score += enemy.score * game.wave_manager.cycle
            assets.play_sound("enemy_killed")
    game.enemies = surviving_enemies
    game.projectiles = [projectile for projectile in game.projectiles if projectile not in used_projectiles]


def update_playing(game, dt):
    update_player(game, dt)
    update_projectiles(game, dt)
    update_enemies(game, dt)
    handle_collisions(game)
    update_wave_manager(game, dt)

    game.ui.time += dt
    game.ui.life = game.player.health_point
    if game.player.health_point <= 0:
        game.state = "game_over"
        assets.play_sound("game_over")
