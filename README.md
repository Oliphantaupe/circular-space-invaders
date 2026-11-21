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
| Z / Q / S / D or arrows | Move |
| Mouse | Aim |
| Left click or Space | Shoot |
| 1 / 2 / 3 | Pick an upgrade (after a wave or a cycle) |
| R | Restart after game over |
| F1 | Toggle the debug grid (distance rings and angles around the player) |

## How it plays

- Enemies spawn on a ring around the player and fly straight at them.
- A **cycle** is every wave in `content.WAVES`, played in order. When a cycle ends, a summary screen shows how enemy health and damage will grow, and you pick one of 3 random big upgrades. Then the next, harder cycle starts. Cycles never end.
- After each other wave, the game pauses and a small popup at the bottom offers 3 random small upgrades: press 1, 2 or 3.
- **Upgrades** change the player's stats (health, damage, defense, multishot, fire rate, move speed). Each projectile copies the shot stats when it is fired.

## Project structure

| File | Contents |
|---|---|
| `main.py` | Entry point: game loop and input handling |
| `game/content.py` | Game design data: player and enemy classes (`Ship` -> `Player` and `Enemy` -> `BasicEnemy`, `EliteEnemy`, `BossEnemy`, values only), waves, cycle scaling, upgrades |
| `game/game_state.py` | Runtime state: `Projectile`, `WaveManager`, `Game` |
| `game/game_logic.py` | All behaviour: waves and cycles, upgrades, movement, shooting, collisions |
| `game/rendering.py` | Everything drawn on screen |

To tune the game (player and enemy stats, waves, scaling, upgrades), edit `game/content.py`. You don't need to touch the logic.

To add an enemy type, subclass `Enemy` in `game/content.py`, set its values, add it to `ENEMY_CLASSES` and use its name in `WAVES`.

## License

[GPL-3.0](LICENSE)
