"""Entry point: game loop and input handling.

Controls: Z/Q/S/D or arrows move, the mouse aims, left click or Space shoots,
1/2/3 pick an upgrade after a wave or a cycle,
R restarts after game over, F1 toggles the debug grid.
"""
import pygame

from game import classes
from game import game_logic
from game import rendering

UPGRADE_KEYS = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2}   # key -> index in the offered upgrades


def handle_keydown(game, key):
    """Returns the game to keep playing with (a new one on restart)."""
    if key == pygame.K_F1:
        game.show_debug_grid = not game.show_debug_grid
    elif key == pygame.K_r and game.state == "game_over":
        return classes.Game()
    elif key in UPGRADE_KEYS and game.state == "cycle_summary":
        game_logic.start_next_cycle(game, UPGRADE_KEYS[key])
    elif key in UPGRADE_KEYS and game.state == "wave_upgrade":
        game_logic.pick_wave_upgrade(game, UPGRADE_KEYS[key])
    return game


def main():
    pygame.init()
    pygame.display.set_caption("Circular Space Invaders")
    fonts = {
        "small": pygame.font.Font(None, 20),
        "normal": pygame.font.Font(None, 28),
        "big": pygame.font.Font(None, 72),
    }
    game = classes.Game()
    running = True
    while running:
        dt = game.clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                game = handle_keydown(game, event.key)
        if game.state == "playing":
            game_logic.update_playing(game, dt)
        rendering.draw(game, fonts)
    pygame.quit()


if __name__ == "__main__":
    main()
