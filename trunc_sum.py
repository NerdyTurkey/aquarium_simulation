import pygame as pg
from time import time

vec = pg.math.Vector2
TINY = 1e-8


def trunc_sum(v1, v2, d):
    """
    Adds as much of v2 to v1 as needed to get length of v1 to d and returns the scaled v2
    i.e. return w * v2
    st. |v1 + w * v2 | = d
    where w > 0
    """
    v1, v2 = vec(v1), vec(v2)
    d = abs(d)
    delta = v1.length() - d
    if delta > TINY:  # can't use zero due to rounding errors
        raise ValueError("length of v1 is already > d")
    if 0 <= delta <= TINY:
        return vec(0, 0)
    x1, y1 = v1
    x2, y2 = v2
    # Need to solve  (x1 + w*x2)**2 + (y1 + w*y2)**2 = d**2 for w.
    # Get quadratic: a*w**2 + b*w + c = 0, with...
    a = x2 * x2 + y2 * y2
    b = 2 * (x1 * x2 + y1 * y2)
    c = x1 * x1 + y1 * y1 - d * d
    det = (b * b - 4 * a * c) ** 0.5
    wpos = 0.5 * (-b + det) / a
    if wpos > 0:
        return wpos * v2
    wneg = 0.5 * (-b - det) / a
    return wneg * v2


def main():
    # demo use
    #
    # 3,4,5 triangle
    v1 = vec(0, 3)
    v2 = vec(1, 0)
    d = 5
    scaled_v2 = trunc_sum(v1, v2, d)
    v_sum = v1 + scaled_v2
    # expect v_sum = [4,3], length = 5
    print(v_sum, v_sum.length())


if __name__ == "__main__":
    main()
    pg.quit()
