"""What the game shows and how it reacts to input: one class per screen.

main.py only talks to the current screen. handle_key() and update() return the screen to show
next (self to stay on it), draw() draws it. Every screen draws the game world under it.
"""
import random

import pygame

from . import game_content
from . import rendering
from .game_state import Game, enemy_classes, scaled_enemy

UPGRADES_OFFERED = 3        # upgrades to choose from
UPGRADE_KEYS = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2}   # key -> index in the offered upgrades
MOVE_KEYS = {               # key -> (x, y) movement (Z/Q/S/D on AZERTY, plus arrows)
    pygame.K_z: (0, -1), pygame.K_UP: (0, -1),
    pygame.K_s: (0, 1), pygame.K_DOWN: (0, 1),
    pygame.K_q: (-1, 0), pygame.K_LEFT: (-1, 0),
    pygame.K_d: (1, 0), pygame.K_RIGHT: (1, 0),
}


class Screen:
    """Base screen: the world is frozen and drawn, F1 toggles the debug grid."""
    def __init__(self, game):
        self.game = game

    def handle_key(self, key):
        if key == pygame.K_F1:
            self.game.show_debug_grid = not self.game.show_debug_grid
        return self

    def update(self, dt):
        return self

    def draw(self, surface):
        rendering.draw_world(surface, self.game)
        rendering.draw_hud(surface, self.game)


class PlayingScreen(Screen):
    """The game runs: reads the controls, then moves to an upgrade or game over screen when needed."""
    def update(self, dt):
        game = self.game
        game.move_player(self.move_direction(), dt)
        game.aim_player(pygame.mouse.get_pos())
        if pygame.key.get_pressed()[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]:
            game.shoot()
        game.update(dt)

        if game.is_player_dead():
            game.assets.play_sound("game_over")
            return GameOverScreen(game)
        if game.is_wave_cleared():
            game.end_wave()
            if game.wave_manager.is_last_wave():
                return CycleSummaryScreen(game)
            game.wave_manager.next_wave()
            return WaveUpgradeScreen(game)
        return self

    def move_direction(self):
        keys = pygame.key.get_pressed()
        x, y = 0, 0
        for key, (key_x, key_y) in MOVE_KEYS.items():
            if keys[key]:
                x += key_x
                y += key_y
        return x, y


class UpgradeScreen(Screen):
    """The game is paused until the player picks one of UPGRADES_OFFERED random upgrades with 1/2/3."""
    def __init__(self, game, upgrades):
        super().__init__(game)
        self.choices = random.sample(upgrades, UPGRADES_OFFERED)

    def handle_key(self, key):
        if key in UPGRADE_KEYS:
            self.game.upgrade_player(self.choices[UPGRADE_KEYS[key]])
            return self.after_pick()
        return super().handle_key(key)

    def after_pick(self):
        return PlayingScreen(self.game)


class WaveUpgradeScreen(UpgradeScreen):
    """Small upgrade after each wave of a cycle but the last: a discreet line at the bottom."""
    def __init__(self, game):
        super().__init__(game, game_content.wave_upgrades)

    def draw(self, surface):
        super().draw(surface)
        choices = "   ".join(f"{number} - {upgrade.capitalize()}" for number, upgrade in enumerate(self.choices, start=1))
        rendered = self.game.assets.fonts["normal"].render(f"Upgrade:   {choices}", True, rendering.UPGRADE_COLOR)
        bounds = surface.get_rect()
        surface.blit(rendered, rendered.get_rect(midbottom=(bounds.centerx, bounds.bottom - 12)))


class CycleSummaryScreen(UpgradeScreen):
    """Big upgrade at the end of a cycle, with how much stronger the enemies get in the next one."""
    def __init__(self, game):
        super().__init__(game, game_content.cycle_upgrades)

    def after_pick(self):
        self.game.wave_manager.next_cycle()
        return super().after_pick()

    def draw(self, surface):
        super().draw(surface)
        fonts = self.game.assets.fonts
        cycle = self.game.wave_manager.cycle
        lines = [(f"Cycle {cycle} complete", fonts["big"], (120, 230, 140)),
                 ("Enemies next cycle:", fonts["normal"], rendering.TEXT_COLOR)]
        for enemy_class in enemy_classes():
            current, upcoming = scaled_enemy(enemy_class, cycle), scaled_enemy(enemy_class, cycle + 1)
            lines.append((
                f"{enemy_class.__name__.replace('_', ' ')}: health {current.health_point:.0f} -> {upcoming.health_point:.0f}, "
                f"damage {current.attack_damage:.0f} -> {upcoming.attack_damage:.0f}",
                fonts["normal"], rendering.TEXT_COLOR,
            ))
        lines.append(("Choose a cycle upgrade:", fonts["normal"], rendering.TEXT_COLOR))
        for number, upgrade in enumerate(self.choices, start=1):
            lines.append((f"{number} - {upgrade.capitalize()}", fonts["normal"], rendering.UPGRADE_COLOR))
        rendering.draw_menu(surface, lines, top=180)


class GameOverScreen(Screen):
    """R starts a new game."""
    def handle_key(self, key):
        if key == pygame.K_r:
            return PlayingScreen(Game(self.game.assets, self.game.bounds))
        return super().handle_key(key)

    def draw(self, surface):
        super().draw(surface)
        fonts = self.game.assets.fonts
        lines = [("GAME OVER", fonts["big"], (255, 90, 90)), ("Press R to restart", fonts["normal"], rendering.TEXT_COLOR)]
        rendering.draw_menu(surface, lines, top=surface.get_rect().centery - 60)
