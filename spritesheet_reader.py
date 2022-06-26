import os
from itertools import cycle
import pygame as pg

# Read from consolidates spritesheets.
# Then run all animations to check proper loading.

WIDTH, HEIGHT = 900, 600
FPS = 60

COLOURS = ("blue", "green", "orange", "pink", "red", "yellow")
COLOUR_INDEX = {col: i for i, col in enumerate(COLOURS)}
NUM_COLOURS = len(COLOURS)

STATES = ("idle", "swim", "swim-chomp")
STATE_INDEX = {state: i for i, state in enumerate(STATES)}
NUM_STATES = len(STATES)

DIRECTIONS = ("left", "right")
DIRECTION_INDEX = {dirn: i for i, dirn in enumerate(DIRECTIONS)}
NUM_DIRECTIONS = len(DIRECTIONS)

NUM_FRAMES = (20, 16, 20)
NUM_COLS = max(NUM_FRAMES)

# # full size
# DIR = os.path.join("fish spritesheets", "full size")
# SPRITESHEET_FNAME_STEM = "fish_spritesheet_full_size_0"
# FRAME_W, FRAME_H = 444, 283
# IMAGE_SIZES = {"1": (376, 283), "2": (295, 253), "3": (396, 269), "4": (216, 149), "5": (444, 281), "6": (318, 280)}

# half size
DIR = os.path.join("fish spritesheets", "half size")
SPRITESHEET_FNAME_STEM = "fish_spritesheet_half_size_0"
FRAME_W, FRAME_H = 222, 141
# frame size is constant, but image sizes within frame vary (but toplefts aligned)
IMAGE_SIZES = {
    "1": (188, 141),
    "2": (147, 126),
    "3": (198, 134),
    "4": (108, 74),
    "5": (222, 140),
    "6": (159, 140),
}

# # third size
# DIR = os.path.join("fish spritesheets", "third size")
# SPRITESHEET_FNAME_STEM = "fish_spritesheet_third_size_0"
# FRAME_W, FRAME_H = 146, 93
# # frame size is constant, but image sizes within frame vary (but toplefts aligned)
# IMAGE_SIZES = {"1": (124, 93), "2": (97, 83), "3": (130, 88), "4": (71, 49), "5": (146, 92), "6": (104, 92)}

# # quarter size
# DIR = os.path.join("fish spritesheets", "quarter size")
# SPRITESHEET_FNAME_STEM = "fish_spritesheet_quarter_size_0"
# FRAME_W, FRAME_H = 111, 70
# # frame size is constant, but image sizes within frame vary (but toplefts aligned)
# IMAGE_SIZES = {"1": (94, 70), "2": (73, 63), "3": (99, 67), "4": (54, 37), "5": (111, 70), "6": (79, 70)}

# # fifth size
# DIR = os.path.join("fish spritesheets", "fifth size")
# SPRITESHEET_FNAME_STEM = "fish_spritesheet_fifth_size_0"
# FRAME_W, FRAME_H = 88, 56
# # frame size is constant, but image sizes within frame vary (but toplefts aligned)
# IMAGE_SIZES = {
#     "1": (75, 56),
#     "2": (59, 50),
#     "3": (79, 53),
#     "4": (43, 29),
#     "5": (88, 56),
#     "6": (63, 56),
# }


# # eighth size
# DIR = os.path.join("fish spritesheets", "eighth size")
# SPRITESHEET_FNAME_STEM = "fish_spritesheet_eighth_size_0"
# FRAME_W, FRAME_H = 55, 35
# # frame size is constant, but image sizes within frame vary (but toplefts aligned)
# IMAGE_SIZES = {"1": (47, 35), "2": (36, 31), "3": (49, 33), "4": (27, 18), "5": (55, 35), "6": (39, 35)}


def get_spritesheet_row(colour, state, direction):
    return (
        NUM_STATES * NUM_DIRECTIONS * COLOUR_INDEX[colour]
        + (NUM_STATES - 1) * STATE_INDEX[state]
        + (NUM_DIRECTIONS - 1) * DIRECTION_INDEX[direction]
    )


pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
clock = pg.time.Clock()

# read in all sprite sheets

fish_frames = {}
for i in range(1, 7):
    print(i)
    fish_num = str(i)
    spritesheet = pg.image.load(
        os.path.join(DIR, SPRITESHEET_FNAME_STEM + fish_num + ".png")
    )
    for colour in COLOURS:
        for state, n in zip(STATES, NUM_FRAMES):
            # fishtypes 1, 4 and 5 have no swim chomp animation frames
            if i in [1, 4, 5] and state == "swim-chomp":
                continue
            for direction in DIRECTIONS:
                frames = []
                for j in range(n):
                    key = fish_num + "_" + colour + "_" + state + "_" + direction
                    frame = pg.Surface(IMAGE_SIZES[fish_num], pg.SRCALPHA)
                    x, y = (
                        j * FRAME_W,
                        get_spritesheet_row(colour, state, direction) * FRAME_H,
                    )
                    # print(x,y)
                    frame.blit(spritesheet, (-x, -y))
                    frames.append(frame)
                fish_frames[key] = cycle(frames)


# check animations
duration = 400
blit_topleft = 100, 100
for i in range(1, 7):
    for colour in COLOURS:
        for state in STATES:
            for direction in DIRECTIONS:
                key = str(i) + "_" + colour + "_" + state + "_" + direction
                print(key)
                start_time = pg.time.get_ticks()
                while pg.time.get_ticks() - start_time < duration:
                    clock.tick(FPS)
                    screen.fill("black")
                    try:
                        frame = next(fish_frames[key])
                    except:
                        print("not found")
                        break
                    screen.blit(frame, blit_topleft)
                    pg.display.flip()

pg.quit()
