"""Loads images, sounds and the font from the assets folder (credits in assets/CREDITS.md)."""
import os

import pygame

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
FONT_PATH = os.path.join(ASSETS_DIR, "fonts", "Orbitron.ttf")

IMAGE_FILES = {
    "player": "player.png",
    "basic_enemy": "basic_enemy.png",
    "elite_enemy": "elite_enemy.png",
    "boss_enemy": "boss_enemy.png",
}
SOUND_FILES = {
    "shoot": "shoot.ogg",
    "enemy_killed": "enemy_killed.ogg",
    "game_over": "game_over.ogg",
}
SOUND_VOLUME = 0.4
NEBULA_ALPHA = 110          # 0 = invisible, 255 = full brightness

images = {}                 # name -> pygame.Surface, filled by load()
sounds = {}                 # name -> pygame.mixer.Sound, filled by load() if audio works
background = None           # stars + dimmed nebula, the size of the screen


def load_image(file_name):
    return pygame.image.load(os.path.join(ASSETS_DIR, "images", file_name)).convert_alpha()


def build_background(screen_size):
    """Black sky with stars, and a dimmed nebula on the right as an accent."""
    sky = pygame.Surface(screen_size)
    sky.fill((0, 0, 0))
    stars = load_image("stars.png")
    for x in range(0, screen_size[0], stars.get_width()):
        for y in range(0, screen_size[1], stars.get_height()):
            sky.blit(stars, (x, y))
    nebula = load_image("nebula.png")
    nebula.set_alpha(NEBULA_ALPHA)
    sky.blit(nebula, nebula.get_rect(midright=(screen_size[0] + 150, screen_size[1] // 2)))
    return sky


def load(screen_size):
    """Call once, after the window is created."""
    global background
    for name, file_name in IMAGE_FILES.items():
        images[name] = load_image(file_name)
    background = build_background(screen_size)
    if pygame.mixer.get_init():
        for name, file_name in SOUND_FILES.items():
            sounds[name] = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "sounds", file_name))
            sounds[name].set_volume(SOUND_VOLUME)


def play_sound(name):
    """Does nothing if the sounds could not be loaded (no audio device)."""
    if name in sounds:
        sounds[name].play()
