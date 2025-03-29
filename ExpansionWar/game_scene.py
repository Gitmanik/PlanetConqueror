import math
import random

from config import *
import pygame

from planet import Planet
from rocket import Rocket


class GameScene:
    def __init__(self, level):
        self.planets = []
        self.rockets = []
        self.selected_planet = None
        self.level = level
        self.info_bar_height = GAME_INFO_BAR_HEIGHT

        self.planets_base_x = 0
        self.planets_base_y = self.info_bar_height

        self.create_level()

    def add_planet(self, planet):
        self.planets.append(planet)

    def rocket_finished(self, rocket):
        self.rockets.remove(rocket)

    def draw(self, surface):
        for planet in self.planets:
            for i in range(0, len(planet.connected_planets)):
                connected_planet_data = planet.connected_planets[i]
                connected_planet = connected_planet_data[0]
                connected_planet_tick = connected_planet_data[1]

                if planet.value > 0 and connected_planet_tick > planet.send_rocket_every:
                    planet.connected_planets[i] = (connected_planet, 0)
                    self.rockets.append(Rocket(self, planet, connected_planet))
                    planet.value -=1
                else:
                    planet.connected_planets[i] = (connected_planet, connected_planet_tick + 1)

                pygame.draw.line(surface, CONNECTION_COLOR,
                                 (self.planets_base_x + planet.center_x, self.planets_base_y + planet.center_y),
                                 (self.planets_base_x + connected_planet.center_x, self.planets_base_y + connected_planet.center_y), 5)

        self.draw_ui(surface)

        for rocket in self.rockets:
            rocket.draw(self.planets_base_x, self.planets_base_y, surface)

        for planet in self.planets:
            planet.draw(surface, self.planets_base_x, self.planets_base_y)

    def draw_ui(self, surface):
        font = pygame.font.SysFont('Arial', PLANET_TEXT_SIZE)
        stage_text = font.render(f"Level {self.level}", True, (255, 255, 255))
        surface.blit(stage_text, (20, 20))

    def handle_click(self, pos):
        for planet in self.planets:
            if planet.is_clicked(0, self.info_bar_height, pos):
                if self.selected_planet is None:
                    if planet.color != PLAYER_COLOR:
                        print("Enemy planet clicked")
                        return True

                    self.selected_planet = planet
                    planet.selected = True
                    return True
                elif self.selected_planet != planet:
                    if planet in self.selected_planet.connected_planets:
                        print("Planets already connected!")
                    else:
                        print("Connected planets")
                        self.selected_planet.connect_planet(planet)

                    self.selected_planet.selected = False
                    self.selected_planet = None
                    return True
                else:
                    planet.selected = False
                    self.selected_planet = None
                    return True
        return False

    def create_level(self):

        enemy_ct = round(1.5**self.level-0.5)
        enemy_planets = round(1.5**self.level-0.5)

        print(f"Creating level {self.level}: enemy_ct: {enemy_ct}, enemy_planets: {enemy_planets}")

        for i in range(-2, enemy_ct):
            if i == -1:
                color = PLAYER_COLOR
            elif i == -2:
                color = NO_OWNER_COLOR
            else:
                color = (
                    random.randint(50, 255),
                    random.randint(50, 255),
                    random.randint(50, 255)
                )

            for _ in range(0, enemy_planets):
                while True:
                    ok = True
                    x = random.uniform(PLANET_RADIUS * 2, GAME_SCENE_WIDTH - PLANET_RADIUS * 2)
                    y = random.uniform(PLANET_RADIUS * 2, GAME_SCENE_HEIGHT - PLANET_RADIUS * 2)

                    for planet in self.planets:
                        if planet.is_clicked(0, 0, (x + PLANET_RADIUS, y + PLANET_RADIUS)):
                            ok = False
                    if ok:
                        break
                self.add_planet(Planet(x,y, color))
