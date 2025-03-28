import math
import random

from config import *
import pygame

from planet import Planet


class GameScene:
    def __init__(self, level):
        self.planets = []
        self.selected_planet = None
        self.level = level
        self.info_bar_height = GAME_INFO_BAR_HEIGHT

        self.create_level()

    def add_planet(self, planet):
        self.planets.append(planet)

    def draw(self, surface):
        for planet in self.planets:
            for connected_cell in planet.connected_planets:
                pygame.draw.line(surface, CONNECTION_COLOR,
                                 (planet.center_x, planet.center_y),
                                 (connected_cell.center_x, connected_cell.center_y), 5)

        self.draw_ui(surface)

        for planet in self.planets:
            planet.draw(surface, 0, self.info_bar_height)

    def draw_ui(self, surface):
        font = pygame.font.SysFont('Arial', PLANET_TEXT_SIZE)
        stage_text = font.render(f"Level {self.level}", True, (255, 255, 255))
        surface.blit(stage_text, (20, 20))

    def handle_click(self, pos):
        for planet in self.planets:
            if planet.is_clicked(0, self.info_bar_height, pos):
                print(f"Clicked planet {planet}")
                if self.selected_planet is None:
                    if planet.color != PLAYER_COLOR:
                        print("Enemy planet clicked")
                        return True

                    self.selected_planet = planet
                    planet.selected = True
                    return True
                elif self.selected_planet != planet:
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

        for i in range(-1, enemy_ct):
            if i == -1:
                color = PLAYER_COLOR
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
