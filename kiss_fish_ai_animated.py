import math
import pygame as pg
from random import random, randint, uniform, choice, choices
from spritesheet_reader import get_frames
from fish_properties import fish_properties
from pprint import pprint

# TODO: make different fish types (and maybe colours) have different properties
# ie. physics, state changes, wander steering params

vec = pg.math.Vector2

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

BACKGROUND_COLOUR = "black"
BOUNCE_MARGIN = 100  # for handling walls

NUM_FISH = 10

SOME_COLOURS = {
    "beige": (245, 245, 220, 255),
    "blue": (0, 0, 255, 255),
    "brown": (165, 42, 42, 255),
    "coral": (255, 127, 80, 255),
    "cyan": (0, 255, 255, 255),
    "gold": (255, 215, 0, 255),
    "green": (0, 128, 0, 255),
    "indigo": (75, 0, 130, 255),
    "ivory": (255, 255, 240, 255),
    "khaki": (240, 230, 140, 255),
    "lavender": (230, 230, 250, 255),
    "lightgray": (150, 150, 150, 255),
    "lightyellow": (255, 255, 224, 255),
    "lime": (0, 255, 0, 255),
    "magenta": (255, 0, 255, 255),
    "maroon": (128, 0, 0, 255),
    "navy": (0, 0, 128, 255),
    "olive": (128, 128, 0, 255),
    "orange": (255, 195, 77, 255),
    "pink": (255, 100, 203, 255),
    "plum": (221, 160, 221, 255),
    "purple": (156, 39, 176, 255),
    "red": (255, 0, 0, 255),
    "salmon": (250, 128, 114, 255),
    "silver": (192, 192, 192, 255),
    "teal": (0, 128, 128, 255),
    "turquoise": (64, 224, 208, 255),
    "violet": (238, 130, 238, 255),
    "wheat": (245, 222, 179, 255),
    "white": (255, 255, 255, 255),
    "yellow": (255, 255, 0, 255),
}


COLOURS = list(SOME_COLOURS.values())


def lerp(a, b, f):
    return a + (b - a) * f


def clamp_angle_to_horizontal(v, max_angle_deg):
    angle = math.degrees(math.atan2(abs(v.y), abs(v.x)))
    if angle <= max_angle_deg:
        return v
    return vec(
        v.x, math.copysign(abs(v.x) * math.tan(math.radians(max_angle_deg)), v.y)
    )


class Bubble(pg.sprite.Sprite):
    ...


class Fish(pg.sprite.Sprite):
    DEFAULT_PARAMS = {
        # animation
        "hover_frame_update_interval": 50,  # ms
        "swim_dart_frame_update_distance": 5,  # pix
        # physics
        "max_force": 0.4,
        "min_speed_hover": 6,
        "min_speed_swim": 30,
        "min_speed_dart": 120,
        "max_speed_hover": 15,
        "max_speed_swim": 60,
        "max_speed_dart":240,
        "max_angle_with_horizontal": 10,  # degrees
        # state changes
        "min_state_duration": 2000,
        "max_state_duration": 10000,
        "acceleration_duration": 2000,
        "prob_swim": 0.45,
        "prob_hover": 0.45,
        "prob_dart": 0.1,
        # wander steering params
        "rand_target_time": 200,
        "wander_ring_distance": 400,
        "wander_ring_radius": 50,
    }

    def __init__(self, screen, sprite_group, frames, **kwargs):
        self.screen = screen
        self.groups = sprite_group
        pg.sprite.Sprite.__init__(self, self.groups)
        self.frames = frames
        params = self.DEFAULT_PARAMS.copy()
        filtered_params = {k: v for k, v in kwargs.items() if v is not None}
        params.update(filtered_params)
        self.__dict__.update(params)
        self.pos = vec(randint(0, SCREEN_WIDTH), randint(0, SCREEN_HEIGHT))
        self.state = "swim"
        self.min_speed = {"hover": self.min_speed_hover, "swim": self.min_speed_swim, "dart": self.min_speed_dart}
        self.max_speed = {"hover": self.max_speed_hover, "swim": self.max_speed_swim, "dart": self.max_speed_dart}
        self.vel = vec(
            uniform(self.min_speed[self.state], self.max_speed[self.state]), 0
        ).rotate(uniform(0, 360))
        if self.vel.x >= 0:
            self.image = next(self.frames[self.state]["right"])
        else:
            self.image = next(self.frames[self.state]["left"])
        self.rect = self.image.get_rect()
        self.acc = vec(0, 0)
        # self.rect.topleft = self.pos  # TODO this might need to be center?
        self.rect.center = self.pos
        self.last_update = 0
        self.target = vec(randint(0, SCREEN_WIDTH), randint(0, SCREEN_HEIGHT))
        self.duration_of_current_state = randint(
            int(self.min_state_duration), int(self.max_state_duration)
        )
        now = pg.time.get_ticks()
        self.time_of_last_state_change = now
        self.last_hover_frame_update = now
        self.transitioning = False
        self.distance = 0  # total distance travelled
        print("\nIn Fish init:")
        pprint(self.__dict__)


    def seek(self, target):
        self.desired = (target - self.pos).normalize() * self.max_speed[
            self.state
        ]  # for vector plotting only
        steer = self.desired - self.vel
        if steer.length() > self.max_force:
            steer.scale_to_length(self.max_force)
        return steer

    def wander(self):
        now = pg.time.get_ticks()
        if now - self.last_update > self.rand_target_time:
            self.last_update = now
            future = self.pos + self.vel.normalize() * self.wander_ring_distance
            self.target = future + vec(self.wander_ring_radius, 0).rotate(
                uniform(0, 360)
            )
        return self.seek(self.target)

    def handle_walls(self, method="turn"):
        if method == "wrap":
            hw = 0.5 * self.rect.w
            hh = 0.5 * self.rect.h
            if self.pos.x < -hw:
                self.pos.x = SCREEN_WIDTH + hw
            elif self.pos.x > SCREEN_WIDTH + hw:
                self.pos.x = -hw
            if self.pos.y < -hh:
                self.pos.y = SCREEN_HEIGHT + hh
            elif self.pos.y > SCREEN_HEIGHT + hh:
                self.pos.y = -hh
        elif method == "turn":
            if not (-BOUNCE_MARGIN <= self.pos.x <= SCREEN_WIDTH + BOUNCE_MARGIN):
                self.vel.x = -self.vel.x
                if not (-BOUNCE_MARGIN <= self.pos.y <= SCREEN_HEIGHT + BOUNCE_MARGIN):
                    self.vel.y = -self.vel.y

    def update(self, dt):
        """ dt is frame time step in seconds """
        now = pg.time.get_ticks()
        if (
            not self.transitioning
            and now - self.time_of_last_state_change > self.duration_of_current_state
        ):
            # print("changing state...")
            self.duration_of_current_state = randint(
                int(self.min_state_duration), int(self.max_state_duration)
            )
            self.time_of_last_state_change = now
            if self.state == "dart":
                self.state = "swim"
            else:
                self.state = choices(
                    ("swim", "hover", "dart"),
                    weights=(self.prob_swim, self.prob_hover, self.prob_dart),
                )[0]
            if self.state == "dart":
                self.duration_of_current_state *= 0.4  # darts are shorter duration
            self.old_speed = self.vel.length()
            self.new_speed = uniform(
                self.min_speed[self.state], self.max_speed[self.state]
            )
            self.transitioning = True
        self.last_vel = vec(self.vel)
        self.acc = self.wander()
        self.vel += self.acc * dt
        if self.transitioning:
            frac = (now - self.time_of_last_state_change) / self.acceleration_duration
            easing_frac = 3 * frac * frac - 2 * frac * frac * frac
            interp_speed = lerp(self.old_speed, self.new_speed, easing_frac)
            self.vel.scale_to_length(interp_speed)
            if frac >= 1:
                self.transitioning = False
        speed = self.vel.length()
        self.distance += speed * dt
        if not self.transitioning and speed > self.max_speed[self.state]:
            self.vel.scale_to_length(self.max_speed[self.state])
        if speed < self.min_speed[self.state]:
            self.vel.scale_to_length(self.min_speed[self.state])
        self.vel = clamp_angle_to_horizontal(self.vel, self.max_angle_with_horizontal)
        self.pos += self.vel * dt
        self.handle_walls(method="wrap")
        if (
            self.state == "hover"
            and now - self.last_hover_frame_update > self.hover_frame_update_interval
        ):
            self.last_hover_frame_update = now
            if self.vel.x >= 0:
                self.image = next(self.frames["hover"]["right"])
            else:
                self.image = next(self.frames["hover"]["left"])
        elif (
            self.state in ["swim", "dart"]
            and self.distance > self.swim_dart_frame_update_distance
        ):
            self.distance = 0
            if self.vel.x >= 0:
                self.image = next(self.frames[self.state]["right"])
            else:
                self.image = next(self.frames[self.state]["left"])
        # self.rect.topleft = self.pos  # TODO this might need to be center?
        self.rect.center = self.pos

    def draw_vectors(self):
        # acceleration indicator
        if self.transitioning:
            pg.draw.circle(self.screen, "white", self.pos, 50, 5)
        scale = 50
        # vel
        pg.draw.line(
            self.screen, "green", self.pos, (self.pos + self.vel.normalize() * scale), 5
        )
        # desired
        pg.draw.line(self.screen, "red", self.pos, (self.pos + self.desired * scale), 5)
        # target
        center = self.pos + self.vel.normalize() * self.wander_ring_distance
        pg.draw.circle(self.screen, "white", center, self.wander_ring_radius, 1)
        pg.draw.line(self.screen, "cyan", center, self.target, 5)


def main():
    fish_frames = get_frames("FIFTH")
    pg.init()
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pg.time.Clock()
    all_sprites = pg.sprite.Group()
    for _ in range(NUM_FISH):
        # key = str(i) + "_" + colour + "_" + state + "_" + direction
        fish_type = str(randint(1, 6))
        fish_props_ranges = fish_properties[fish_type]
        fish_props = {}
        for k, v in fish_props_ranges.items():
            if isinstance(v, (list, tuple)) and len(v) == 2:
                fish_props[k] = uniform(v[0], v[1])
            else:
                fish_props[k] = v
        # pprint(fish_props)
        fish_colour = choice(("blue", "green", "orange", "pink", "red", "yellow"))
        hover_left_key = fish_type + "_" + fish_colour + "_" + "idle" + "_" + "left"
        hover_right_key = fish_type + "_" + fish_colour + "_" + "idle" + "_" + "right"
        swim_left_key = fish_type + "_" + fish_colour + "_" + "swim" + "_" + "left"
        swim_right_key = fish_type + "_" + fish_colour + "_" + "swim" + "_" + "right"
        dart_left_key = fish_type + "_" + fish_colour + "_" + "swim" + "_" + "left"
        dart_right_key = fish_type + "_" + fish_colour + "_" + "swim" + "_" + "right"
        frames = {
            "hover": {
                "left": fish_frames[hover_left_key],
                "right": fish_frames[hover_right_key],
            },
            "swim": {
                "left": fish_frames[swim_left_key],
                "right": fish_frames[swim_right_key],
            },
            "dart": {
                "left": fish_frames[dart_left_key],
                "right": fish_frames[dart_right_key],
            },
        }
        Fish(screen, all_sprites, frames, **fish_props)
    paused = False
    show_vectors = False
    running = True
    while running:
        dt = clock.tick(FPS)  # ms
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
                if event.key == pg.K_SPACE:
                    paused = not paused
                if event.key == pg.K_v:
                    show_vectors = not show_vectors

        screen.fill(BACKGROUND_COLOUR)
        if not paused:
            all_sprites.update(0.001 * dt)
        pg.display.set_caption(f"{clock.get_fps():.0f}")
        all_sprites.draw(screen)
        if show_vectors:
            for sprite in all_sprites:
                sprite.draw_vectors()
        pg.display.flip()
    pg.quit()


if __name__ == "__main__":
    main()
