class Ship:
    def __init__(
        self,
        is_player: bool = False,
        is_enemy: bool = False,
        health_point: float = None,
        attack_damage: float = None,
        attack_delay: float = None,
        defense_amount: float = None,
        projectile_amount: int = None,
        projectile_spread: int = None,
        projectile_speed: float = None,
        movement_speed: float = None,
        angle: int = None,
        position: list[int] = None,
        shape: str = None,
        color: str = None,
        size: int = None,
        score: int = None,
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
        self.score = score


class Player(Ship):
    def __init__(self, position: list[float]):
        super().__init__(
            is_player = True,
            health_point = 100,
            attack_damage = 10,
            attack_delay = 0.5,
            defense_amount = 0,
            projectile_amount = 1,
            projectile_spread = 10,
            projectile_speed = 200,
            movement_speed = 100,
            position = position,
            shape = "triangle",
            color = "blue",
            size = 20,
        )


class Basic_Enemy(Ship):
    def __init__(self, position: list[float]) -> None:
        super().__init__(
            is_enemy = True,
            health_point = 10,
            attack_damage = 10,
            movement_speed = 90,
            position = position,
            shape = "circle",
            color = "red",
            size = 15,
            score = 10,
        )


class Elite_Enemy(Ship):
    def __init__(self, position: list[float]):
        super().__init__(
            is_enemy = True,
            health_point = 25,
            attack_damage = 20,
            movement_speed = 75,
            position = position,
            shape = "circle",
            color = "orange",
            size = 25,
            score = 25,
        )


class Boss_Enemy(Ship):
    def __init__(self, position: list[float]):
        super().__init__(
            is_enemy = True,
            health_point = 100,
            attack_damage = 60,
            movement_speed = 60,
            position = position,
            shape = "circle",
            color = "purple",
            size = 50,
            score = 100
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
