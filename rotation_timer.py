import pygame as pg
from random import uniform
from time import time

W, H = 100, 100
NUM_ROTATIONS = 10000

pg.init()
screen = pg.display.set_mode((900, 600))

surf = pg.Surface((W, H), pg.SRCALPHA)

t0 = time()
for i in range(NUM_ROTATIONS):
    rot_surf = pg.transform.rotate(surf, uniform(0, 360))
dt = time() - t0


print(f"time per rotation is {1000*dt/NUM_ROTATIONS:.2f} ms")
pg.quit()
