from game_class import *

waves = [{"enemy":5},{"enemy":7, "elite":1},{"enemy":6, "elite":2},{"enemy":8, "elite":3},{"enemy":5, "elite":2, "boss":1}]

enemy_classes = {"enemy": Basic_Enemy, "elite": Elite_Enemy, "boss": Boss_Enemy}

upgrades = ["health up", "attack up", "defense up", "multishot", "attack speed up", "move speed up"]

def apply_upgrade(player, upgrade):
    if upgrade == "health up":
        player.health_point *= 1.10
    elif upgrade == "attack up":
        player.attack_damage *= 1.15
    elif upgrade == "defense up":
        player.defense_amount += 1
    elif upgrade == "multishot":
        player.projectile_amount += 1
    elif upgrade == "attack speed up":
        player.attack_delay /= 1.10
    elif upgrade == "move speed up":
        player.movement_speed *= 1.10
    else:
        raise ValueError(f"Unknown upgrade: {upgrade}")

def spawn_wave(wave, cycle, position):
    enemies = []
    stat_mult = 1.5 ** (cycle - 1)

    for enemy_type, enemy_amount in wave.items():
        enemy_class = enemy_classes[enemy_type]

        for i in range(enemy_amount * cycle):
            enemy = enemy_class(position())
            enemy.health_point *= stat_mult
            enemy.attack_damage *= stat_mult
            enemies.append(enemy)

    return enemies