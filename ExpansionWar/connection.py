import math

import pygame

import config
from rocket import Rocket


class Connection:
    def __init__(self, planet, other_planet):
        self.planet = planet
        self.other_planet = other_planet

        self.last_ticks = 0
        self.line_width = 10

        self.rockets = []

    def rocket_finished(self, rocket):
        self.rockets.remove(rocket)

    def draw(self, base_x, base_y, surface):
        current_ticks = pygame.time.get_ticks()

        if self.planet.value > 0 and current_ticks - self.last_ticks > self.planet.send_rocket_every:
            self.last_ticks = current_ticks
            self.rockets.append(Rocket(self, self.planet, self.other_planet))
            self.planet.value -= 1

        pygame.draw.line(surface, config.CONNECTION_COLOR,
                         (base_x + self.planet.center_x, base_y + self.planet.center_y),
                         (base_x + self.other_planet.center_x, base_y + self.other_planet.center_y),
                         self.line_width)

        for rocket in self.rockets:
            rocket.draw(base_x, base_y, surface)

    def is_clicked(self, base_x, base_y, point):
        px, py = point
        x1, y1 = (base_x + self.planet.center_x, base_y + self.planet.center_y)
        x2, y2 = (base_x + self.other_planet.center_x, base_y + self.other_planet.center_y)

        if x1 == x2 and y1 == y2:
            return math.hypot(px - x1, py - y1) <= self.line_width

        # Line segment vector
        dx = x2 - x1
        dy = y2 - y1

        # Project point onto line segment, clamp between 0 and 1
        t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))

        # Find the closest point on the segment
        nearest_x = x1 + t * dx
        nearest_y = y1 + t * dy

        # Distance from click to closest point
        dist = math.hypot(px - nearest_x, py - nearest_y)

        return dist <= self.line_width