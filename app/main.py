from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Tuple

from PIL import Image


def solve_quadratic_equation(a, b, c):
    """Quadratic equation solver.
    Solve function of form f(x) = ax^2 + bx + c
    From: https://github.com/adamlwgriffiths/Pyrr/blob/master/pyrr/utils.py

    :param float a: Quadratic part of equation.
    :param float b: Linear part of equation.
    :param float c: Static part of equation.
    :rtype: list
    :return: List contains either two elements for two solutions, one element for one solution, or is empty if
        no solution for the quadratic equation exists.
    """
    delta = b * b - 4 * a * c
    if delta > 0:
        # Two solutions
        # See https://www.scratchapixel.com/lessons/3d-basic-rendering/minimal-ray-tracer-rendering-simple-shapes/ray-sphere-intersection
        # Why not use simple form:
        # s1 = (-b + math.sqrt(delta)) / (2 * a)
        # s2 = (-b - math.sqrt(delta)) / (2 * a)
        q = -0.5 * (b + math.sqrt(delta)) if b > 0 else -0.5 * (b - math.sqrt(delta))
        s1 = q / a
        s2 = c / q
        return [s1, s2]
    elif delta == 0:
        # One solution
        return [-b / (2 * a)]
    else:
        # No solution exists
        return list()


@dataclass
class Vector:
    x: int = 0
    y: int = 0
    z: int = 0

    def __add__(self, vec: Vector) -> Vector:
        return Vector(self.x + vec.x, self.y + vec.y, self.z + vec.z)

    def __sub__(self, vec: Vector) -> Vector:
        return Vector(self.x - vec.x, self.y - vec.y, self.z - vec.z)

    def __mul__(self, k: int) -> Vector:
        return Vector(self.x * k, self.y * k, self.z * k)

    def normalize(self) -> Vector:
        size = self.size()
        return Vector(self.x / size, self.y / size, self.z / size)

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z

    def dot(self, vec: Vector):
        return self.x * vec.x + self.y * vec.y + self.z * vec.z

    def cross(self, vec: Vector) -> Vector:
        return Vector(self.y * vec.z - self.z * vec.y, self.z * vec.x - self.x * vec.z, self.x * vec.y - self.y * vec.x)

    def size(self):
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)


Position = Vector


@dataclass
class Color:
    red: int = 0
    green: int = 0
    blue: int = 0

    def to_rgb(self) -> Tuple[int, int, int]:
        return (int(self.red), int(self.green), int(self.blue))

    def __mul__(self, x: float) -> Color:
        return Color(self.red * x, self.green * x, self.blue * x)

    def __add__(self, color: Color) -> Color:
        return Color(self.red + color.red, self.green + color.green, self.blue + color.blue)

    def __truediv__(self, x: float) -> Color:
        return Color(self.red / x, self.green / x, self.blue / x)


@dataclass
class Object:
    color: Color
    albedo: float


@dataclass
class Sphere(Object):
    pos: Position
    radius: int

    def intersect(self, origin: Position, direction: Vector) -> Hit:

        a = 1
        b = 2 * direction.dot(origin - self.pos)
        c = (origin - self.pos).dot(origin - self.pos) - self.radius * self.radius

        t_list = solve_quadratic_equation(a, b, c)

        if not t_list:
            return

        min_t = min(t_list)

        if min_t >= 0:
            pos = origin + direction * min_t
            return Hit(pos=pos, normal=pos - self.pos, obj=self)


@dataclass
class Plane(Object):
    pos: Position
    normal: Vector

    def intersect(self, origin: Position, direction: Vector) -> Hit:
        dir_dot_normal = direction.dot(self.normal)

        if dir_dot_normal == 0.0:
            return

        t = (self.pos.dot(self.normal) - origin.dot(self.normal)) / dir_dot_normal

        return Hit(pos=origin + direction * t, normal=self.normal * (1 if dir_dot_normal > 0 else -1), obj=self)


@dataclass
class Camera:
    pos: Position
    height: int
    width: int
    fov: float


@dataclass
class Light:
    pos: Position
    intensity: int


@dataclass
class Hit:
    pos: Position
    normal: Vector
    obj: Object


def intersect(origin: Position, direction: Vector, scene: List[Object]) -> Hit:
    closest_hit, distance_to_closest_hit = None, None

    for obj in scene:
        hit = obj.intersect(origin, direction)
        if not hit:
            continue

        distance = (hit.pos - origin).size()
        if closest_hit is None or distance < distance_to_closest_hit:
            distance_to_closest_hit = distance
            closest_hit = hit

    if closest_hit:
        return closest_hit


def main():
    img = Image.new("RGB", [500, 500], 255)
    data = img.load()

    camera = Camera(pos=Position(0, 0, 0), height=500, width=500, fov=90)
    scene = [
        Sphere(pos=Position(250, 250, 150), radius=100, color=Color(0x26, 0x60, 0x53), albedo=0.3),
        Sphere(pos=Position(400, 250, 120), radius=100, color=Color(0x2A, 0x9D, 0x8F), albedo=0.8),
        Sphere(pos=Position(300, 150, 200), radius=60, color=Color(0xE9, 0xC4, 0x6A), albedo=0.4),
        Sphere(pos=Position(250, 250, 130), radius=50, color=Color(0xF4, 0xA2, 0x61), albedo=0.3),
        # Sphere(pos=Position(250, 250, 300), radius=50, color=Color(0x26, 0x60, 0x53), albedo=0.5),
        # Plane(pos=Position(0, 400, 0), normal=Vector(0, 0, -1), color=Color(0x00, 0x80, 0xff), albedo=0.2),
        # Sphere(pos=Position(100, 100, 150), radius=20, color=Color(0x2A, 0x9D, 0x8F), albedo=0.5),
    ]
    background = Color()

    lights = [Light(pos=Position(-150, -150, -150), intensity=0.2)]

    pov_z = 250 / math.tan(math.radians(camera.fov / 2))

    print(pov_z)

    for x in range(img.size[0]):
        if not x % (img.size[0] / 10):
            print(f"\rGeneration {x * 100 / img.size[0]}%", flush=True)
        for y in range(img.size[1]):

            origin = camera.pos + Vector(x, y)
            hit = intersect(origin, (origin - Position(250, 250, -pov_z)).normalize(), scene)

            if not hit:
                data[x, y] = background.to_rgb()
                continue

            color = Color()

            scene_without_obj = [scene_obj for scene_obj in scene if scene_obj != hit.obj]

            for light in lights:
                obj_before_light = intersect(hit.pos, (light.pos - hit.pos).normalize(), scene_without_obj)
                if obj_before_light:
                    continue

                color += hit.obj.color * (
                    hit.obj.albedo
                    / math.pi
                    * light.intensity
                    * max(0, hit.normal.dot((light.pos - hit.pos).normalize()))
                )

            color += hit.obj.color * (
                hit.obj.albedo / math.pi * 0.03 * max(0, hit.normal.dot((origin - hit.pos).normalize()))
            )

            data[x, y] = color.to_rgb()

    print("Saving image.png")
    img.save("image.png")
    print("Done")
