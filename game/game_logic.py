"""Game flow: cycles and waves, upgrades, input and collisions.

Entity behaviour (movement, shooting, damage) lives in the classes' methods.
"""
import random

import pygame
from pygame.math import Vector2

from . import classes
from . import content


def wave_enemy_counts(wave_index, cycle):
    return {name: count * cycle for name, count in content.WAVES[wave_index].items()}


def start_next_wave(game):
    wave_manager = game.wave_manager
    if wave_manager.wave_index >= 0:    # a wave was just cleared (-1 means the cycle is starting)
        game.player.heal(content.WAVE_END_HEAL * game.player.max_health)
    wave_manager.wave_index += 1
    if wave_manager.wave_index == len(content.WAVES):
        game.upgrade_choices = random.sample(list(content.UPGRADES), content.UPGRADES_OFFERED)
        game.state = "cycle_summary"
        return
    counts = wave_enemy_counts(wave_manager.wave_index, wave_manager.cycle)
    wave_manager.spawn_queue = [name for name, count in counts.items() for _ in range(count)]
    random.shuffle(wave_manager.spawn_queue)
    wave_manager.spawn_timer = 0.0


def start_next_cycle(game, upgrade_key):
    game.player.apply_upgrade(upgrade_key)
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
        enemy_class = classes.ENEMY_CLASSES[wave_manager.spawn_queue.pop()]
        spawn_angle = random.uniform(0, 360)
        spawn_pos = wave_manager.center + Vector2(wave_manager.spawn_radius, 0).rotate(spawn_angle)
        game.enemies.append(enemy_class(spawn_pos, wave_manager.cycle))
        wave_manager.spawn_timer = wave_manager.spawn_delay


def update_player(game, dt):
    keys = pygame.key.get_pressed()
    rotation = 0
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        rotation -= 1
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        rotation += 1
    game.player.update(dt, rotation)
    if keys[pygame.K_SPACE]:
        game.projectiles += game.player.shoot()


def handle_collisions(game):
    player = game.player
    for enemy in game.enemies:
        if enemy.collides_with(player):
            player.take_damage(enemy.contact_damage)
            enemy.health = 0            # enemies die on contact
            continue
        for projectile in game.projectiles:
            if projectile.alive and enemy.collides_with(projectile):
                projectile.alive = False
                enemy.take_damage(projectile.damage)
                if not enemy.alive:
                    game.score += enemy.score
                break


def update_playing(game, dt):
    update_player(game, dt)
    bounds = game.screen.get_rect()
    for projectile in game.projectiles:
        projectile.update(dt, bounds)
    for enemy in game.enemies:
        enemy.update(dt, game.player)
    handle_collisions(game)
    game.projectiles = [p for p in game.projectiles if p.alive]
    game.enemies = [e for e in game.enemies if e.alive]
    update_wave_manager(game, dt)

    game.elapsed_time += dt
    if not game.player.alive:
        game.state = "game_over"
