"""Everything drawn on screen."""
import pygame

from . import assets
from .game_logic import PROJECTILE_SIZE, SPAWN_RADIUS, enemy_classes, point_at, scaled_enemy

TEXT_COLOR = (220, 220, 230)
GRID_COLOR = (35, 35, 60)
UPGRADE_COLOR = (255, 240, 120)
GRID_RING_STEP = 100        # pixels between debug rings
GRID_SECTORS = 12           # debug angle sectors (30 degrees each)
BOLT_LENGTH = 16            # length of a projectile's laser bolt in pixels
BOLT_COLOR = (230, 250, 255)
BOLT_GLOW_COLOR = (40, 140, 200)
SPRITE_SCALE = 2.5          # a sprite's longest side is SPRITE_SCALE * the ship's size (hitbox radius)
SPRITE_FACING = -90         # every ship image points up (-90 degrees)

# Ship class name -> image name in assets.images. Classes not listed are drawn from their shape and color.
SHIP_SPRITES = {
    "Player": "player",
    "Basic_Enemy": "basic_enemy",
    "Elite_Enemy": "elite_enemy",
    "Boss_Enemy": "boss_enemy",
}


def draw_debug_grid(surface, center, max_radius, font):
    """Polar grid: rings by distance from the player, sectors by angle (0 = right, clockwise)."""
    for radius in range(GRID_RING_STEP, int(max_radius) + 1, GRID_RING_STEP):
        pygame.draw.circle(surface, GRID_COLOR, center, radius, 1)
        surface.blit(font.render(str(radius), True, GRID_COLOR), (center[0] + radius + 3, center[1] + 2))
    for sector in range(GRID_SECTORS):
        angle = sector * 360 / GRID_SECTORS
        pygame.draw.line(surface, GRID_COLOR, center, point_at(center, angle, max_radius), 1)
        label = font.render(f"{angle:.0f}", True, GRID_COLOR)
        surface.blit(label, label.get_rect(center=point_at(center, angle, max_radius + 20)))


def draw_sprite(surface, image, position, angle, length):
    """Draws image centered on position, rotated to face angle, its longest side scaled to length."""
    scale = length / max(image.get_size())
    rotated = pygame.transform.rotozoom(image, SPRITE_FACING - angle, scale)
    surface.blit(rotated, rotated.get_rect(center=position))


def draw_ship(surface, ship):
    image_name = SHIP_SPRITES.get(type(ship).__name__)
    if image_name in assets.images:
        draw_sprite(surface, assets.images[image_name], ship.position, ship.angle, SPRITE_SCALE * ship.size)
    elif ship.shape == "circle":
        pygame.draw.circle(surface, ship.color, ship.position, ship.size)
    elif ship.shape == "triangle":
        tip = point_at(ship.position, ship.angle, ship.size + 10)
        left = point_at(ship.position, ship.angle + 140, ship.size)
        right = point_at(ship.position, ship.angle - 140, ship.size)
        pygame.draw.polygon(surface, ship.color, [tip, left, right])
    else:
        raise ValueError(f"Unknown shape: {ship.shape}")


def draw_bolt(surface, projectile):
    """Laser bolt: a short bright line with a wider dark glow behind it, pointing where it flies."""
    tail = point_at(projectile.position, projectile.angle + 180, BOLT_LENGTH)
    pygame.draw.line(surface, BOLT_GLOW_COLOR, tail, projectile.position, PROJECTILE_SIZE + 1)
    pygame.draw.line(surface, BOLT_COLOR, tail, projectile.position, 2)


def draw_world(game, small_font):
    screen = game.screen
    player = game.player
    if game.show_debug_grid:
        draw_debug_grid(screen, player.position, SPAWN_RADIUS, small_font)
    draw_ship(screen, player)
    for projectile in game.projectiles:
        draw_bolt(screen, projectile)
    for enemy in game.enemies:
        draw_ship(screen, enemy)


def draw_hud(game, font):
    ui = game.ui
    hud = (
        f"Health {ui.life:.0f}/{game.max_health_point:.0f}   Score {ui.score}   "
        f"Time {ui.time:.1f}s   Wave {ui.wave}"
    )
    game.screen.blit(font.render(hud, True, TEXT_COLOR), (12, 10))


def draw_wave_upgrade_popup(game, font):
    """Discreet line at the bottom of the screen, the game is paused until a pick."""
    choices = "   ".join(f"{number} - {upgrade.capitalize()}" for number, upgrade in enumerate(game.wave_upgrade_choices, start=1))
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
    for enemy_class in enemy_classes():
        current, upcoming = scaled_enemy(enemy_class, cycle), scaled_enemy(enemy_class, cycle + 1)
        lines.append((
            f"{enemy_class.__name__.replace('_', ' ')}: health {current.health_point:.0f} -> {upcoming.health_point:.0f}, "
            f"damage {current.attack_damage:.0f} -> {upcoming.attack_damage:.0f}",
            font, TEXT_COLOR,
        ))
    lines.append(("Choose a cycle upgrade:", font, TEXT_COLOR))
    for number, upgrade in enumerate(game.cycle_upgrade_choices, start=1):
        lines.append((f"{number} - {upgrade.capitalize()}", font, UPGRADE_COLOR))
    draw_overlay(game.screen)
    draw_centered_lines(game.screen, lines, top=180)


def draw_game_over(game, font, big_font):
    lines = [("GAME OVER", big_font, (255, 90, 90)), ("Press R to restart", font, TEXT_COLOR)]
    draw_overlay(game.screen)
    draw_centered_lines(game.screen, lines, top=game.screen.get_rect().centery - 60)


def draw(game, fonts):
    game.screen.blit(assets.background, (0, 0))
    draw_world(game, fonts["small"])
    draw_hud(game, fonts["normal"])
    if game.state == "wave_upgrade":
        draw_wave_upgrade_popup(game, fonts["normal"])
    elif game.state == "cycle_summary":
        draw_cycle_summary(game, fonts["normal"], fonts["big"])
    elif game.state == "game_over":
        draw_game_over(game, fonts["normal"], fonts["big"])
    pygame.display.flip()
