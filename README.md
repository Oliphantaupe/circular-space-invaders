# Circular Space Invaders

A space shooter where enemies come in from every direction. You move around the screen, aim with the mouse and shoot them before they reach you.

> **Work in progress.** Each version is a proof of concept for testing our changes. Nothing here is final: mechanics, numbers and visuals will change.

## Setup

Tested with Python 3.15.

```bash
python3 -m venv .venv
source .venv/bin/activate        # fish: source .venv/bin/activate.fish
pip install -r requirements.txt
python main.py
```

## Controls

| Key | Action |
|---|---|
| Z / Q / S / D or arrows | Move |
| Mouse | Aim |
| Left click or Space | Shoot |
| 1 / 2 / 3 | Pick an upgrade (after a wave or a cycle) |
| R | Restart after game over |
| F1 | Toggle the debug grid (distance rings and angles around the player) |

## How it plays

- Enemies spawn on a ring around the player and fly straight at them.
- A **cycle** is every wave in `game_content.waves`, played in order. When a cycle ends, a summary screen shows how enemy health and damage will grow, and you pick one of 3 random cycle upgrades. Then the next, harder cycle starts. Cycles never end.
- After each other wave, the game pauses and a small popup at the bottom offers 3 random wave upgrades: press 1, 2 or 3.
- **Upgrades** change the player's stats (see `apply_upgrade` in `game_content.py`). Each projectile copies the shooter's stats when it is fired.

## Project structure

| File | Contents |
|---|---|
| `main.py` | Entry point: opens the window and runs the game loop |
| `game/game_class.py` | Ships (`Ship` -> `Player`, `Basic_Enemy`, `Elite_Enemy`, `Boss_Enemy`) with their stats, `Projectile`, `UI` |
| `game/game_content.py` | Waves, upgrade lists and their effects (`apply_upgrade`), wave spawning and cycle scaling (`scale_wave`) |
| `game/game_state.py` | A game in progress: `WaveManager` (cycles, waves, enemy release) and `Game` (player actions, health, upgrades, movement, collisions), plus spawn ring, heal and projectile size settings and geometry helpers (`point_at`, `move`, `angle_towards`, `collides`) |
| `game/screens.py` | One class per screen (`Screen` -> `PlayingScreen`, `GameOverScreen`, `UpgradeScreen` -> `WaveUpgradeScreen`, `CycleSummaryScreen`): controls, screen changes and what each screen draws |
| `game/rendering.py` | Drawing helpers shared by the screens: world, HUD, menus |
| `game/assets.py` | `Assets`: loads the images, fonts, sounds and music from `assets/` |

To tune the ships, edit their class in `game/game_class.py`. Waves, upgrades and scaling are in `game/game_content.py`.

To add an enemy type, add a `Ship` subclass in `game/game_class.py` and use the class in `waves`. To add an upgrade, add its name to `wave_upgrades` or `cycle_upgrades` and its effect in `apply_upgrade`. To add a screen (pause, menu...), add a `Screen` subclass in `game/screens.py`.

Images face right (angle 0) and are already the size a ship has when it is created (2.5 x its `size`); a new ship class needs its image in `SHIP_IMAGE_FILES` (`game/assets.py`).

## Credits

Enemy ships by Skorpio (GPL 3.0 / CC-BY-SA 3.0), background photo by Francesco Ungaro (Pexels), player ship by wuhu (CC-BY 3.0), sounds by Kenney (CC0), music "Angel Eyes (Vision II)" by Kim Lightyear (CC-BY-SA), Orbitron font (SIL Open Font License). Details and links in [assets/CREDITS.md](assets/CREDITS.md).

## License

[GPL-3.0](LICENSE)
