"""Runtime game state that is not part of the ships: wave spawner and the game itself.

Ships, projectiles and the UI are the classes in game_class.py.
"""
import pygame

from .game_class import Player, UI


class WaveManager:
    """Spawner: tracks the current cycle/wave and the enemies left to release."""
    def __init__(self):
        self.cycle = 1                      # one cycle = every wave in game_content.waves
        self.wave_index = -1                # index in game_content.waves, -1 before the first wave
        self.spawn_queue = []               # enemies created by spawn_wave, not on screen yet
        self.spawn_timer = 0.0


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((1000, 700))
        self.clock = pygame.time.Clock()
        self.state = "playing"              # "playing" | "wave_upgrade" | "cycle_summary" | "game_over"
        self.player = Player(list(self.screen.get_rect().center))
        self.player.angle = -90             # facing up
        self.max_health_point = self.player.health_point    # health_point is the current health
        self.shot_timer = 0.0               # seconds until the player can shoot again
        self.enemies = []
        self.projectiles = []
        self.wave_manager = WaveManager()
        self.ui = UI(life=self.player.health_point)
        self.show_debug_grid = False
        self.wave_upgrade_choices = []      # names from game_content.wave_upgrades offered in the popup
        self.cycle_upgrade_choices = []     # names from game_content.cycle_upgrades offered on the summary
