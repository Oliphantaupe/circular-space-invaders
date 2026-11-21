"""Game design data: enemy types, waves, cycle scaling and upgrades.

Tune the game here without touching the logic.
"""

# "score" is multiplied by the cycle number when the enemy is killed.
ENEMY_TYPES = {
    "enemy": {"health": 10, "speed": 10, "contact_damage": 10, "radius": 15, "score": 10, "color": "red"},
    "elite": {"health": 25, "speed": 8, "contact_damage": 20, "radius": 25, "score": 30, "color": "orange"},
    "boss": {"health": 100, "speed": 6, "contact_damage": 60, "radius": 50, "score": 200, "color": "purple"},
}

# One cycle = all these waves in order. The game then starts the next, harder cycle.
WAVES = [
    {"enemy": 5},
    {"enemy": 7, "elite": 1},
    {"enemy": 6, "elite": 2},
    {"enemy": 8, "elite": 3},
    {"enemy": 5, "elite": 2, "boss": 1},
]

# Scaling between cycles: wave counts are multiplied by the cycle number,
# enemy health and contact damage by STAT_GROWTH_PER_CYCLE ** (cycle - 1).
STAT_GROWTH_PER_CYCLE = 1.5

WAVE_END_HEAL = 0.20                # fraction of max health restored when a wave is cleared

UPGRADES_OFFERED = 3                # random upgrades shown on the cycle summary screen

# "stat" is a Player attribute. "add" adds "amount" to it, "multiply" multiplies it by "amount".
UPGRADES = {
    "health": {"label": "Max health +10%", "stat": "max_health", "operation": "multiply", "amount": 1.10},
    "attack": {"label": "Damage +15%", "stat": "damage", "operation": "multiply", "amount": 1.15},
    "defense": {"label": "Defense +1", "stat": "defense", "operation": "add", "amount": 1},
    "multishot": {"label": "Multishot +1", "stat": "projectile_count", "operation": "add", "amount": 1},
    "attack_speed": {"label": "Fire rate +10%", "stat": "shot_cooldown", "operation": "multiply", "amount": 1 / 1.10},
    "rotation_speed": {"label": "Rotation speed +10%", "stat": "rotation_speed", "operation": "multiply", "amount": 1.10},
}
