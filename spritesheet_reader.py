import json
from itertools import cycle
import pygame as pg

WIDTH, HEIGHT = 900, 600
FPS = 60

pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
clock = pg.time.Clock()

spritesheet_info = {}
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
        parts = frame_id.split("_")
        if len(parts) == 6:
            colour = parts[2]
            state = parts[4]
            frame_number = parts[5].split(".")[0][1:]
            key = "0" + str(i) + "_" + colour + "_" + state + "_" + frame_number
        else:
            colour = parts[2]
            state = parts[4]
            extra = parts[5]
            frame_number = parts[6].split(".")[0][1:]
            key = (
                "0"
                + str(i)
                + "_"
                + colour
                + "_"
                + state
                + "_"
                + extra
                + "_"
                + frame_number
            )
        # print(key)
        spritesheet_info[key] = [(x, y), (w, h)]

frames = {}

for key, frame_info in spritesheet_info.items():
    spritesheet = pg.image.load("spritesheet" + key[:2] + ".png")
    (x, y), (w, h) = frame_info
    frame = pg.Surface((w, h), pg.SRCALPHA)
    frame.blit(spritesheet, (-x, -y))
    frames[key] = frame

# ToDo
# sort into dict with keys = fish_number + "_" + colour + "_" + state + ("_" + "chomping"), values = cycle(frames)
# idle has 20 frames
# swim has 16 frames
# swim chomping has 16 frames


# frames_by_type = {}
# for i in range(1, 7):
#     fish_type = "0" + str(i)
#     sprite_sheet = pg.image.load("spritesheet" + fish_type + ".png")
#     frames_by_colour = {}
#     for colour, info in frames_toplefts.items():
#         frames_by_state = {}
#         for state, toplefts in info.items():
#             frames = []
#             for x, y in toplefts:
#                 frame = pg.Surface((FRAME_W, FRAME_H), pg.SRCALPHA)
#                 frame.blit(sprite_sheet, (-x, -y))
#                 frames.append(frame)
#             frames_by_state[state] = cycle(frames)
#         frames_by_colour[colour] = frames_by_state
#     frames_by_type[fish_type] = frames_by_colour
#
#
# fish_type = "01"
# colour = "green"
# state = "idle"
# running = True
# while running:
#     clock.tick(FPS)
#     screen.fill("black")
#     screen.blit(next(frames_by_type[fish_type][colour][state]), (100, 100))
#     pg.display.flip()
