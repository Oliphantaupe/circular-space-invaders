"""Entry point: opens the window and runs the game loop.

Controls: Z/Q/S/D or arrows move, the mouse aims, left click or Space shoots,
1/2/3 pick an upgrade after a wave or a cycle,
R restarts after game over, F1 toggles the debug grid.
"""
import pygame

from game.assets import Assets
from game.game_state import Game
from game.screens import PlayingScreen

WINDOW_SIZE = (1000, 700)
FPS = 60


def main():
    pygame.init()
    pygame.display.set_caption("Circular Space Invaders")
    window = pygame.display.set_mode(WINDOW_SIZE)
    clock = pygame.time.Clock()
    assets = Assets()
    screen = PlayingScreen(Game(assets, window.get_rect()))
    running = True
    while running:
        dt = clock.tick(FPS) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                screen = screen.handle_key(event.key)
        screen = screen.update(dt)
        screen.draw(window)
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()
