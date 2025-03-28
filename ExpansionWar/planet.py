import random
import pygame
from config import *

class Planet:
    def __init__(self, x, y):
        radius = PLANET_RADIUS

        self.x = x
        self.y = y

        self.radius = radius
        self.selected = False
        self.center_x = self.x + self.radius
        self.center_y = self.y + self.radius

        self.color = (
            random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255)
        )

        self.connected_cells = []

        self.target_value = None
        self.value = 1

        base_texture = random.choice([planet_assets[key] for key in planet_assets if "sphere" in key])
        noise_texture = random.choice([planet_assets[key] for key in planet_assets if "noise" in key])
        light_texture = random.choice([planet_assets[key] for key in planet_assets if "light" in key])

        self.base_texture = pygame.transform.scale(base_texture, (radius * 2, radius * 2))
        self.noise_texture = pygame.transform.scale(noise_texture, (radius * 2, radius * 2))
        self.light_texture = pygame.transform.scale(light_texture, (radius * 2, radius * 2))

        self.surface = self.create_planet_surface()

    def create_planet_surface(self):
        planet_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)

        planet_surface.blit(self.base_texture, (0, 0))  # Base sphere texture
        planet_surface.blit(self.light_texture, (0, 0), special_flags = pygame.BLEND_RGBA_MULT)
        planet_surface.blit(self.noise_texture, (0, 0))

        colored_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        colored_surface.fill(self.color)

        self.selected_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        self.selected_surface.fill((255,255,255,127))
        self.selected_surface.blit(self.base_texture, (0, 0), special_flags = pygame.BLEND_RGBA_MULT)

        planet_surface.blit(colored_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        return planet_surface

    def draw(self, screen, base_x, base_y):
        screen.blit(self.surface, (base_x + self.x, base_y + self.y))
        if self.selected:
            screen.blit(self.selected_surface, (base_x + self.x, base_y + self.y))

        font = pygame.font.SysFont('Arial', 20)
        if self.target_value:
            text = font.render(f"{self.value}/{self.target_value}", True, (255, 255, 255))
        else:
            text = font.render(f"{self.value}", True, (255, 255, 255))

        text_rect = text.get_rect(center=(base_x + self.center_x, base_y + self.center_y))
        screen.blit(text, text_rect)


    def is_clicked(self, base_x, base_y, pos):
        distance = ((pos[0] - (base_x + self.center_x)) ** 2 + (pos[1] - (base_y + self.center_y)) ** 2) ** 0.5
        return distance <= self.radius
