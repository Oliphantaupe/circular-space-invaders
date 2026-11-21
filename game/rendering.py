"""Everything drawn on screen."""
import math

import pygame
from pygame.math import Vector2

from . import content
from .game_logic import create_enemy

BG_COLOR = (10, 10, 25)
TEXT_COLOR = (220, 220, 230)
ORBIT_COLOR = (60, 60, 90)
GRID_COLOR = (35, 35, 60)
UPGRADE_COLOR = (255, 240, 120)
GRID_RING_STEP = 100        # pixels between debug rings
GRID_SECTORS = 12           # debug angle sectors (30 degrees each)


def draw_dashed_circle(surface, color, center, radius, dashes=60):
    step = 2 * math.pi / dashes
    for i in range(0, dashes, 2):
        start = center + Vector2(math.cos(i * step), math.sin(i * step)) * radius
        end = center + Vector2(math.cos((i + 1) * step), math.sin((i + 1) * step)) * radius
        pygame.draw.line(surface, color, start, end, 1)


def draw_debug_grid(surface, center, max_radius, font):
    """Polar grid: rings by distance from the player, sectors by angle (0 = right, clockwise)."""
    for radius in range(GRID_RING_STEP, int(max_radius) + 1, GRID_RING_STEP):
        pygame.draw.circle(surface, GRID_COLOR, center, radius, 1)
        surface.blit(font.render(str(radius), True, GRID_COLOR), center + Vector2(radius + 3, 2))
    for sector in range(GRID_SECTORS):
        angle = sector * 360 / GRID_SECTORS
        edge = center + Vector2(max_radius, 0).rotate(angle)
        pygame.draw.line(surface, GRID_COLOR, center, edge, 1)
        label = font.render(f"{angle:.0f}", True, GRID_COLOR)
        surface.blit(label, label.get_rect(center=center + Vector2(max_radius + 20, 0).rotate(angle)))


def draw_world(game, small_font):
    screen = game.screen
    player = game.player
    spawn_radius = content.SPAWN_RADIUS
    if game.show_debug_grid:
        draw_debug_grid(screen, player.pos, spawn_radius, small_font)
    draw_dashed_circle(screen, ORBIT_COLOR, player.pos, spawn_radius)

    tip = player.pos + player.direction * (player.radius + 10)
    left = player.pos + player.direction.rotate(140) * player.radius
    right = player.pos + player.direction.rotate(-140) * player.radius
    pygame.draw.polygon(screen, player.color, [tip, left, right])

    for projectile in game.projectiles:
        pygame.draw.circle(screen, (255, 240, 120), projectile.pos, projectile.radius)
    for enemy in game.enemies:
        pygame.draw.circle(screen, enemy.color, enemy.pos, enemy.radius)


def draw_hud(game, font):
    player = game.player
    wave_manager = game.wave_manager
    wave_number = min(wave_manager.wave_index + 1, len(content.WAVES))
    hud = (
        f"Health {player.health:.0f}/{player.max_health:.0f}   Score {game.score}   "
        f"Time {game.elapsed_time:.1f}s   Cycle {wave_manager.cycle}   "
        f"Wave {wave_number}/{len(content.WAVES)}"
    )
    game.screen.blit(font.render(hud, True, TEXT_COLOR), (12, 10))


def draw_wave_upgrade_popup(game, font):
    """Discreet line at the bottom of the screen, the game is paused until a pick."""
    choices = "   ".join(f"{number} - {upgrade['label']}" for number, upgrade in enumerate(game.wave_upgrade_choices, start=1))
    text = f"Upgrade:   {choices}"
    rendered = font.render(text, True, UPGRADE_COLOR)
    screen_rect = game.screen.get_rect()
    game.screen.blit(rendered, rendered.get_rect(midbottom=(screen_rect.centerx, screen_rect.bottom - 12)))


def draw_centered_lines(surface, lines, top):
    """lines: list of (text, font, color), drawn centered horizontally from y = top."""
    center_x = surface.get_rect().centerx
    for text, font, color in lines:
        rendered = font.render(text, True, color)
        surface.blit(rendered, rendered.get_rect(midtop=(center_x, top)))
        top += rendered.get_height() + 10


def draw_overlay(surface):
    shade = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 180))
    surface.blit(shade, (0, 0))


def draw_cycle_summary(game, font, big_font):
    cycle = game.wave_manager.cycle
    lines = [(f"Cycle {cycle} complete", big_font, (120, 230, 140)), ("Enemies next cycle:", font, TEXT_COLOR)]
    for name in content.ENEMY_CLASSES:
        current, upcoming = create_enemy(name, Vector2(), cycle), create_enemy(name, Vector2(), cycle + 1)
        lines.append((
            f"{name.capitalize()}: health {current.max_health} -> {upcoming.max_health}, "
            f"damage {current.contact_damage} -> {upcoming.contact_damage}",
            font, TEXT_COLOR,
        ))
    lines.append(("Choose a cycle upgrade:", font, TEXT_COLOR))
    for number, upgrade in enumerate(game.cycle_upgrade_choices, start=1):
        lines.append((f"{number} - {upgrade['label']}", font, UPGRADE_COLOR))
    draw_overlay(game.screen)
    draw_centered_lines(game.screen, lines, top=180)


def draw_game_over(game, font, big_font):
    lines = [("GAME OVER", big_font, (255, 90, 90)), ("Press R to restart", font, TEXT_COLOR)]
    draw_overlay(game.screen)
    draw_centered_lines(game.screen, lines, top=game.screen.get_rect().centery - 60)


def draw(game, fonts):
    game.screen.fill(BG_COLOR)
    draw_world(game, fonts["small"])
    draw_hud(game, fonts["normal"])
    if game.state == "wave_upgrade":
        draw_wave_upgrade_popup(game, fonts["normal"])
    elif game.state == "cycle_summary":
        draw_cycle_summary(game, fonts["normal"], fonts["big"])
    elif game.state == "game_over":
        draw_game_over(game, fonts["normal"], fonts["big"])
    pygame.display.flip()
