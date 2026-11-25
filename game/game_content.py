from .game_class import *

waves = [
    {Basic_Enemy: 5}, #wave 1
    {Basic_Enemy: 7, Elite_Enemy: 1}, #wave 2
    {Basic_Enemy: 6, Elite_Enemy: 2}, #wave 3
    {Basic_Enemy: 8, Elite_Enemy: 3}, #wave 4
    {Basic_Enemy: 5, Elite_Enemy: 2, Boss_Enemy: 1}, #wave 5
        ]

wave_upgrades = ["health up", "attack up", "defense up", "multishot", "attack speed up", "move speed up", "accuracy up", "bullet speed up"]
cycle_upgrades = ["tank", "high caliber", "shotgunner", "slug bullet", "octogun", "condensed shot", "strifer", "colossus", "micro drone"]

def apply_upgrade(player, upgrade):
    """Apply the chosen stat upgrade to the player ship.

    player: the player ship (object)
    upgrade: upgrade to apply (str)
    """
    # Wave upgrades
    if upgrade == "health up":
        player.health_point *= 1.1
    elif upgrade == "attack up":
        player.attack_damage *= 1.15
    elif upgrade == "defense up":
        player.defense_amount += 2
        player.defense_amount *= 1.1
    elif upgrade == "multishot":
        player.projectile_amount += 1
        if player.projectile_spread == 0:
            player.projectile_spread = 10
    elif upgrade == "attack speed up":
        player.attack_delay *= 0.9
    elif upgrade == "move speed up":
        player.movement_speed *= 1.1
    elif upgrade == "accuracy up":
        player.projectile_spread *= 0.75
    elif upgrade == "bullet speed up":
        player.projectile_speed *= 1.25

    # Cycle upgrades
    elif upgrade == "tank":
        player.health_point *= 1.25
        player.defense_amount += 5
        player.defense_amount *= 1.2
        player.movement_speed *= 0.75
    elif upgrade == "high caliber":
        player.attack_damage *= 1.5
        player.attack_delay *= 1.4
        player.projectile_speed *= 1.5
    elif upgrade == "shotgunner":
        player.projectile_amount += 5
        player.attack_damage *= 0.7
        player.attack_delay *= 1.6
        player.projectile_spread = 90/player.projectile_amount
    elif upgrade == "slug bullet":
        player.projectile_amount += 3
        player.projectile_spread = 0
        player.projectile_speed *= 0.7
    elif upgrade == "octogun":
        player.attack_damage = player.attack_damage*player.projectile_amount/8
        player.projectile_amount = 8
        player.projectile_spread = 45
    elif upgrade == "condensed shot":
        player.projectile_spread *= 0.50
        player.attack_damage *= 1.25
        player.attack_delay *= 1.15
    elif upgrade == "strifer":
        player.attack_damage *= 0.5
        player.attack_delay *= 0.5
        player.projectile_speed *= 0.75
    elif upgrade == "colossus":
        player.health_point *= 2
        player.defense_amount += 3
        player.defense_amount *= 1.3
        player.attack_damage *= 1.3
        player.attack_delay *= 1.3
        player.movement_speed *= 0.5
        player.size += 10
    elif upgrade == "micro drone":
        player.health_point *= 0.75
        player.attack_damage *= 0.8
        player.attack_delay *= 0.8
        player.movement_speed *= 1.50
        player.size = max(5, player.size*0.7)
    else:
        raise ValueError(f"Unknown upgrade: {upgrade}")

def scale_wave(wave, cycle, position):
    """spawn enemies from a wave

    wave: amount of each enemy that will spzwn during the wave (dict)
    cycle: scaling of the wave depending of waves loop number (int)
    position: pos[x,y] of the enemy spawn (list), random.choice() should be used to randomize spawns
    """
    enemies = []
    stat_mult = 1.25 ** (cycle - 1)

    for enemy_class, enemy_amount in wave.items():
        for _ in range(enemy_amount * cycle):
            enemy = enemy_class(position())
            enemy.health_point *= stat_mult
            enemy.attack_damage *= stat_mult
            enemies.append(enemy)

    return enemies
