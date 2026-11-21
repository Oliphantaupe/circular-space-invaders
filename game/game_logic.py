"""Game behaviour: cycles and waves, upgrades, movement, shooting and collisions."""
import random

import pygame
from pygame.math import Vector2

from . import classes
from . import content


def enemy_stats(kind, cycle):
    base = content.ENEMY_TYPES[kind]
    growth = content.STAT_GROWTH_PER_CYCLE ** (cycle - 1)
    stats = dict(base)
    stats["health"] = round(base["health"] * growth)
    stats["contact_damage"] = round(base["contact_damage"] * growth)
    stats["score"] = base["score"] * cycle
    return stats


def wave_enemy_counts(wave_index, cycle):
    return {kind: count * cycle for kind, count in content.WAVES[wave_index].items()}


def start_next_wave(game):
    wave_manager = game.wave_manager
    if wave_manager.wave_index >= 0:    # a wave was just cleared (-1 means the cycle is starting)
        heal_player(game.player, content.WAVE_END_HEAL * game.player.max_health)
    wave_manager.wave_index += 1
    if wave_manager.wave_index == len(content.WAVES):
        game.upgrade_choices = random.sample(list(content.UPGRADES), content.UPGRADES_OFFERED)
        game.state = "cycle_summary"
        return
    counts = wave_enemy_counts(wave_manager.wave_index, wave_manager.cycle)
    wave_manager.spawn_queue = [kind for kind, count in counts.items() for _ in range(count)]
    random.shuffle(wave_manager.spawn_queue)
    wave_manager.spawn_timer = 0.0


def heal_player(player, amount):
    player.health = min(player.max_health, player.health + amount)


def apply_upgrade(player, upgrade_key):
    upgrade = content.UPGRADES[upgrade_key]
    old_value = getattr(player, upgrade["stat"])
    if upgrade["operation"] == "multiply":
        new_value = old_value * upgrade["amount"]
    else:
        new_value = old_value + upgrade["amount"]
    setattr(player, upgrade["stat"], new_value)
    if upgrade["stat"] == "max_health":
        player.health += new_value - old_value     # heal the health gained
    player.upgrades.append(upgrade_key)


def start_next_cycle(game, upgrade_key):
    apply_upgrade(game.player, upgrade_key)
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
        kind = wave_manager.spawn_queue.pop()
        spawn_angle = random.uniform(0, 360)
        spawn_pos = wave_manager.center + Vector2(wave_manager.spawn_radius, 0).rotate(spawn_angle)
        game.enemies.append(classes.Enemy(kind, spawn_pos, enemy_stats(kind, wave_manager.cycle)))
        wave_manager.spawn_timer = wave_manager.spawn_delay


def update_player(game, dt):
    keys = pygame.key.get_pressed()
    player = game.player
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player.angle -= player.rotation_speed * dt
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player.angle += player.rotation_speed * dt

    player.cooldown_timer -= dt
    if keys[pygame.K_SPACE] and player.cooldown_timer <= 0:
        for i in range(player.projectile_count):
            offset = (i - (player.projectile_count - 1) / 2) * player.projectile_gap
            direction = player.direction.rotate(offset)
            muzzle = player.pos + direction * player.radius
            game.projectiles.append(classes.Projectile(muzzle, direction, player.damage, player.shot_speed))
        player.cooldown_timer = player.shot_cooldown


def update_projectiles(game, dt):
    screen_rect = game.screen.get_rect()
    for projectile in game.projectiles:
        projectile.pos += projectile.direction * projectile.speed * dt
        if not screen_rect.collidepoint(projectile.pos):
            projectile.alive = False


def update_enemies(game, dt):
    player = game.player
    for enemy in game.enemies:
        enemy.pos += (player.pos - enemy.pos).normalize() * enemy.speed * dt
        if enemy.pos.distance_to(player.pos) < enemy.radius + player.radius:
            enemy.alive = False
            player.health -= max(1, enemy.contact_damage - player.defense)
            continue
        for projectile in game.projectiles:
            if projectile.alive and enemy.pos.distance_to(projectile.pos) < enemy.radius + projectile.radius:
                projectile.alive = False
                enemy.health -= projectile.damage
                if enemy.health <= 0:
                    enemy.alive = False
                    game.score += enemy.score_value
                break


def update_playing(game, dt):
    update_player(game, dt)
    update_projectiles(game, dt)
    update_enemies(game, dt)
    game.projectiles = [p for p in game.projectiles if p.alive]
    game.enemies = [e for e in game.enemies if e.alive]
    update_wave_manager(game, dt)

    game.elapsed_time += dt
    if game.player.health <= 0:
        game.player.health = 0
        game.state = "game_over"
