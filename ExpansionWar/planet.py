import random
import pygame
import config
import math
import logging

logger = logging.getLogger(__name__)

class Planet:
    def __init__(self, x, y, color, radius = config.PLANET_RADIUS, show_value = True, base_texture = None, noise_texture = None, light_texture = None):
        self.x = x
        self.y = y
        self.color = color

        self.radius = radius
        self.selected = False
        self.apply_black_surface = False
        self.center_x = self.x + self.radius
        self.center_y = self.y + self.radius

        self.target_value = None

        self.value = 1
        self.value_start = 0
        self.show_value = show_value

        self.add_value_every = 1 * 1000
        self.send_rocket_every = 1 * 1000
        self.rocket_upgrade = 1

        if base_texture is None:
            self.base_texture_name = random.choice([key for key in config.planet_assets if "sphere" in key])
        else:
            self.base_texture_name = base_texture
        self.base_texture = config.planet_assets[self.base_texture_name]

        if noise_texture is None:
            self.noise_texture_name = random.choice([key for key in config.planet_assets if "noise" in key])
        else:
            self.noise_texture_name = noise_texture
        self.noise_texture = config.planet_assets[self.noise_texture_name]

        if light_texture is None:
            self.light_texture_name = random.choice([key for key in config.planet_assets if "light" in key])
        else:
            self.light_texture_name = light_texture
        self.light_texture = config.planet_assets[self.light_texture_name]

        self.base_texture = pygame.transform.scale(self.base_texture, (radius * 2, radius * 2))
        self.noise_texture = pygame.transform.scale(self.noise_texture, (radius * 2, radius * 2))
        self.light_texture = pygame.transform.scale(self.light_texture, (radius * 2, radius * 2))

        self.font = pygame.font.Font(config.assets[config.FONT_NAME], 35)

        self.create_planet_surface()

        # Satellite attributes:
        self.satellite_upgrade = 0
        scaled_satellite = pygame.image.load(config.assets['satellite.png'])
        scaled_satellite = pygame.transform.scale(scaled_satellite, (scaled_satellite.get_width()/6, scaled_satellite.get_height()/6))
        self.satellite_base_texture = pygame.transform.rotate(scaled_satellite, -90)
        self.satellite_orbit_speed = 0.01

    def create_planet_surface(self):
        planet_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)

        planet_surface.blit(self.base_texture, (0, 0))
        planet_surface.blit(self.light_texture, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        planet_surface.blit(self.noise_texture, (0, 0))

        colored_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        colored_surface.fill(self.color)

        self.selected_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        self.selected_surface.fill((255, 255, 255, 127))
        self.selected_surface.blit(self.base_texture, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        self.black_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        self.black_surface.fill((0, 0, 0, 127))
        self.black_surface.blit(self.base_texture, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        planet_surface.blit(colored_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        self.surface = planet_surface

    def draw(self, screen, base_x, base_y):
        current_ticks = pygame.time.get_ticks()
        if self.color != config.NO_OWNER_COLOR:
            if current_ticks - self.value_start > self.add_value_every:
                self.value_start = current_ticks
                self.value += 1 + self.satellite_upgrade

        # Render orbiting satellites if upgrade is applied
        if self.satellite_upgrade > 0:
            planet_center_x = base_x + self.center_x
            planet_center_y = base_y + self.center_y
            orbit_radius = self.radius + (self.satellite_base_texture.get_width() // 2) + 5
            orbit_offset = (current_ticks * self.satellite_orbit_speed) % 360

            for i in range(self.satellite_upgrade):
                base_angle_degrees = (360 / self.satellite_upgrade) * i
                orbit_angle_degrees = base_angle_degrees + orbit_offset
                orbit_angle_radians = math.radians(orbit_angle_degrees)
                sat_x = planet_center_x + orbit_radius * math.cos(orbit_angle_radians)
                sat_y = planet_center_y + orbit_radius * math.sin(orbit_angle_radians)
                facing_angle = math.degrees(math.atan2(sat_y - planet_center_y, planet_center_x - sat_x))
                rotated_satellite = pygame.transform.rotate(self.satellite_base_texture, facing_angle)
                rotated_rect = rotated_satellite.get_rect(center=(sat_x, sat_y))

                if current_ticks - self.value_start < 100:
                    pygame.draw.line(screen, config.SATELLITE_RAY_COLOR, (sat_x, sat_y),
                                     (planet_center_x, planet_center_y), 5)

                screen.blit(rotated_satellite, rotated_rect)

        screen.blit(self.surface, (base_x + self.x, base_y + self.y))
        if self.selected:
            screen.blit(self.selected_surface, (base_x + self.x, base_y + self.y))

        if self.apply_black_surface:
            screen.blit(self.black_surface, (base_x + self.x, base_y + self.y))

        if self.show_value:
            if self.target_value:
                text = self.font.render(f"{self.value}/{self.target_value}", True, (255, 255, 255))
            else:
                text = self.font.render(f"{self.value}", True, (255, 255, 255))
            text_rect = text.get_rect(center=(base_x + self.center_x, base_y + self.center_y))
            screen.blit(text, text_rect)

    def is_clicked(self, base_x, base_y, pos):
        distance = ((pos[0] - (base_x + self.center_x)) ** 2 + (pos[1] - (base_y + self.center_y)) ** 2) ** 0.5
        return distance <= self.radius

    def set_color(self, new_color):
        self.color = new_color
        self.create_planet_surface()

    def to_dict(self):
        return {
            'x': self.x,
            'y': self.y,
            'color': self.color,
            'radius': self.radius,
            'value': self.value,
            'rocket_upgrade': self.rocket_upgrade,
            'satellite_upgrade': self.satellite_upgrade,
            'base_texture_name': self.base_texture_name,
            'noise_texture_name': self.noise_texture_name,
            'light_texture_name': self.light_texture_name,
        }

    @classmethod
    def from_dict(cls, data):
        planet = cls(data['x'], data['y'], tuple(data['color']), data['radius'], True, data['base_texture_name'], data['noise_texture_name'], data['light_texture_name'])
        planet.value = data.get('value', 1)
        planet.rocket_upgrade = data.get('rocket_upgrade', 1)
        planet.satellite_upgrade = data.get('satellite_upgrade', 0)
        planet.create_planet_surface()
        return planet