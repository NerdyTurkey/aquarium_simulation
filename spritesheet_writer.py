import json
from itertools import cycle
import os
import pygame as pg

# Read from raw sprite sheets and make consolidated spritesheets (1 for each fish type).
# Then run all animations to check proper functioning.

WIDTH, HEIGHT = 900, 600
FPS = 60

# make full size spritesheet
SCALE_FACTOR = 1  # scaling factor from raw sprite sheet to output sprite sheet
WRITE_DIR = os.path.join("fish spritesheets", "full size")
WRITE_FNAME_STEM = "fish_spritesheet_full_size_0"

# # make half size spritesheet
# SCALE_FACTOR = 0.5  # scaling factor from raw sprite sheet to output sprite sheet
# WRITE_DIR = os.path.join("fish spritesheets", "half size")
# WRITE_FNAME_STEM = "fish_spritesheet_half_size_0"

pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
clock = pg.time.Clock()

spritesheet_info = {}
max_frame_width, max_frame_height = 0, 0
for i in range(1, 7):
    fname = "spritesheet0" + str(i) + ".json"
    with open(fname, "r") as f:
        data = json.load(f)
    info = data["frames"]
    for frame_id, frame_info in info.items():
        x = frame_info["frame"]["x"]
        y = frame_info["frame"]["y"]
        w = frame_info["frame"]["w"]
        h = frame_info["frame"]["h"]
        max_frame_width = max(w, max_frame_width)
        max_frame_height = max(h, max_frame_height)
        parts = frame_id.split("_")
        colour = parts[2].lower()
        state = parts[4].lower()
        if len(parts) == 6:
            frame_number = int(parts[5].split(".")[0][1:])
            key = str(i) + "_" + colour + "_" + state + "_" + str(frame_number)
        else:
            frame_number = int(parts[6].split(".")[0][1:])
            key = str(i) + "_" + colour + "_" + "swim-chomp" + "_" + str(frame_number)
        # print(key)
        spritesheet_info[key] = [(x, y), (w, h)]

fish_frames = {}
COLOURS = ("blue", "green", "orange", "pink", "red", "yellow")
STATES = ("idle", "swim", "swim-chomp")
NUM_FRAMES = (20, 16, 20)
DIRECTIONS = ("left", "right")
NUM_COLS = max(NUM_FRAMES)
NUM_ROWS = len(COLOURS) * len(STATES) * len(DIRECTIONS)

output_frame_width, output_frame_height = (
    int(SCALE_FACTOR * max_frame_width),
    int(SCALE_FACTOR * max_frame_height),
)

# print(output_frame_width, output_frame_height)
# print(num_cols * output_frame_width, num_rows * output_frame_height)

for i in range(1, 7):
    print(i)
    output_spritesheet = pg.Surface(
        (NUM_COLS * output_frame_width, NUM_ROWS * output_frame_height), pg.SRCALPHA
    )
    fish_num = str(i)
    input_spritesheet = pg.image.load("spritesheet0" + fish_num + ".png")
    row = 0
    for colour in COLOURS:
        for state, n in zip(STATES, NUM_FRAMES):
            for direction in DIRECTIONS:
                frames = []
                for j in range(NUM_COLS):
                    # to access spritesheet_info dict
                    key1 = fish_num + "_" + colour + "_" + state + "_" + str(j)
                    # to access fish_frames dict
                    key2 = fish_num + "_" + colour + "_" + state + "_" + direction
                    # print(key1, end="")
                    try:
                        (x, y), (w, h) = spritesheet_info[key1]
                    except KeyError:
                        # print("...error")
                        continue
                    # print("...ok")
                    frame = pg.Surface((w, h), pg.SRCALPHA)
                    frame.blit(input_spritesheet, (-x, -y))
                    frame = pg.transform.rotozoom(frame, 0, SCALE_FACTOR)
                    if direction == "right":
                        frame = pg.transform.flip(frame, True, False)
                    # print(key2, frame.get_size())
                    output_spritesheet.blit(
                        frame, (j * output_frame_width, row * output_frame_height)
                    )
                    frames.append(frame)
                row += 1
                fish_frames[key2] = cycle(frames)
    pg.image.save(os.path.join(WRITE_DIR, WRITE_FNAME_STEM + fish_num + ".png"))


duration = 500
blit_topleft = 100, 100

for i in range(1, 7):
    for colour in COLOURS:
        for state in STATES:
            for direction in DIRECTIONS:
                key = str(i) + "_" + colour + "_" + state + "_" + direction
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
