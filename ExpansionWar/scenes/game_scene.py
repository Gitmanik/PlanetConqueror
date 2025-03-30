import math
import random

import config
import pygame

from card import Card
from connection import Connection
from planet import Planet

import logging
logger = logging.getLogger(__name__)

class GameScene:
    def __init__(self, level, year):
        self.planets = []
        self.rockets = []
        self.connections = []

        self.selected_planet = None
        self.level = level
        self.year_start = year
        self.year = year

        self.planets_base_x = 0
        self.planets_base_y = config.GAME_INFO_BAR_HEIGHT

        self.info_bar_surface = pygame.Surface((config.SCREEN_WIDTH, config.GAME_INFO_BAR_HEIGHT))
        self.info_bar_surface.set_alpha(200)
        self.info_bar_surface.fill((0, 0, 0))
        self.info_bar_font = pygame.font.Font(config.assets[config.FONT_NAME], config.PLANET_TEXT_SIZE)

        self.cards_surface = pygame.Surface((config.SCREEN_WIDTH, config.CARDS_BAR_HEIGHT))
        self.cards_surface.set_alpha(200)
        self.cards_surface.fill((0, 0, 0))

        self.current_turn_color = config.PLAYER_COLOR
        self.current_turn_start = pygame.time.get_ticks()
        self.create_level()

        self.cards = []
        self.cards.append(Card(config.CARDS_BAR_HEIGHT * 3 / 4 * 3 / 4, config.CARDS_BAR_HEIGHT * 3 / 4, pygame.image.load(config.assets["satellite.png"]), 10))
        self.cards.append(Card(config.CARDS_BAR_HEIGHT * 3 / 4 * 3 / 4, config.CARDS_BAR_HEIGHT * 3 / 4, pygame.image.load(config.assets["Rockets/spaceRockets_002.png"]), 5))

        self.card_rects = self.get_card_rects()

        self.dragging_card = None
        self.dragging_card_offset = (0, 0)
        self.dragging_card_pos = (0, 0)

    def draw(self, surface):
        surface.blit(self.info_bar_surface, (0,0))
        if self.current_turn_color == config.PLAYER_COLOR:
            surface.blit(self.cards_surface, (0, self.planets_base_y + config.GAME_SCENE_HEIGHT))

        self.draw_info(surface)
        self.draw_cards(surface)
        if self.current_turn_color != config.PLAYER_COLOR:
            surface.blit(self.cards_surface, (0, self.planets_base_y + config.GAME_SCENE_HEIGHT))

        self.draw_turn(surface)

        for connection in self.connections:
            connection.draw(self.planets_base_x, self.planets_base_y, surface)

        for planet in self.planets:
            planet.draw(surface, self.planets_base_x, self.planets_base_y)

        if self.dragging_card is not None:
            self.cards[self.dragging_card].draw(surface, self.dragging_card_pos[0], self.dragging_card_pos[1])

        # GAME LOGIC

        all_colors = sorted(set(planet.color for planet in self.planets))
        all_playing_colors = sorted(set(planet.color for planet in self.planets if planet.color != config.NO_OWNER_COLOR))

        # Update black surface
        for planet in self.planets:
            if self.dragging_card == 0:
                planet.apply_black_surface = not (
                            planet.color == config.PLAYER_COLOR and planet.value > config.SATELLITE_COST)
            elif self.dragging_card == 1:
                planet.apply_black_surface = not (
                            planet.color == config.PLAYER_COLOR and planet.value > config.ROCKET_COST)

        # End condition
        if len(all_colors) == 1:
            if all_colors.pop() == config.PLAYER_COLOR:
                config.logger.info("win")
                config.set_scene(GameScene(self.level + 1, self.year))
            else:
                config.logger.info("lose")
                config.set_scene(GameScene(self.level, self.year_start))
            return

        # Turn time
        if pygame.time.get_ticks() - self.current_turn_start > config.TURN_TIME:
            idx = all_playing_colors.index(self.current_turn_color) + 1
            if idx >= len(all_playing_colors):
                self.year += 1

            self.dragging_card = None
            self.current_turn_color = all_playing_colors[(idx) % len(all_playing_colors)]
            self.current_turn_start = pygame.time.get_ticks()

    def draw_info(self, surface):
        y = (config.GAME_INFO_BAR_HEIGHT - self.info_bar_font.get_linesize()) / 2

        stage_text = self.info_bar_font.render(f"Level {self.level}", True, (255, 255, 255))
        stage_x = 20

        year_text = self.info_bar_font.render(f"Year {self.year}", True, (255,255,255))
        year_x = config.SCREEN_WIDTH - year_text.get_width() - stage_x

        surface.blit(stage_text, (stage_x, y))
        surface.blit(year_text, (year_x, y))

    def draw_cards(self, surface):
        for i, card in enumerate(self.cards):
            if self.dragging_card == i:
                continue
            card.draw(surface, self.card_rects[i].x, self.card_rects[i].y)

    def draw_turn(self, surface):
        x = config.lerp(0, config.TURN_TIME, config.SCREEN_WIDTH, 0, pygame.time.get_ticks() - self.current_turn_start)
        pygame.draw.rect(surface, self.current_turn_color, (self.planets_base_x, self.planets_base_y, x, 10))

    def handle_click(self, pos):
        for planet in self.planets:
            if planet.is_clicked(self.planets_base_x, self.planets_base_y, pos):
                logger.debug(f"Planet {planet} clicked")
                if self.selected_planet is None:
                    if planet.color != config.PLAYER_COLOR:
                        config.logger.debug("Enemy planet clicked")
                        return True

                    if planet.value < 1:
                        logger.warning("Planet has value less than 1")
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
                if connection.planet.color == config.PLAYER_COLOR:
                    self.connections.remove(connection)
                return True

        if self.current_turn_color == config.PLAYER_COLOR:
            for i, rect in enumerate(self.get_card_rects()):
                if rect.collidepoint(pos):
                    logger.debug(f"Card {i} clicked")
                    self.dragging_card = i
                    self.dragging_card_offset = (pos[0] - rect.x, pos[1] - rect.y)
                    self.dragging_card_pos = (rect.x, rect.y)
                    return True

        return False

    def handle_mouse_motion(self, pos):
        if self.dragging_card is not None:
            new_x = pos[0] - self.dragging_card_offset[0]
            new_y = pos[1] - self.dragging_card_offset[1]
            self.dragging_card_pos = (new_x, new_y)
            return True

        return False

    def handle_mouse_up(self, pos):
        if self.dragging_card is not None:
            for planet in self.planets:
                if planet.is_clicked(self.planets_base_x, self.planets_base_y, pos):
                    config.logger.info(f"Card dropped on planet {planet}")
                    if self.dragging_card == 0:
                        if planet.color == config.PLAYER_COLOR and planet.value > config.SATELLITE_COST and planet.satellite_upgrade < 6:
                            planet.satellite_upgrade += 1
                            planet.value -= config.SATELLITE_COST
                            logger.info(f"Upgraded Satellite on planet {planet}, new value: {planet.satellite_upgrade}")
                    if self.dragging_card == 1:
                        if planet.color == config.PLAYER_COLOR and planet.value > config.ROCKET_COST and planet.rocket_upgrade < 4:
                            planet.rocket_upgrade += 1
                            planet.value -= config.ROCKET_COST
                            logger.info(f"Upgraded Rocket on planet {planet}, new value: {planet.rocket_upgrade}")
                    break

            for planet in self.planets:
                planet.apply_black_surface = False

            self.dragging_card = None
            self.dragging_card_offset = (0, 0)
            self.dragging_card_pos = (0, 0)
            return True

        return False

    def get_card_rects(self):
        total_cards = 2
        spacing = 40

        card = self.cards[0]
        card_width = card.card_surface.get_width()
        card_height = card.card_surface.get_height()

        total_width = total_cards * card_width + (total_cards - 1) * spacing
        start_x = (config.SCREEN_WIDTH - total_width) // 2
        y = self.planets_base_y + config.GAME_SCENE_HEIGHT + (config.CARDS_BAR_HEIGHT - card_height) // 2
        rects = []
        for i in range(total_cards):
            x = start_x + i * (card_width + spacing)
            rects.append(pygame.Rect(x, y, card_width, card_height))
        return rects

    def create_level(self):
        enemy_ct = round(1.5**self.level - 0.5)
        enemy_planets = round(1.5**self.level - 0.5)

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

                    candidate_center = (x + config.PLANET_RADIUS, y + config.PLANET_RADIUS)

                    for planet in self.planets:
                        dx = candidate_center[0] - planet.center_x
                        dy = candidate_center[1] - planet.center_y
                        distance = math.hypot(dx, dy)

                        if distance < 2 * config.PLANET_RADIUS:
                            ok = False
                            break

                    if ok:
                        break

                self.planets.append(Planet(x, y, color))
