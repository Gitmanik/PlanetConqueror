import math
import random

import config
import pygame

from connection import Connection
from planet import Planet

import logging
logger = logging.getLogger(__name__)

class GameScene:
    def __init__(self, level):
        self.planets = []
        self.rockets = []
        self.connections = []

        self.selected_planet = None
        self.level = level

        self.year = 2100

        self.planets_base_x = 0
        self.planets_base_y = config.GAME_INFO_BAR_HEIGHT

        self.info_bar_surface = pygame.Surface((config.SCREEN_WIDTH, config.GAME_INFO_BAR_HEIGHT))
        self.info_bar_surface.set_alpha(200)
        self.info_bar_surface.fill((0, 0, 0))
        self.cards_surface = pygame.Surface((config.SCREEN_WIDTH, config.CARDS_BAR_HEIGHT))
        self.cards_surface.set_alpha(200)
        self.cards_surface.fill((0, 0, 0))

        self.create_level()

    def add_planet(self, planet):
        self.planets.append(planet)

    def draw(self, surface):
        surface.blit(self.info_bar_surface, (0,0))
        surface.blit(self.cards_surface, (0, self.planets_base_y + config.GAME_SCENE_HEIGHT))

        self.draw_info(surface)
        self.draw_cards(surface)

        colors = set(planet.color for planet in self.planets)
        if len(colors) == 1: # Win condition
            if colors.pop() == config.PLAYER_COLOR:
                config.logger.info("win")
                config.set_scene(GameScene(self.level + 1))
            else:
                config.logger.info("lose")
                config.set_scene(GameScene(self.level))
            return

        for connection in self.connections:
            connection.draw(self.planets_base_x, self.planets_base_y, surface)

        for planet in self.planets:
            planet.draw(surface, self.planets_base_x, self.planets_base_y)

    def draw_info(self, surface):
        font = pygame.font.Font(config.FONT_NAME, config.PLANET_TEXT_SIZE)
        y = (config.GAME_INFO_BAR_HEIGHT - font.get_linesize()) / 2

        stage_text = font.render(f"Level {self.level}", True, (255, 255, 255))
        stage_x = 20

        year_text = font.render(f"Year {self.year}", True, (255,255,255))

        year_x = config.SCREEN_WIDTH - year_text.get_width() - stage_x

        surface.blit(stage_text, (stage_x, y))
        surface.blit(year_text, (year_x, y))

    def draw_cards(self, surface):
        total_cards = 4
        spacing = 0

        card_width = (config.SCREEN_WIDTH - 3*spacing) // total_cards
        card_height = 3/4 * config.CARDS_BAR_HEIGHT

        total_width = total_cards * card_width + 3 * spacing
        start_x = (config.SCREEN_WIDTH - total_width) // 2

        card = pygame.transform.scale(config.card, (card_width, card_height))

        y = self.planets_base_y + config.GAME_SCENE_HEIGHT + (config.CARDS_BAR_HEIGHT - card_height) // 2

        for i in range(total_cards):
            x = start_x + i * (card_width + spacing)
            surface.blit(card, (x, y))

    def handle_click(self, pos):
        for planet in self.planets:
            if planet.is_clicked(self.planets_base_x, self.planets_base_y, pos):
                if self.selected_planet is None:
                    if planet.color != config.PLAYER_COLOR:
                        config.logger.debug("Enemy planet clicked")
                        return True

                    self.selected_planet = planet
                    planet.selected = True
                    return True
                elif self.selected_planet != planet:
                    if planet in [connection.other_planet for connection in self.connections if connection.planet == self.selected_planet]:
                        config.logger.warning("Planets already connected!")
                    else:
                        config.logger.info("Connected planets")
                        self.connections.append(Connection(self.selected_planet, planet))

                    self.selected_planet.selected = False
                    self.selected_planet = None
                    return True
                else:
                    planet.selected = False
                    self.selected_planet = None
                    return True

        for connection in self.connections:
            if connection.is_clicked(self.planets_base_x, self.planets_base_y, pos):
                logger.debug(f"Connection {connection} clicked")
                self.connections.remove(connection)
                return True

        return False

    def create_level(self):
        enemy_ct = round(1.5**self.level-0.5)
        enemy_planets = round(1.5**self.level-0.5)

        config.logger.info(f"Creating level {self.level}: enemy_ct: {enemy_ct}, enemy_planets: {enemy_planets}")

        for i in range(-2, enemy_ct):
            if i == -1:
                color = config.PLAYER_COLOR
            elif i == -2:
                color = config.NO_OWNER_COLOR
            else:
                color = (
                    random.randint(50, 255),
                    random.randint(50, 255),
                    random.randint(50, 255)
                )

            for _ in range(0, enemy_planets):
                while True:
                    ok = True
                    x = random.uniform(config.PLANET_RADIUS * 2, config.GAME_SCENE_WIDTH - config.PLANET_RADIUS * 2)
                    y = random.uniform(config.PLANET_RADIUS * 2, config.GAME_SCENE_HEIGHT - config.PLANET_RADIUS * 2)

                    for planet in self.planets:
                        if planet.is_clicked(0, 0, (x + config.PLANET_RADIUS, y + config.PLANET_RADIUS)):
                            ok = False
                    if ok:
                        break
                self.add_planet(Planet(x,y, color))
