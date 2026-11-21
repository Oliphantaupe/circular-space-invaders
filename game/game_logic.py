"""Game behaviour: cycles and waves, upgrades, movement, shooting and collisions."""
import random

import pygame
from pygame.math import Vector2

from . import game_state
from . import content

MOVE_KEYS = {                       # key -> movement direction (Z/Q/S/D on AZERTY, plus arrows)
    pygame.K_z: Vector2(0, -1), pygame.K_UP: Vector2(0, -1),
    pygame.K_s: Vector2(0, 1), pygame.K_DOWN: Vector2(0, 1),
    pygame.K_q: Vector2(-1, 0), pygame.K_LEFT: Vector2(-1, 0),
    pygame.K_d: Vector2(1, 0), pygame.K_RIGHT: Vector2(1, 0),
}


# --- Ships -----------------------------------------------------------------

def take_damage(ship, amount):
    ship.health = max(0, ship.health - amount)


def damage_player(player, amount):
    take_damage(player, max(1, amount - player.defense))


def heal(ship, amount):
    ship.health = min(ship.max_health, ship.health + amount)


def collides(first, second):
    """Anything with a pos and a radius (ship or projectile)."""
    return first.pos.distance_to(second.pos) < first.radius + second.radius


def create_enemy(name, pos, cycle):
    """Enemy of content.ENEMY_CLASSES[name], with its stats scaled for this cycle."""
    enemy = content.ENEMY_CLASSES[name](pos)
    growth = content.STAT_GROWTH_PER_CYCLE ** (cycle - 1)
    enemy.max_health = round(enemy.max_health * growth)
    enemy.health = enemy.max_health
    enemy.contact_damage = round(enemy.contact_damage * growth)
    enemy.score = enemy.score * cycle
    return enemy


# --- Cycles, waves and upgrades -------------------------------------------

def wave_enemy_counts(wave_index, cycle):
    return {name: count * cycle for name, count in content.WAVES[wave_index].items()}


def start_next_wave(game):
    wave_manager = game.wave_manager
    if wave_manager.wave_index >= 0:    # a wave was just cleared (-1 means the cycle is starting)
        heal(game.player, content.WAVE_END_HEAL * game.player.max_health)
    wave_manager.wave_index += 1
    if wave_manager.wave_index == len(content.WAVES):
        game.cycle_upgrade_choices = random_upgrades(content.CYCLE_UPGRADES)
        game.state = "cycle_summary"
        return
    if wave_manager.wave_index > 0:     # the last wave of a cycle gives the cycle upgrade instead
        game.wave_upgrade_choices = random_upgrades(content.WAVE_UPGRADES)
        game.state = "wave_upgrade"
    counts = wave_enemy_counts(wave_manager.wave_index, wave_manager.cycle)
    wave_manager.spawn_queue = [name for name, count in counts.items() for _ in range(count)]
    random.shuffle(wave_manager.spawn_queue)
    wave_manager.spawn_timer = 0.0


def random_upgrades(upgrades):
    return random.sample(list(upgrades.values()), content.UPGRADES_OFFERED)


def apply_effect(player, effect):
    old_value = getattr(player, effect["stat"])
    if effect["operation"] == "multiply":
        new_value = old_value * effect["amount"]
    else:
        new_value = old_value + effect["amount"]
    setattr(player, effect["stat"], new_value)
    if effect["stat"] == "max_health":
        heal(player, new_value - old_value)     # heal the health gained


def apply_upgrade(player, upgrade):
    for effect in upgrade["effects"]:
        apply_effect(player, effect)
    player.upgrades.append(upgrade["label"])


def pick_wave_upgrade(game, choice):
    """choice: index in game.wave_upgrade_choices."""
    apply_upgrade(game.player, game.wave_upgrade_choices[choice])
    game.state = "playing"


def start_next_cycle(game, choice):
    """choice: index in game.cycle_upgrade_choices."""
    apply_upgrade(game.player, game.cycle_upgrade_choices[choice])
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
        spawn_angle = random.uniform(0, 360)
        spawn_pos = game.player.pos + Vector2(content.SPAWN_RADIUS, 0).rotate(spawn_angle)
        game.enemies.append(create_enemy(wave_manager.spawn_queue.pop(), spawn_pos, wave_manager.cycle))
        wave_manager.spawn_timer = content.SPAWN_DELAY


# --- Player ----------------------------------------------------------------

def shoot(player):
    """Fires projectile_count projectiles fanned around the aim direction."""
    projectiles = []
    for i in range(player.projectile_count):
        offset = (i - (player.projectile_count - 1) / 2) * player.projectile_gap
        direction = player.direction.rotate(offset)
        muzzle = player.pos + direction * player.radius
        projectiles.append(game_state.Projectile(muzzle, direction, player.damage, player.shot_speed))
    player.cooldown_timer = player.shot_cooldown
    return projectiles


def move_player(player, dt, bounds):
    keys = pygame.key.get_pressed()
    movement = Vector2()
    for key, direction in MOVE_KEYS.items():
        if keys[key]:
            movement += direction
    if movement.length() > 0:
        player.pos += movement.normalize() * player.movement_speed * dt
    player.pos.x = max(bounds.left + player.radius, min(bounds.right - player.radius, player.pos.x))
    player.pos.y = max(bounds.top + player.radius, min(bounds.bottom - player.radius, player.pos.y))


def aim_player(player):
    to_mouse = Vector2(pygame.mouse.get_pos()) - player.pos
    if to_mouse.length() > 0:
        player.angle = Vector2(1, 0).angle_to(to_mouse)


def update_player(game, dt):
    player = game.player
    move_player(player, dt, game.screen.get_rect())
    aim_player(player)
    player.cooldown_timer -= dt
    wants_to_shoot = pygame.key.get_pressed()[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]
    if wants_to_shoot and player.cooldown_timer <= 0:
        game.projectiles += shoot(player)


# --- World -----------------------------------------------------------------

def update_projectiles(game, dt):
    bounds = game.screen.get_rect()
    for projectile in game.projectiles:
        projectile.pos += projectile.direction * projectile.speed * dt
        if not bounds.collidepoint(projectile.pos):
            projectile.alive = False


def update_enemies(game, dt):
    for enemy in game.enemies:
        to_player = game.player.pos - enemy.pos
        if to_player.length() > 0:
            enemy.pos += to_player.normalize() * enemy.speed * dt


def handle_collisions(game):
    player = game.player
    for enemy in game.enemies:
        if collides(enemy, player):
            damage_player(player, enemy.contact_damage)
            enemy.health = 0            # enemies die on contact
            continue
        for projectile in game.projectiles:
            if projectile.alive and collides(enemy, projectile):
                projectile.alive = False
                take_damage(enemy, projectile.damage)
                if not enemy.alive:
                    game.score += enemy.score
                break


def update_playing(game, dt):
    update_player(game, dt)
    update_projectiles(game, dt)
    update_enemies(game, dt)
    handle_collisions(game)
    game.projectiles = [p for p in game.projectiles if p.alive]
    game.enemies = [e for e in game.enemies if e.alive]
    update_wave_manager(game, dt)

    game.elapsed_time += dt
    if not game.player.alive:
        game.state = "game_over"
