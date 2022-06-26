from random import randrange, uniform
import pygame as pg
from steer_combiner import combined_steer
from angle_clamper import clamp_angle_to_horizontal

vec = pg.math.Vector2

BOUNCE_MARGIN = 20

BEHAVIOUR_COLOURS = {"wander": "blue", "seek": "green", "evade": "red"}
SF = 200


class Agent(pg.sprite.Sprite):
    def __init__(self, screen, sprite_group):
        self.groups = sprite_group
        pg.sprite.Sprite.__init__(self, self.groups)
        self.screen = screen
        self.screen_width, self.screen_height = pg.display.get_surface().get_size()
        # constants
        self.width, self.height = 10, 10
        self.friction_coeff = 0.1
        # could depend on state
        self.mass = 0.5  # mass might change after eating
        self.max_angle_with_horizontal = 45  # degrees
        self.max_force = 0.5
        self.max_speed = 2
        self.wander_ring_radius = 50
        self.wander_ring_distance = 100
        self.seek_detect_radius = 100
        self.seek_approach_radius = 20
        self.evade_detect_radius = 55
        self.wander_weight = 1
        self.seek_weight = 2
        self.evade_weight = 4
        self.behaviour_priority_order = ["evade", "wander", "seek"]
        # physics
        self.pos = vec(randrange(0, self.screen_width), randrange(self.screen_height))
        self.vel = vec(uniform(0, self.max_speed), 0).rotate(uniform(0, 360))
        self.acc = vec(0, 0)

        self.image = pg.Surface((self.width, self.height), pg.SRCALPHA)
        self.image.fill("blue")
        self.rect = self.image.get_rect(center=self.pos)

        self.targets = {"seek": {}, "evade": {}}

    def handle_walls(self, method="wrap"):
        if method == "wrap":
            hw = 0.5 * self.rect.w
            hh = 0.5 * self.rect.h
            if self.pos.x < -hw:
                self.pos.x = self.screen_width + hw
            elif self.pos.x > self.screen_width + hw:
                self.pos.x = -hw
            if self.pos.y < -hh:
                self.pos.y = self.screen_height + hh
            elif self.pos.y > self.screen_height + hh:
                self.pos.y = -hh
        elif method == "turn":
            if not (-BOUNCE_MARGIN <= self.pos.x <= self.screen_width + BOUNCE_MARGIN):
                self.vel.x = -self.vel.x
                if not (
                    -BOUNCE_MARGIN <= self.pos.y <= self.screen_height + BOUNCE_MARGIN
                ):
                    self.vel.y = -self.vel.y

    def draw_targets(self):
        for behaviour in ["seek", "evade"]:
            for id, info in self.targets[behaviour].items():
                pg.draw.circle(
                    self.screen,
                    BEHAVIOUR_COLOURS[behaviour],
                    info["pos"],
                    int(5 * info["weight"]),
                )

    def debug(self):
        for behaviour, steer in self.steers:
            pg.draw.line(
                self.screen, BEHAVIOUR_COLOURS[behaviour], self.pos, self.pos + SF * steer, 5
            )
            if behaviour == "seek":
                pg.draw.circle(
                    self.screen, "green", self.pos, self.seek_detect_radius, 1
                )
            elif behaviour == "evade":
                pg.draw.circle(
                    self.screen, "red", self.pos, self.evade_detect_radius, 1
                )

    def add_target(self, kind, id, info):
        if kind in self.targets:
            self.targets[kind][id] = info

    def remove_target(self, kind, id):
        if id in self.targets[kind]:
            del self.targets[kind][id]

    def update_physics(self):
        params = {
            "pos": self.pos,
            "vel": self.vel,
            "max_speed": self.max_speed,
            "max_force": self.max_force,
        }
        priority_ordered_info = []
        for behaviour in self.behaviour_priority_order:
            if behaviour == "wander":
                priority_ordered_info.append(
                    (
                        "wander",
                        {
                            "ring_radius": self.wander_ring_radius,
                            "ring_distance": self.wander_ring_distance,
                            "weight": self.wander_weight,
                        },
                    )
                )
                continue
            for id, info in self.targets[behaviour].items():
                if behaviour == "seek":
                    priority_ordered_info.append(
                        (
                            "seek",
                            {
                                "target_pos": info["pos"],
                                "target_weight": info["weight"],
                                "detect_radius": self.seek_detect_radius,
                                "approach_radius": self.seek_approach_radius,
                                "weight": self.seek_weight,
                            },
                        )
                    )
                elif behaviour == "evade":
                    priority_ordered_info.append(
                        (
                            "evade",
                            {
                                "target_pos": info["pos"],
                                "target_weight": info["weight"],
                                "detect_radius": self.evade_detect_radius,
                                "weight": self.evade_weight,
                            },
                        )
                    )
        total_steer, self.steers = combined_steer(params, priority_ordered_info)
        friction_force = (
                -self.friction_coeff * self.vel.length_squared() * total_steer.normalize()
        )
        force = total_steer + friction_force
        self.acc = force / self.mass
        self.vel += self.acc
        if self.vel.length() > self.max_speed:
            self.vel.scale_to_length(self.max_speed)
        self.vel = clamp_angle_to_horizontal(self.vel, self.max_angle_with_horizontal)
        self.pos += self.vel

    def update_state(self):
        pass

    def update_image(self):
        pass


    def update(self, *args, **kwargs):
        # self.update_state()
        self.update_physics()
        # self.update_image()
        self.handle_walls()
        self.rect.center = self.pos


def main():
    fps = 60
    screen_width, screen_height = 900, 600
    pg.init()
    screen = pg.display.set_mode((screen_width, screen_height))
    clock = pg.time.Clock()
    all_sprites = pg.sprite.Group()
    num_fish = 10
    agents = []
    for _ in range(num_fish):
        agents.append(Agent(screen, all_sprites))
    running = True
    paused = False
    debug = True
    target_counter = 0
    while running:
        clock.tick(fps)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
                if event.key == pg.K_SPACE:
                    paused = not paused
                if event.key == pg.K_d:
                    debug = not debug
                if event.key == pg.K_s:
                    # add seek target
                    for agent in agents:
                        agent.add_target(
                            "seek",
                            "seek" + str(target_counter),
                            {
                                "pos": (
                                    randrange(0, screen_width),
                                    randrange(0, screen_height),
                                ),
                                "weight": uniform(0.5, 10),
                            },
                            )
                    target_counter += 1
                if event.key == pg.K_e:
                    # add evade target
                    for agent in agents:
                        agent.add_target(
                            "evade",
                            "evade" + str(target_counter),
                            {
                                "pos": (
                                    randrange(0, screen_width),
                                    randrange(0, screen_height),
                                ),
                                "weight": 1,
                            },
                            )
                    target_counter += 1
        screen.fill("black")
        if not paused:
            all_sprites.update()
        all_sprites.draw(screen)
        for sprite in all_sprites:
            sprite.draw_targets()
            if debug:
                sprite.debug()
        pg.display.set_caption(f"{clock.get_fps():.0f}")
        pg.display.flip()
    pg.quit()


if __name__ == "__main__":
    main()
