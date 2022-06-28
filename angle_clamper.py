import math
import pygame as pg

vec = pg.math.Vector2


def clamp_angle_to_horizontal(v, max_angle_deg):
    angle = math.degrees(math.atan2(abs(v.y), abs(v.x)))
    if angle <= max_angle_deg:
        return v
    return vec(
        v.x, math.copysign(abs(v.x) * math.tan(math.radians(max_angle_deg)), v.y)
    )
