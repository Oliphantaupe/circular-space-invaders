# Circular Space Invaders

A space shooter where your ship sits fixed in the center of the screen. Enemies come in from every direction, and you rotate to aim and shoot before they reach you.

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
| Left / Right or A / D | Rotate |
| Space | Shoot |
| 1 / 2 / 3 | Pick an upgrade at the end of a cycle |
| R | Restart after game over |
| F1 | Toggle the debug grid (distance rings and angles around the player) |

## How it plays

- A **cycle** is every wave in `content.WAVES`, played in order. When a cycle ends, a summary screen shows how enemy health and damage will grow, and you pick one of 3 random upgrades. Then the next, harder cycle starts. Cycles never end.
- **Upgrades** change the player's stats (health, damage, defense, multishot, fire rate, rotation speed). Each projectile copies the shot stats when it is fired.

## Project structure

| File | Contents |
|---|---|
| `main.py` | Entry point: game loop and input handling |
| `game/classes.py` | Game entities: `Player`, `Projectile`, `Enemy`, `WaveManager`, `Game` |
| `game/content.py` | Game design data: enemy types, waves, cycle scaling, upgrades |
| `game/game_logic.py` | Behaviour: waves and cycles, upgrades, movement, collisions |
| `game/rendering.py` | Everything drawn on screen |

To tune the game (enemy stats, wave composition, scaling, upgrades), edit `game/content.py`. You don't need to touch the logic.

## License

[GPL-3.0](LICENSE)
