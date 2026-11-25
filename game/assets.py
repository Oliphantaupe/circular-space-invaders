"""Images, sounds, music and fonts from the assets folder (credits in assets/CREDITS.md)."""
import os

import pygame

from .game_class import Basic_Enemy, Boss_Enemy, Elite_Enemy, Player

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
FONT_PATH = os.path.join(ASSETS_DIR, "fonts", "Orbitron.ttf")
MUSIC_PATH = os.path.join(ASSETS_DIR, "music", "angel_eyes.ogg")

# Ship class -> image. Every image faces right (angle 0) and is already the size the ship has
# when it is created (SPRITE_SCALE * size in rendering.py).
SHIP_IMAGE_FILES = {
    Player: "player.png",
    Basic_Enemy: "basic_enemy.png",
    Elite_Enemy: "elite_enemy.png",
    Boss_Enemy: "boss_enemy.png",
}
DEFAULT_SHIP_CLASS = Basic_Enemy    # its image is used for ship classes not listed above
SOUND_FILES = {
    "shoot": "shoot.ogg",
    "enemy_killed": "enemy_killed.ogg",
    "game_over": "game_over.ogg",
}
FONT_SIZES = {"small": 13, "normal": 18, "big": 44}
SOUND_VOLUME = 0.4
MUSIC_VOLUME = 0.25         # quieter than the sound effects


def load_image(file_name):
    return pygame.image.load(os.path.join(ASSETS_DIR, "images", file_name)).convert_alpha()


class Assets:
    """Loads everything once, after the window is created, and starts the music (looping)."""
    def __init__(self):
        window_size = pygame.display.get_surface().get_size()
        self.background = pygame.transform.smoothscale(load_image("background.jpg"), window_size)
        self.projectile_image = load_image("projectile.png")
        self.ship_images = {}
        for ship_class, file_name in SHIP_IMAGE_FILES.items():
            self.ship_images[ship_class] = load_image(file_name)
        self.fonts = {}
        for name, size in FONT_SIZES.items():
            self.fonts[name] = pygame.font.Font(FONT_PATH, size)
        self.sounds = {}
        if pygame.mixer.get_init():     # no audio device: the game runs silently
            for name, file_name in SOUND_FILES.items():
                self.sounds[name] = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "sounds", file_name))
                self.sounds[name].set_volume(SOUND_VOLUME)
            pygame.mixer.music.load(MUSIC_PATH)
            pygame.mixer.music.set_volume(MUSIC_VOLUME)
            pygame.mixer.music.play(-1)

    def ship_image(self, ship):
        return self.ship_images.get(type(ship), self.ship_images[DEFAULT_SHIP_CLASS])

    def play_sound(self, name):
        if name in self.sounds:
            self.sounds[name].play()
