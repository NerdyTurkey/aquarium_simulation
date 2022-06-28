import math
import pygame as pg
from random import random, randint, uniform, choice, choices
from buffer_smooth import BufferSmooth

vec = pg.math.Vector2

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

BACKGROUND_COLOUR = "black"
BOUNCE_MARGIN = 100  # for handling walls

NUM_FISH = 1
DS = 100

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
        # appearance
        "body_width": None,
        "body_height": None,
        "colour": None,
        # physics
        "max_force": 0.4,
        "min_speed": {"hover": 6, "swim": 30, "dart": 120},
        "max_speed": {"hover": 15, "swim": 60, "dart": 240},
        "max_angle_with_horizontal": 20,  # degrees
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

    def __init__(self, screen, sprite_group, **kwargs):
        self.groups = sprite_group
        pg.sprite.Sprite.__init__(self, self.groups)
        self.screen = screen
        params = self.DEFAULT_PARAMS.copy()
        filtered_params = {k: v for k, v in kwargs.items() if v is not None}
        params.update(filtered_params)
        self.__dict__.update(params)
        if self.body_width is None:
            self.body_width = randint(30, 50)
        if self.body_height is None:
            self.body_height = uniform(0.2, 0.8) * self.body_width
        if self.colour is None:
            self.colour = choice(COLOURS)
        self.create_images()
        self.pos = vec(randint(0, SCREEN_WIDTH), randint(0, SCREEN_HEIGHT))
        self.state = "swim"
        self.vel = vec(
            uniform(self.min_speed[self.state], self.max_speed[self.state]), 0
        ).rotate(uniform(0, 360))
        self.image = self.image_right
        self.rect = self.image.get_rect()
        self.acc = vec(0, 0)
        self.rect.center = self.pos
        self.last_update = 0
        self.target = vec(randint(0, SCREEN_WIDTH), randint(0, SCREEN_HEIGHT))
        self.duration_of_current_state = randint(
            self.min_state_duration, self.max_state_duration
        )
        self.time_of_last_state_change = pg.time.get_ticks()
        self.transitioning = False
        self.s = 0  # total distance travelled

    def create_images(self):
        body = pg.Surface((self.body_width, self.body_height), pg.SRCALPHA)
        body_rect = body.get_rect()
        pg.draw.ellipse(body, self.colour, body_rect)
        eye_pos = vec(body_rect.midright) - vec(0.2 * self.body_width, 0)
        tail_width = uniform(0.2, 0.5) * self.body_width
        tail_height = self.body_height
        tail = pg.Surface((tail_width, tail_height), pg.SRCALPHA)
        tail_poly_pts = ((0, 0), (tail_width, 0.5 * tail_height), (0, tail_height))
        pg.draw.circle(body, "black", eye_pos, 0.1 * self.body_width)
        pg.draw.line(
            body,
            "black",
            (body_rect.right, body_rect.centery + 5),
            (body_rect.right - 0.2 * self.body_width, body_rect.centery + 5),
            1,
        )
        pg.draw.polygon(tail, self.colour, tail_poly_pts)
        self.image_right = pg.Surface(
            (self.body_width + tail_width, self.body_height + tail_height), pg.SRCALPHA
        )
        self.image_right.blit(tail, (0, 0))
        self.image_right.blit(body, (tail_width, 0))
        self.image_left = pg.transform.flip(self.image_right, True, False)

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
                self.min_state_duration, self.max_state_duration
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
        self.s += speed * dt
        if self.s >= DS:
            print(f"{now} travelled {DS}")
            self.s = 0
        if not self.transitioning and speed > self.max_speed[self.state]:
            self.vel.scale_to_length(self.max_speed[self.state])
        if speed < self.min_speed[self.state]:
            self.vel.scale_to_length(self.min_speed[self.state])
        self.vel = clamp_angle_to_horizontal(self.vel, self.max_angle_with_horizontal)
        self.pos += self.vel * dt
        self.handle_walls(method="wrap")
        if self.vel.x >= 0:
            self.image = self.image_right
        else:
            self.image = self.image_left
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
    pg.init()
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pg.time.Clock()
    all_sprites = pg.sprite.Group()
    for _ in range(NUM_FISH):
        Fish(screen, all_sprites)
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
            if event.key == pg.K_m:
                    Fish(screen, all_sprites)

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
