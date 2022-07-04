import math
import pygame as pg
from random import random, randint, uniform, choice, choices
from spritesheet_reader import get_frames
from fish_properties import fish_properties
from pprint import pprint

vec = pg.math.Vector2

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

BACKGROUND_COLOUR = "black"
BOUNCE_MARGIN = 100  # for handling walls


MAX_NUM_FISH = 50
# TODO make these type dependent
MIN_MAX_NUM_PAIRS = {
    "1": (1, 4),
    "2": (1, 4),
    "3": (1, 4),
    "4": (1, 4),
    "5": (1, 4),
    "6": (1, 4),
}

MAX_SELECTED_FISH = 2

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


def filter_by_occurrences(alist, occurrences=1):
    """
    Returns alist keeping only elements that appear <= occurrences
    """
    return [i for i in alist if alist.count(i) <= occurrences]


def lerp(a, b, f):
    return a + (b - a) * f


def clamp_angle_to_horizontal(v, max_angle_deg):
    angle = math.degrees(math.atan2(abs(v.y), abs(v.x)))
    if angle <= max_angle_deg:
        return v
    return vec(
        v.x, math.copysign(abs(v.x) * math.tan(math.radians(max_angle_deg)), v.y)
    )


def get_outline_image(img, colour="white", linewidth=1, sf=1.4):
    mask = pg.mask.from_surface(img)
    outline = mask.outline()
    dw, dh = 2 * linewidth, 2 * linewidth
    outline = [(dw // 2 + p[0], dh // 2 + p[1]) for p in outline]
    outline_img = pg.Surface(img.get_rect().inflate(dw, dh).size, pg.SRCALPHA)
    pg.draw.polygon(outline_img, colour, outline, linewidth)
    return pg.transform.rotozoom(outline_img, 0, sf)


class Bubble(pg.sprite.Sprite):
    DEFAULT_PARAMS = {
        "radius_min_max": (3, 5),
        "size_scale_factor": 1.0,
        "colour": "white",
        "linewidth":1,
        "speed_scale_factor":1.0,
    }

    def __init__(self, sprite_group, pos, **kwargs):
        pg.sprite.Sprite.__init__(self, sprite_group)
        self.pos = vec(pos)
        params = self.DEFAULT_PARAMS.copy()
        filtered_params = {k: v for k, v in kwargs.items() if v is not None}
        params.update(filtered_params)
        self.__dict__.update(params)
        self.radius = randint(*self.radius_min_max)
        self.vel = vec(0, -self.size_scale_factor * 20 * self.radius**0.5)
        self.image = pg.Surface((2*self.radius, 2*self.radius), pg.SRCALPHA)
        pg.draw.circle(self.image, self.colour, (self.radius, self.radius), self.radius, self.linewidth)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, dt):
        self.pos += self.vel * dt
        if self.pos.y < -self.radius:
            self.kill()
        else:
            self.rect.center = self.pos


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
        "max_speed_dart": 240,
        "max_angle_with_horizontal": 10,  # degrees
        # state changes
        "min_state_duration": 2000,
        "max_state_duration": 10000,
        "acceleration_duration": 2000,
        "prob_swim": 0.45,
        "prob_hover": 0.45,
        "prob_dart": 0.1,
        # modifiers
        "prob_chomp": 0.2,
        # wander steering params
        "rand_target_time": 200,
        "wander_ring_distance": 400,
        "wander_ring_radius": 50,
    }

    def __init__(self, screen, sprite_group, frames, id, **kwargs):
        self.screen = screen
        pg.sprite.Sprite.__init__(self, sprite_group)
        self.frames = frames
        self.id = id
        params = self.DEFAULT_PARAMS.copy()
        filtered_params = {k: v for k, v in kwargs.items() if v is not None}
        params.update(filtered_params)
        self.__dict__.update(params)
        self.pos = vec(randint(0, SCREEN_WIDTH), randint(0, SCREEN_HEIGHT))
        self.state = "swim"
        self.modifier = None
        self.min_speed = {
            "hover": self.min_speed_hover,
            "swim": self.min_speed_swim,
            "dart": self.min_speed_dart,
        }
        self.max_speed = {
            "hover": self.max_speed_hover,
            "swim": self.max_speed_swim,
            "dart": self.max_speed_dart,
        }
        self.vel = vec(
            uniform(self.min_speed[self.state], self.max_speed[self.state]), 0
        ).rotate(uniform(0, 360))
        image_left = next(self.frames[self.state]["left"])
        image_right = next(self.frames[self.state]["right"])
        # self.outline_image_left = get_outline_image(image_left)
        # self.outline_image_right = get_outline_image(image_right)
        if self.vel.x >= 0:
            self.image = image_right
        else:
            self.image = image_left
        self.rect = self.image.get_rect()  # same size for left and right
        self.acc = vec(0, 0)
        self.rect.center = self.pos
        self.last_update = 0
        self.target = vec(randint(0, SCREEN_WIDTH), randint(0, SCREEN_HEIGHT))
        self.duration_of_current_state = randint(
            int(self.min_state_duration), int(self.max_state_duration)
        )
        now = pg.time.get_ticks()
        self.time_of_last_state_change = now
        self.time_of_last_bubble = now
        self.bubble = False
        self.bubble_interval = randint(2000, 5000)
        self.last_hover_frame_update = now
        self.transitioning = False
        self.distance = 0  # total distance travelled
        self.selected = False
        self.selection_ring_radius = self.rect.w // 2 + 10
        # self.show_outline = False
        # print("\nIn Fish init:")
        # pprint(self.__dict__)

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
        # bubbles
        if now - self.time_of_last_bubble > self.bubble_interval:
            self.bubble = True
            self.time_of_last_bubble = now
            self.bubble_interval = randint(2000, 5000)
        if (
            not self.transitioning
            and now - self.time_of_last_state_change > self.duration_of_current_state
        ):
            # print("changing state...")
            # modifiers change behaviour of a state (they are not a state in their own right)
            # currently only have a chomp modifier (mouth opening and closing)
            self.modifier = choices(
                (None, "chomp"), weights=(self.prob_chomp, 1 - self.prob_chomp)
            )[0]
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
                # confusingly, not all fish types have chomp frames,
                # so we need to check if it has_chomp before checking modifier flag
                if self.has_chomp and self.modifier == "chomp":
                    self.image = next(self.frames["chomp"]["right"])
                else:
                    self.image = next(self.frames["hover"]["right"])
            else:
                if self.has_chomp and self.modifier == "chomp":
                    self.image = next(self.frames["chomp"]["left"])
                else:
                    self.image = next(self.frames["hover"]["left"])
        elif (
            self.state in ["swim", "dart"]
            and self.distance > self.swim_dart_frame_update_distance
        ):
            self.distance = 0
            if self.vel.x >= 0:
                if self.has_chomp and self.modifier == "chomp":
                    self.image = next(self.frames["chomp"]["right"])
                else:
                    self.image = next(self.frames[self.state]["right"])
            else:
                if self.has_chomp and self.modifier == "chomp":
                    self.image = next(self.frames["chomp"]["left"])
                else:
                    self.image = next(self.frames[self.state]["left"])
        # for collision detection using pg.sprite.collide_circle
        # 0.2 found by trial and error
        self.radius = 0.2 * sum(self.image.get_size())
        self.rect.center = self.pos


def main():
    pg.init()
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pg.time.Clock()

    pg.mouse.set_visible(False)
    fish_sprites = pg.sprite.Group()
    bubble_sprites = pg.sprite.Group()
    all_sprites = pg.sprite.Group()


    cursor = pg.sprite.Sprite()
    cursor.radius = 5
    cursor.image = pg.Surface((2 * cursor.radius, 2 * cursor.radius), pg.SRCALPHA)
    pg.draw.circle(
        cursor.image, "white", (cursor.radius, cursor.radius), cursor.radius, 1
    )
    cursor.rect = cursor.image.get_rect()

    fish_frames = get_frames("FIFTH")
    num_fish = 0
    while True:
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
        hover_left_dict_key = fish_type + "_" + fish_colour + "_" + "idle" + "_" + "left"
        hover_right_dict_key = fish_type + "_" + fish_colour + "_" + "idle" + "_" + "right"
        swim_left_dict_key = fish_type + "_" + fish_colour + "_" + "swim" + "_" + "left"
        swim_right_dict_key = fish_type + "_" + fish_colour + "_" + "swim" + "_" + "right"
        dart_left_dict_key = fish_type + "_" + fish_colour + "_" + "swim" + "_" + "left"
        dart_right_dict_key = fish_type + "_" + fish_colour + "_" + "swim" + "_" + "right"
        chomp_left_dict_key = (
            fish_type + "_" + fish_colour + "_" + "swim-chomp" + "_" + "left"
        )
        chomp_right_dict_key = (
            fish_type + "_" + fish_colour + "_" + "swim-chomp" + "_" + "right"
        )
        frames = {
            "hover": {
                "left": fish_frames[hover_left_dict_key],
                "right": fish_frames[hover_right_dict_key],
            },
            "swim": {
                "left": fish_frames[swim_left_dict_key],
                "right": fish_frames[swim_right_dict_key],
            },
            "dart": {
                "left": fish_frames[dart_left_dict_key],
                "right": fish_frames[dart_right_dict_key],
            },
        }
        # not all fish types have chomp frames
        if fish_props["has_chomp"]:
            frames["chomp"] = {
                "left": fish_frames[chomp_left_dict_key],
                "right": fish_frames[chomp_right_dict_key],
            }
        id = fish_type + "_" + fish_colour
        num_pairs = randint(*MIN_MAX_NUM_PAIRS[fish_type])
        for i in range(num_pairs):
            num_fish += 2
            Fish(screen, fish_sprites, frames, id, **fish_props)
            Fish(screen, fish_sprites, frames, id, **fish_props)
        if num_fish >= MAX_NUM_FISH:
            break


    print(f"{num_fish=}")

    paused = False
    show_hitboxes = False
    show_mouths = False
    running = True
    num_fish_selected = 0
    selected_fishes = {}
    while running:
        cursor.rect.center = pg.mouse.get_pos()
        dt = clock.tick(FPS)  # ms
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEBUTTONUP:
                hit_fishes = pg.sprite.spritecollide(
                    cursor, fish_sprites, False, pg.sprite.collide_circle
                )
                for fish in hit_fishes:
                    id = fish.id
                    if fish.selected:
                        selected_fishes[id].remove(fish)
                        num_fish_selected -= 1
                        fish.selected = False
                    elif num_fish_selected < MAX_SELECTED_FISH:
                        if id not in selected_fishes:
                            selected_fishes[id] = []
                        selected_fishes[id].append(fish)
                        num_fish_selected += 1
                        fish.selected = True
                    # sprite.show_outline = not sprite.show_outline
                    # sprite.kill()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
                elif event.key == pg.K_SPACE:
                    paused = not paused
                elif event.key == pg.K_h:
                    show_hitboxes = not show_hitboxes
                elif event.key == pg.K_m:
                    show_mouths = not show_mouths

        # remove matched fish
        selected_fishes_copy = selected_fishes.copy()
        for id, fishes in selected_fishes.items():
            if len(fishes) >= 2:
                num_fish_selected -= len(fishes)
                for fish in fishes:
                    fish.kill()
                selected_fishes_copy[id] = []
        selected_fishes = selected_fishes_copy.copy()

        screen.fill(BACKGROUND_COLOUR)

        for fish in fish_sprites:
            if fish.bubble:
                if fish.vel.x >= 0:
                    bubble_pos = fish.rect.midright
                else:
                    bubble_pos = fish.rect.midleft
                Bubble(bubble_sprites, bubble_pos)
                fish.bubble = False
        all_sprites.add(fish_sprites, bubble_sprites)
        #  update
        if not paused:
            all_sprites.update(0.001 * dt)
        pg.display.set_caption(f"{clock.get_fps():.0f}")
        if len(fish_sprites) == 0:
            running = False
        # draw
        all_sprites.draw(screen)
        for fish in fish_sprites:
            if fish.selected:
                pg.draw.circle(
                    screen, "yellow", fish.rect.center, fish.selection_ring_radius, 5
                )
                # if sprite.vel.x >= 0:
                #     outline_image = sprite.outline_image_right
                # else:
                #     outline_image = sprite.outline_image_left
                # outline_rect = outline_image.get_rect(center=sprite.rect.center)
                # screen.blit(outline_image, outline_rect)
            if show_hitboxes:
                pg.draw.circle(screen, "white", fish.rect.center, fish.radius, 1)
            if show_mouths:
                pg.draw.circle(screen, "white", fish.rect.midright, 2)
                pg.draw.circle(screen, "white", fish.rect.midleft, 2)
        screen.blit(cursor.image, cursor.rect)
        pg.display.flip()
    pg.quit()


if __name__ == "__main__":
    main()
