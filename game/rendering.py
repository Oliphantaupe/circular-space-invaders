"""Drawing helpers shared by the screens (screens.py): world, HUD, overlay and text."""
import pygame

from .game_state import SPAWN_RADIUS
from .geometry import point_at

TEXT_COLOR = (220, 220, 230)
UPGRADE_COLOR = (255, 240, 120)
GRID_COLOR = (35, 35, 60)
OVERLAY_COLOR = (0, 0, 0, 180)  # black, 180/255 opaque
GRID_RING_STEP = 100        # pixels between debug rings
GRID_SECTORS = 12           # debug angle sectors (30 degrees each)
SPRITE_SCALE = 2.5          # a ship image's longest side is SPRITE_SCALE * the ship's size (hitbox radius)


def draw_sprite(surface, image, position, angle, zoom=1):
    """Draws image (facing right) centered on position, rotated to face angle."""
    rotated = pygame.transform.rotozoom(image, -angle, zoom)
    surface.blit(rotated, rotated.get_rect(center=position))


def draw_ship(surface, ship, image):
    """The zoom follows the ship's size, which some upgrades change."""
    zoom = SPRITE_SCALE * ship.size / max(image.get_size())
    draw_sprite(surface, image, ship.position, ship.angle, zoom)


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


def draw_world(surface, game):
    assets = game.assets
    surface.blit(assets.background, (0, 0))
    if game.show_debug_grid:
        draw_debug_grid(surface, game.player.position, SPAWN_RADIUS, assets.fonts["small"])
    draw_ship(surface, game.player, assets.ship_images[type(game.player)])
    for projectile in game.projectiles:
        draw_sprite(surface, assets.projectile_image, projectile.position, projectile.angle)
    for enemy in game.enemies:
        draw_ship(surface, enemy, assets.ship_images[type(enemy)])


def draw_hud(surface, game):
    ui = game.ui
    hud = (
        f"Health {ui.life:.0f}/{game.max_health_point:.0f}   Score {ui.score}   "
        f"Time {ui.time:.1f}s   Wave {ui.wave}"
    )
    surface.blit(game.assets.fonts["normal"].render(hud, True, TEXT_COLOR), (12, 10))


def draw_overlay(surface):
    shade = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    shade.fill(OVERLAY_COLOR)
    surface.blit(shade, (0, 0))


def draw_centered_lines(surface, lines, top):
    """lines: list of (text, font, color), drawn centered horizontally from y = top."""
    center_x = surface.get_rect().centerx
    for text, font, color in lines:
        rendered = font.render(text, True, color)
        surface.blit(rendered, rendered.get_rect(midtop=(center_x, top)))
        top += rendered.get_height() + 10
