import os
from itertools import cycle
import pygame as pg


pg.init()

COLOURS = ("blue", "green", "orange", "pink", "red", "yellow")
COLOUR_INDEX = {col: i for i, col in enumerate(COLOURS)}
NUM_COLOURS = len(COLOURS)

STATES = ("idle", "swim", "swim-chomp")
STATE_INDEX = {state: i for i, state in enumerate(STATES)}
NUM_STATES = len(STATES)

DIRECTIONS = ("left", "right")
DIRECTION_INDEX = {dirn: i for i, dirn in enumerate(DIRECTIONS)}
NUM_DIRECTIONS = len(DIRECTIONS)

NUM_FRAMES = (20, 16, 16)
NUM_COLS = max(NUM_FRAMES)

SHEET_INFO = {}
SHEET_INFO["FULL"] = {
    "DIR": "full size",
    "STEM": "fish_spritesheet_full_size_0",
    "FRAME_SIZE": (444, 283),
    "IMAGE_SIZES": {
        "1": (376, 283),
        "2": (295, 253),
        "3": (396, 269),
        "4": (216, 149),
        "5": (444, 281),
        "6": (318, 280),
    },
}
SHEET_INFO["HALF"] = {
    "DIR": "half size",
    "STEM": "fish_spritesheet_half_size_0",
    "FRAME_SIZE": (222, 141),
    "IMAGE_SIZES": {
        "1": (188, 141),
        "2": (147, 126),
        "3": (198, 134),
        "4": (108, 74),
        "5": (222, 140),
        "6": (159, 140),
    },
}
SHEET_INFO["THIRD"] = {
    "DIR": "third size",
    "STEM": "fish_spritesheet_third_size_0",
    "FRAME_SIZE": (146, 93),
    "IMAGE_SIZES": {
        "1": (124, 93),
        "2": (97, 83),
        "3": (130, 88),
        "4": (71, 49),
        "5": (146, 92),
        "6": (104, 92),
    },
}
SHEET_INFO["QUARTER"] = {
    "DIR": "quarter size",
    "STEM": "fish_spritesheet_quarter_size_0",
    "FRAME_SIZE": (111, 70),
    "IMAGE_SIZES": {
        "1": (94, 70),
        "2": (73, 63),
        "3": (99, 67),
        "4": (54, 37),
        "5": (111, 70),
        "6": (79, 70),
    },
}
SHEET_INFO["FIFTH"] = {
    "DIR": "fifth size",
    "STEM": "fish_spritesheet_fifth_size_0",
    "FRAME_SIZE": (88, 56),
    "IMAGE_SIZES": {
        "1": (75, 56),
        "2": (59, 50),
        "3": (79, 53),
        "4": (43, 29),
        "5": (88, 56),
        "6": (63, 56),
    },
}
SHEET_INFO["EIGHTH"] = {
    "DIR": "eighth size",
    "STEM": "fish_spritesheet_eighth_size_0",
    "FRAME_SIZE": (55, 35),
    "IMAGE_SIZES": {
        "1": (47, 35),
        "2": (36, 31),
        "3": (49, 33),
        "4": (27, 18),
        "5": (55, 35),
        "6": (39, 35),
    },
}


def get_spritesheet_row(colour, state, direction):
    return (
        NUM_STATES * NUM_DIRECTIONS * COLOUR_INDEX[colour]
        + (NUM_STATES - 1) * STATE_INDEX[state]
        + (NUM_DIRECTIONS - 1) * DIRECTION_INDEX[direction]
    )


def get_frames(size, verbose=False):
    """
    Returns dictionary of cycled animation frames for requested size.
    Dictionary keys are:
        key = fish_num + "_" + colour + "_" + state + "_" + direction
    NB: constructing a key in this way is faster than nested dictionaries which
    is important since the animation frames are accessed at the frame rate for
    potentially large numbers of fish.

    """

    size = size.upper()
    directory = SHEET_INFO[size]["DIR"]
    stem = SHEET_INFO[size]["STEM"]
    image_sizes = SHEET_INFO[size]["IMAGE_SIZES"]
    frame_width, frame_height = SHEET_INFO[size]["FRAME_SIZE"]

    fish_frames = {}

    for i in range(1, 7):
        fish_num = str(i)
        path = os.path.join("fish spritesheets", directory, stem + fish_num + ".png")
        if verbose:
            print(f"Fish type {i}: loading spritesheet {path}")
        spritesheet = pg.image.load(path)
        for colour in COLOURS:
            for state, n in zip(STATES, NUM_FRAMES):
                # fishtypes 1, 4 and 5 have no swim chomp animation frames
                if i in [1, 4, 5] and state == "swim-chomp":
                    continue
                for direction in DIRECTIONS:
                    frames = []
                    for j in range(n):
                        key = fish_num + "_" + colour + "_" + state + "_" + direction
                        frame = pg.Surface(image_sizes[fish_num], pg.SRCALPHA)
                        x, y = (
                            j * frame_width,
                            get_spritesheet_row(colour, state, direction)
                            * frame_height,
                        )
                        # print(x,y)
                        frame.blit(spritesheet, (-x, -y))
                        frames.append(frame)
                    fish_frames[key] = cycle(frames)
    return fish_frames


def main():
    width, height = 900, 600
    fps = 60
    screen = pg.display.set_mode((width, height))
    clock = pg.time.Clock()
    # check animations
    size = "fifth"
    fish_frames = get_frames(size)
    duration = 500
    blit_topleft = 100, 100
    for i in range(1, 7):
        for colour in COLOURS:
            for state in STATES:
                for direction in DIRECTIONS:
                    key = str(i) + "_" + colour + "_" + state + "_" + direction
                    print(key)
                    start_time = pg.time.get_ticks()
                    while pg.time.get_ticks() - start_time < duration:
                        for event in pg.event.get():
                            if event.type == pg.QUIT:
                                return
                            if event.type == pg.KEYDOWN:
                                if event.key == pg.K_ESCAPE:
                                    return
                        clock.tick(fps)
                        screen.fill("black")
                        try:
                            frame = next(fish_frames[key])
                        except:
                            print("not found")
                            break
                        screen.blit(frame, blit_topleft)
                        pg.display.flip()


if __name__ == "__main__":
    main()
    pg.quit()
