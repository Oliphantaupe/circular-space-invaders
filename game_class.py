class Ship:
    def __init__(
        self,
        is_player: bool,
        is_enemy: bool,
        health_point: float,
        attack_damage: float,
        attack_delay: float,
        defense_amount: float,
        projectile_amount: int,
        projectile_spread: int,
        projectile_speed: float,
        movement_speed: float,
        angle: int,
        position: list[int],
        shape: str,
        color: str,
        size: int,
    ) -> None:
        self.is_player = is_player
        self.is_enemy = is_enemy
        self.health_point = health_point
        self.attack_damage = attack_damage
        self.attack_delay = attack_delay
        self.defense_amount = defense_amount
        self.projectile_amount = projectile_amount
        self.projectile_spread = projectile_spread
        self.projectile_speed = projectile_speed
        self.movement_speed = movement_speed
        self.angle = angle
        self.position = list(position)
        self.shape = shape
        self.color = color
        self.size = size


class Player(Ship):
    def __init__(self, position: list[float]):
        super().__init__(
            is_player = True,
            is_enemy = False,
            health_point = 100,
            attack_damage = 10,
            attack_delay = 0.2,
            defense_amount = 0,
            projectile_amount = 1,
            projectile_spread = 0,
            projectile_speed = 200,
            movement_speed = 20,
            angle = 0,
            position = position,
            shape = "triangle",
            color = "blue",
            size = 20,
        )


class Basic_Enemy(Ship):
    def __init__(self, position: list[float] | None = None) -> None:
        super().__init__(
            is_player = False,
            is_enemy = True,
            health_point = 10,
            attack_damage = 10,
            attack_delay = None,
            defense_amount = 0,
            projectile_amount = None,
            projectile_spread = None,
            projectile_speed = None,
            movement_speed = 10,
            angle = 0,
            position = position,
            shape = "circle",
            color = "red",
            size = 15,
        )


class Elite_Enemy(Ship):
    def __init__(self, position: list[float]):
        super().__init__(
            is_player = False,
            is_enemy = True,
            health_point = 25,
            attack_damage = 20,
            attack_delay = None,
            defense_amount = 0,
            projectile_amount = None,
            projectile_spread = None,
            projectile_speed = None,
            movement_speed = 8,
            angle = 0,
            position = position,
            shape = "circle",
            color = "orange",
            size = 25,
        )


class Boss_Enemy(Ship):
    def __init__(self, position: list[float]):
        super().__init__(
            is_player = False,
            is_enemy = True,
            health_point = 100,
            attack_damage = 60,
            attack_delay = None,
            defense_amount = 0,
            projectile_amount = None,
            projectile_spread = None,
            projectile_speed = None,
            movement_speed = 6,
            angle = 0,
            position = position,
            shape = "circle",
            color = "purple",
            size = 50,
        )


class Projectile:
    def __init__(self, shooter: Ship):
        self.attack_damage = shooter.attack_damage
        self.angle = shooter.angle
        self.position = shooter.position.copy()
        self.is_player = shooter.is_player
        self.is_enemy = shooter.is_enemy
        self.speed = shooter.projectile_speed


class UI:
    def __init__(
        self,
        score: int = 0,
        time: float = 0,
        life: float = 0,
        wave: int = 1,
    ) -> None:
        self.score = score
        self.time = time
        self.life = life
        self.wave = wave