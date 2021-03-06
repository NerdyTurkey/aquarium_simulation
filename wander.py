import math
import pygame as pg
from random import random, randint, uniform, choice, choices
from buffer_smooth import BufferSmooth

vec = pg.math.Vector2

WIDTH = 1200
HEIGHT = 800
FPS = 60

NUM_FISH = 1

col_dict_short = {
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

ALL_COLOURS = list(col_dict_short.values())

WHITE = 255, 255, 255
BLACK = 0, 0, 0
RED = 255, 0, 0
GREEN = 0, 255, 0
BLUE = 0, 0, 255
CYAN = 0, 255, 255
YELLOW = 255, 255, 0
DARKGRAY = 40, 40, 40

BOUNCE_MARGIN = 100
# To avoid problem with Vector2 normalize and scale to length vcrashing with very small vectors
MIN_LENGTH = 1e-5


# Fish properties; will be different for different types of fish

MIN_SPEED = {"hover": 0.1, "swim": 0.5, "dart": 2}
MAX_SPEED = {"hover": 0.4, "swim": 1, "dart": 4}
# should these be state-dependent?
MAX_ANGLE_WITH_HORIZONTAL = 10  # degrees
MIN_STATE_DURATION = 2000
MAX_STATE_DURATION = 2000  # 10000
ACCELERATION_DURATION = 2000
PROB_SWIM = 0.45
PROB_HOVER = 0.45
PROB_DART = 0.1
# PROB_TURN = 1
FRICTION = 1
# turning
SMALL_VX = 0.1
TURN_DURATION = 2000
TURN_RATE = math.pi / TURN_DURATION

# angular steering
ANGLE_SMOOTHING_BUFFER_SIZE = 5  # angle of fish is running average of this many frames

# wander steering params
MAX_FORCE = 0.4
RAND_TARGET_TIME = 1000
WANDER_RING_DISTANCE = 400
WANDER_RING_RADIUS = 50

# seek with approach params
SEEK_RADIUS = 400  # only approach target when within this distance of it
APPROACH_RADIUS = 50  # decelerate towards target at this distance from it

# evade params
EVADE_RADIUS = 400

# steering weights
STEER_WEIGHT_WANDER = 1
STEER_WEIGHT_SEEK = 0
STEER_WEIGHT_EVADE = 0


def blitRotate(surf, image, pos, origin_pos, angle):
    """
    https://stackoverflow.com/questions/4183208/how-do-i-rotate-an-image-around-its-center-using-pygame
    """
    # offset from pivot to center
    image_rect = image.get_rect(
        topleft=(pos[0] - origin_pos[0], pos[1] - origin_pos[1])
    )
    offset_center_to_pivot = vec(pos) - image_rect.center

    # rotated offset from pivot to center
    rotated_offset = offset_center_to_pivot.rotate(-angle)

    # rotated image center
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)

    # get a rotated image
    rotated_image = pg.transform.rotate(image, angle)
    rotated_image_rect = rotated_image.get_rect(center=rotated_image_center)

    # rotate and blit the image
    surf.blit(rotated_image, rotated_image_rect)

    # draw rectangle around the image
    pg.draw.rect(
        surf, (255, 0, 0), (*rotated_image_rect.topleft, *rotated_image.get_size()), 2
    )


def rotate_about_centre(surf, rect, angle):
    """
    Pass in a surface `surf` and its rect `rect` and the rotated surface and its new rect are returned.
    Rotation is about the centre of rect.
    `angle`is the rotation angle in degrees, >0 --> clockwise
    """
    rotated_surf = pg.transform.rotate(surf, angle)
    return rotated_surf, rotated_surf.get_rect(center=rect.center)


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
    pass


class Fish(pg.sprite.Sprite):
    def __init__(self, screen, sprite_group):
        self.groups = sprite_group
        pg.sprite.Sprite.__init__(self, self.groups)
        body_width = 100  # randint(30, 50)
        body_height = 50  # uniform(0.2, 0.8) * body_width
        body = pg.Surface((body_width, body_height), pg.SRCALPHA)
        body_rect = body.get_rect()
        colour = "cyan"  # choice(COLOURS)
        pg.draw.ellipse(body, colour, body_rect)
        eye_pos = vec(body_rect.midright) - vec(0.2 * body_width, 0)
        tail_width = uniform(0.2, 0.5) * body_width
        tail_height = body_height
        tail = pg.Surface((tail_width, tail_height), pg.SRCALPHA)
        tail_poly_pts = ((0, 0), (tail_width, 0.5 * tail_height), (0, tail_height))
        pg.draw.circle(body, BLACK, eye_pos, 0.1 * body_width)
        pg.draw.line(
            body,
            BLACK,
            (body_rect.right, body_rect.centery + 5),
            (body_rect.right - 0.2 * body_width, body_rect.centery + 5),
            1,
        )
        pg.draw.polygon(tail, colour, tail_poly_pts)
        self.image_right = pg.Surface(
            (body_width + tail_width, body_height + tail_height), pg.SRCALPHA
        )
        self.image_right.blit(tail, (0, 0))
        self.image_right.blit(body, (tail_width, 0))
        self.image_left = pg.transform.flip(self.image_right, True, False)
        self.screen = screen
        self.state = "swim"
        self.pos = vec(randint(0, WIDTH), randint(0, HEIGHT))
        self.vel = vec(uniform(MIN_SPEED[self.state], MAX_SPEED[self.state]), 0).rotate(
            uniform(0, 360)
        )
        self.image = self.image_right
        self.rect = self.image.get_rect()
        self.acc = vec(0, 0)
        self.rect.center = self.pos
        self.last_update = 0
        self.target = vec(randint(0, WIDTH), randint(0, HEIGHT))
        self.duration_of_current_state = randint(MIN_STATE_DURATION, MAX_STATE_DURATION)
        self.time_of_last_state_change = pg.time.get_ticks()
        self.transitioning = False
        self.buffer_smooth = BufferSmooth(buffer_size=ANGLE_SMOOTHING_BUFFER_SIZE)
        self.turning = False
        self.turn_has_flipped = False

    def evade(self, target, ahead_only=True):
        steer = vec(0, 0)
        if ahead_only and not self.is_ahead(target):
            return steer
        dist = self.pos - target
        if EVADE_RADIUS > dist.length() > MIN_LENGTH:
            desired = dist.normalize() * MAX_SPEED[self.state]
            steer = desired - self.vel
            if steer.length() > MAX_FORCE:
                steer.scale_to_length(MAX_FORCE)
        print(steer)
        return steer

    def seek(self, target):
        self.desired = (target - self.pos).normalize() * MAX_SPEED[
            self.state
        ]  # for vector plotting only
        steer = self.desired - self.vel
        if steer.length() > MAX_FORCE:
            steer.scale_to_length(MAX_FORCE)
        return steer

    def wander(self):
        now = pg.time.get_ticks()
        if now - self.last_update > RAND_TARGET_TIME:
            self.last_update = now
            future = self.pos + self.vel.normalize() * WANDER_RING_DISTANCE
            self.target = future + vec(WANDER_RING_RADIUS, 0).rotate(uniform(0, 360))
        return self.seek(self.target)

    def is_ahead(self, target):
        dx = target.x - self.pos.x
        if dx > 0 and self.vel.x > 0:
            return True
        if dx < 0 and self.vel.x < 0:
            return True
        return False

    def seek_with_approach(self, target, ahead_only=True):
        """
        Decelerates towards target
        """
        steer = vec(0, 0)
        if ahead_only and not self.is_ahead(target):
            return steer
        dist = target - self.pos
        if SEEK_RADIUS > dist.length() > MIN_LENGTH:
            desired = dist.normalize() * MAX_SPEED[self.state]
            if dist.length() < APPROACH_RADIUS:
                desired *= dist.length() / APPROACH_RADIUS
            steer = desired - self.vel
            if steer.length() > MAX_FORCE:
                steer.scale_to_length(MAX_FORCE)
        return steer

    def handle_walls(self, method="turn"):
        if method == "wrap":
            hw = 0.5 * self.rect.w
            hh = 0.5 * self.rect.h
            if self.pos.x < -hw:
                self.pos.x = WIDTH + hw
            elif self.pos.x > WIDTH + hw:
                self.pos.x = -hw
            if self.pos.y < -hh:
                self.pos.y = HEIGHT + hh
            elif self.pos.y > HEIGHT + hh:
                self.pos.y = -hh
        elif method == "turn":
            if not (-BOUNCE_MARGIN <= self.pos.x <= WIDTH + BOUNCE_MARGIN):
                self.vel.x = -self.vel.x
                if not (-BOUNCE_MARGIN <= self.pos.y <= HEIGHT + BOUNCE_MARGIN):
                    self.vel.y = -self.vel.y

    def update(self):
        now = pg.time.get_ticks()
        if (
            not self.transitioning
            and now - self.time_of_last_state_change > self.duration_of_current_state
        ):
            print("changing state...")
            self.duration_of_current_state = randint(
                MIN_STATE_DURATION, MAX_STATE_DURATION
            )
            self.time_of_last_state_change = now
            if self.state == "dart":
                self.state = "swim"
            # elif self.state == "hover" and random() <= PROB_TURN:
            #     print("change to turning")
            #     self.vel.x = 0
            #     self.turning = True
            #     self.turn_start_time = pg.time.get_ticks()
            #     self.image_save = self.image.copy()
            #     self.is_flipped = False
            #     return
            else:
                self.state = choices(
                    ("swim", "hover", "dart"),
                    weights=(PROB_SWIM, PROB_HOVER, PROB_DART),
                )[0]
            if self.state == "dart":
                self.duration_of_current_state *= 0.4  # darts are shorter duration
            self.old_speed = self.vel.length()
            self.new_speed = uniform(MIN_SPEED[self.state], MAX_SPEED[self.state])
            self.transitioning = True
        # ----
        mp = vec(pg.mouse.get_pos())
        self.acc = (
            STEER_WEIGHT_WANDER * self.wander()
            + STEER_WEIGHT_SEEK * self.seek_with_approach(mp)
            + STEER_WEIGHT_EVADE * self.evade(mp, ahead_only=False)
            - vec(FRICTION * self.vel.x ** 2, 0)
        )
        # ---
        self.last_vel = vec(self.vel)
        self.vel += self.acc
        if self.transitioning:
            frac = (now - self.time_of_last_state_change) / ACCELERATION_DURATION
            easing_frac = 3 * frac * frac - 2 * frac * frac * frac
            # interp_speed = lerp(self.old_speed, self.new_speed, frac) # linear easing
            interp_speed = lerp(self.old_speed, self.new_speed, easing_frac)
            self.vel.scale_to_length(interp_speed)
            if frac >= 1:
                self.transitioning = False
        speed = self.vel.length()
        if not self.transitioning and speed > MAX_SPEED[self.state]:
            self.vel.scale_to_length(MAX_SPEED[self.state])
        if speed < MIN_SPEED[self.state]:
            self.vel.scale_to_length(MIN_SPEED[self.state])
        print(f"{self.vel.x:.2f}")
        self.vel = clamp_angle_to_horizontal(self.vel, MAX_ANGLE_WITH_HORIZONTAL)
        # if (self.vel.x > SMALL_VX and self.last_vel.x < SMALL_VX) or (self.vel.x < SMALL_VX and self.last_vel.x > SMALL_VX):
        #     print("\nChanged direction!")
        #     self.turning = True
        #     self.turn_start_time = pg.time.get_ticks()
        self.pos += self.vel
        self.handle_walls(method="wrap")
        if self.vel.x >= 0:
            self.image = self.image_right
            self.dirn = "right"
        else:
            # self.image = pg.transform.flip(self.image_right, False, True)
            self.image = self.image_left
            self.dirn = "left"
        # angle = math.degrees(math.atan2(-self.vel.y, self.vel.x))
        # angle = self.buffer_smooth.smooth(angle)
        # # print(f"{angle:.0f}")
        # self.image, self.rect = rotate_about_centre(self.image, self.rect, angle)
        # if self.turning:
        #     elapsed = now - self.turn_start_time
        #     if elapsed < TURN_DURATION:
        #         if elapsed >= 0.5 * TURN_DURATION and not self.turn_has_flipped:
        #             # 2nd half of turn animation
        #             # flip image horizontally
        #             self.image = pg.transform.flip(self.image, True, False)
        #             self.turn_has_flipped = True
        #         self.image = pg.transform.smoothscale(self.image, (
        #         int(abs(self.rect.w * math.cos(TURN_RATE * elapsed))), self.rect.h))
        #     else:
        #         # turn finished
        #         self.turning = False
        #         self.state = "swim"
        #         self.dirn = "left" if self.dirn == "right" else "right"
        #         # self.vel.x *= 20 # kick to prevent immediately turning again
        self.rect.center = self.pos

    def draw_vectors(self):
        # acceleration indicator
        # if self.transitioning:
        #     pg.draw.circle(self.screen, WHITE, self.pos, 50, 5)
        scale = 50
        # vel
        pg.draw.line(
            self.screen, GREEN, self.pos, (self.pos + self.vel.normalize() * scale), 5
        )
        # desired
        pg.draw.line(self.screen, RED, self.pos, (self.pos + self.desired * scale), 5)
        # target
        center = self.pos + self.vel.normalize() * WANDER_RING_DISTANCE
        pg.draw.circle(
            self.screen,
            WHITE,
            center,
            WANDER_RING_RADIUS,
            1
            # self.screen, WHITE, (int(center.x), int(center.y)), wander_ring_radius, 1
        )
        pg.draw.line(self.screen, CYAN, center, self.target, 5)


def main():
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    all_sprites = pg.sprite.Group()
    for _ in range(NUM_FISH):
        Fish(screen, all_sprites)
    paused = False
    show_vectors = False
    running = True
    while running:
        clock.tick(FPS)
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
                if event.key == pg.K_m:
                    Fish(screen, all_sprites)

        screen.fill(DARKGRAY)
        if not paused:
            all_sprites.update()
        pg.display.set_caption(f"{clock.get_fps():.0f}")
        all_sprites.draw(screen)
        if show_vectors:
            for sprite in all_sprites:
                sprite.draw_vectors()
        pg.display.flip()
    pg.quit()


if __name__ == "__main__":
    main()
