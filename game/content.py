"""Game design data: enemy types, waves, cycle scaling and upgrades.

Tune the game here without touching the logic.
"""

ENEMY_TYPES = {
    "enemy": {"health": 1, "speed": 60, "contact_damage": 10, "radius": 14, "score": 10, "color": (230, 70, 90)},
    "elite": {"health": 3, "speed": 50, "contact_damage": 20, "radius": 18, "score": 30, "color": (240, 160, 60)},
    "boss": {"health": 15, "speed": 35, "contact_damage": 50, "radius": 30, "score": 200, "color": (180, 80, 230)},
}

# One cycle = all these waves in order. The game then starts the next, harder cycle.
WAVES = [
    {"enemy": 1},
    {"enemy": 2},
    {"enemy": 2, "elite": 1},
    {"enemy": 3, "elite": 1},
    {"enemy": 2, "boss": 1},
]

# Placeholder scaling between cycles, the final formula is not decided yet.
EXTRA_ENEMIES_PER_CYCLE = 1         # added to every count of every wave, per cycle
HEALTH_GROWTH_PER_CYCLE = 0.5       # +50% of base health per cycle
DAMAGE_GROWTH_PER_CYCLE = 0.25      # +25% of base contact damage per cycle

# Picked on the cycle summary screen. "stat" is a Player attribute, "amount" is added to it.
UPGRADES = {
    "damage": {"label": "Damage +1", "stat": "damage", "amount": 1},
    "shot_speed": {"label": "Shot speed +150", "stat": "shot_speed", "amount": 150},
}
