"""Geometry on positions [x, y] and angles in degrees (0 = right, 90 = down)."""
import math


def point_at(start, angle, distance):
    """Position distance pixels away from start in the direction of angle."""
    return [start[0] + math.cos(math.radians(angle)) * distance,
            start[1] + math.sin(math.radians(angle)) * distance]


def move(thing, angle, distance):
    """Moves a ship or projectile."""
    thing.position = point_at(thing.position, angle, distance)


def angle_towards(start, target):
    """Angle from position start to position target."""
    return math.degrees(math.atan2(target[1] - start[1], target[0] - start[0]))


def collides(first_position, first_size, second_position, second_size):
    return math.dist(first_position, second_position) < first_size + second_size
