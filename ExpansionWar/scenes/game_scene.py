import logging
import random

import pygame

import config
from card import Card
from connection import Connection
from game_data import GameData
from scenes.info_scene import InfoScene

logger = logging.getLogger(__name__)

class GameScene:
    def __init__(self, data: GameData):

        self.data = data

        self.selected_planet = None

        self.planets_base_x = 0
        self.planets_base_y = config.GAME_INFO_BAR_HEIGHT

        self.info_bar_surface = pygame.Surface((config.SCREEN_WIDTH, config.GAME_INFO_BAR_HEIGHT))
        self.info_bar_surface.set_alpha(200)
        self.info_bar_surface.fill((0, 0, 0))
        self.info_bar_font = pygame.font.Font(config.assets[config.FONT_NAME], 48)

        self.cards_surface = pygame.Surface((config.SCREEN_WIDTH, config.CARDS_BAR_HEIGHT))
        self.cards_surface.set_alpha(200)
        self.cards_surface.fill((0, 0, 0))

        self.save_button_img = pygame.image.load(config.assets["save.png"])
        btn_width = self.save_button_img.get_width()
        btn_x = (config.SCREEN_WIDTH - btn_width) // 2
        btn_y = (config.GAME_INFO_BAR_HEIGHT - self.save_button_img.get_height()) // 2
        self.save_btn_rect = pygame.Rect(btn_x, btn_y, btn_width, self.save_button_img.get_height())

        self.cards = []
        self.cards.append(Card(config.CARDS_BAR_HEIGHT * 3 / 4 * 3 / 4, config.CARDS_BAR_HEIGHT * 3 / 4, pygame.image.load(config.assets["satellite.png"]), 10))
        self.cards.append(Card(config.CARDS_BAR_HEIGHT * 3 / 4 * 3 / 4, config.CARDS_BAR_HEIGHT * 3 / 4, pygame.image.load(config.assets["Rockets/spaceRockets_002.png"]), 5))

        self.card_rects = self.get_card_rects()

        self.dragging_card = None
        self.dragging_card_offset = (0, 0)
        self.dragging_card_pos = (0, 0)

        # Flag to ensure the enemy AI only acts once per enemy turn.
        self.enemy_ai_done = False

        self.ticks = 0

    def draw(self, surface):
        self.data.current_ticks += pygame.time.get_ticks() - self.ticks
        self.ticks = pygame.time.get_ticks()

        surface.blit(self.info_bar_surface, (0,0))
        if self.data.current_turn_color in (self.data.p1color, self.data.p2color):
            surface.blit(self.cards_surface, (0, self.planets_base_y + config.GAME_SCENE_HEIGHT))

        self.draw_info(surface)
        self.draw_cards(surface)
        if self.data.current_turn_color not in (self.data.p1color, self.data.p2color):
            surface.blit(self.cards_surface, (0, self.planets_base_y + config.GAME_SCENE_HEIGHT))

        self.draw_turn(surface)

        for connection in self.data.connections:
            connection.draw(self.planets_base_x, self.planets_base_y, surface, self.data.current_ticks)

        for planet in self.data.planets:
            planet.draw(surface, self.planets_base_x, self.planets_base_y, self.data.current_ticks)

        if self.dragging_card is not None:
            self.cards[self.dragging_card].draw(surface, self.dragging_card_pos[0], self.dragging_card_pos[1])

        # GAME LOGIC

        # Enemy AI
        if self.data.current_turn_color not in (self.data.p1color, self.data.p2color) and not self.enemy_ai_done:
            self.run_enemy_ai_turn()

        for color in sorted(set(planet.color for planet in self.data.planets if planet.color != config.NO_OWNER_COLOR and planet.color not in (self.data.p1color, self.data.p2color))):
            self.run_enemy_ai_continous(color)

        all_colors = sorted(set(planet.color for planet in self.data.planets))
        all_playing_colors = sorted(set(planet.color for planet in self.data.planets if planet.color != config.NO_OWNER_COLOR))

        # Update black surface
        for planet in self.data.planets:
            if self.dragging_card == 0:
                planet.apply_black_surface = not (
                            planet.color == self.data.current_turn_color and planet.value > config.SATELLITE_COST)
            elif self.dragging_card == 1:
                planet.apply_black_surface = not (
                            planet.color == self.data.current_turn_color and planet.value > config.ROCKET_COST)

        # End condition
        if len(all_colors) == 1:
            if all_colors.pop() in (self.data.p1color, self.data.p2color):
                config.logger.info("win")
                self.data.level += 1
                config.set_scene(InfoScene("Mission\nSuccessful!", 2.5, GameScene(self.data.next_level())))
            else:
                config.logger.info("lose")
                from scenes.menu_scene import MenuScene
                config.set_scene(InfoScene("Mission\nfailed.", 2.5, MenuScene()))
            return

        # Turn time
        if self.data.current_ticks - self.data.current_turn_start > config.TURN_TIME or self.data.current_turn_color not in all_playing_colors:
            idx = all_playing_colors.index(self.data.current_turn_color) + 1 if self.data.current_turn_color in all_playing_colors else 0
            if idx >= len(all_playing_colors):
                self.data.year += 1

            self.dragging_card = None
            self.data.current_turn_color = all_playing_colors[(idx) % len(all_playing_colors)]
            self.data.current_turn_start = self.data.current_ticks

            if self.data.current_turn_color not in (self.data.p1color, self.data.p2color):
                self.enemy_ai_done = False

    def run_enemy_ai_turn(self):
        enemy_planets = [planet for planet in self.data.planets if planet.color == self.data.current_turn_color]
        if not enemy_planets:
            self.enemy_ai_done = True
            return

        # Try to use a card upgrade.
        if random.random() < 0.9:
            chosen = random.choice(enemy_planets)
            if chosen.value > config.SATELLITE_COST and chosen.satellite_upgrade < 6:
                chosen.satellite_upgrade += 1
                chosen.value -= config.SATELLITE_COST
                logger.info(f"Enemy {self.data.current_turn_color} {chosen} upgraded Satellite, new upgrade: {chosen.satellite_upgrade}")
            elif chosen.value > config.ROCKET_COST and chosen.rocket_upgrade < 4:
                chosen.rocket_upgrade += 1
                chosen.value -= config.ROCKET_COST
                logger.info(f"Enemy {self.data.current_turn_color} {chosen} upgraded Rocket, new upgrade: {chosen.rocket_upgrade}")
        self.enemy_ai_done = True

    def run_enemy_ai_continous(self, color):
        # Try to make a new connection.
        if random.random() > 0.005:
            return

        enemy_planets = [planet for planet in self.data.planets if planet.color == color]
        source = random.choice(enemy_planets)
        candidates = []
        for candidate in self.data.planets:
            if candidate != source:
                # Check if there is already a connection between source and candidate.
                already_connected = False
                for connection in self.data.connections:
                    if (connection.planet == source and connection.other_planet == candidate) or \
                       (connection.planet == candidate and connection.other_planet == source):
                        already_connected = True
                        break
                if not already_connected:
                    candidates.append(candidate)
        if candidates:
            target = random.choice(candidates)
            self.data.connections.append(Connection(source, target))
            logger.info(f"Enemy connection made between {source} and {target}")

        self.enemy_ai_done = True

    def draw_info(self, surface):
        y = (config.GAME_INFO_BAR_HEIGHT - self.info_bar_font.get_linesize()) / 2

        stage_text = self.info_bar_font.render(f"Level {self.data.level}", True, (255, 255, 255))
        stage_x = 20

        year_text = self.info_bar_font.render(f"Year {self.data.year}", True, (255,255,255))
        year_x = config.SCREEN_WIDTH - year_text.get_width() - stage_x

        surface.blit(stage_text, (stage_x, y))
        surface.blit(year_text, (year_x, y))
        surface.blit(self.save_button_img, (self.save_btn_rect.x, self.save_btn_rect.y))

    def draw_cards(self, surface):
        for i, card in enumerate(self.cards):
            if self.dragging_card == i:
                continue
            card.draw(surface, self.card_rects[i].x, self.card_rects[i].y)

    def draw_turn(self, surface):
        x = config.lerp(0, config.TURN_TIME, config.SCREEN_WIDTH, 0, self.data.current_ticks - self.data.current_turn_start)
        pygame.draw.rect(surface, self.data.current_turn_color, (self.planets_base_x, self.planets_base_y, x, 10))

    def handle_click(self, pos):
        for planet in self.data.planets:
            if planet.is_clicked(self.planets_base_x, self.planets_base_y, pos):
                logger.debug(f"Planet {planet} clicked")
                if self.selected_planet is None:
                    if planet.color not in (self.data.p1color, self.data.p2color) or (self.data.p2color is not None and self.data.current_turn_color != planet.color):
                        config.logger.debug("Enemy planet clicked")
                        return True

                    if planet.value < 1:
                        logger.warning("Planet has value less than 1")
                        return True

                    self.selected_planet = planet
                    planet.selected = True
                    return True
                elif self.selected_planet != planet:
                    if planet in [connection.other_planet for connection in self.data.connections if connection.planet == self.selected_planet]:
                        config.logger.warning("Planets already connected!")
                    else:
                        config.logger.info("Connected planets")
                        self.data.connections.append(Connection(self.selected_planet, planet))

                    self.selected_planet.selected = False
                    self.selected_planet = None
                    return True
                else:
                    planet.selected = False
                    self.selected_planet = None
                    return True

        for connection in self.data.connections:
            if connection.is_clicked(self.planets_base_x, self.planets_base_y, pos):
                logger.debug(f"Connection {connection} clicked")
                if connection.planet.color  in (self.data.p1color, self.data.p2color) and (self.data.p2color is None or (self.data.p2color is not None and self.data.current_turn_color == connection.planet.color)):
                    self.data.connections.remove(connection)
                return True

        if self.data.current_turn_color in (self.data.p1color, self.data.p2color):
            for i, rect in enumerate(self.get_card_rects()):
                if rect.collidepoint(pos):
                    logger.debug(f"Card {i} clicked")
                    self.dragging_card = i
                    self.dragging_card_offset = (pos[0] - rect.x, pos[1] - rect.y)
                    self.dragging_card_pos = (rect.x, rect.y)
                    return True

        if self.save_btn_rect.collidepoint(pos):
            self.data.save_json('save.json')
            self.data.save_xml('save.xml')
            self.data.save_to_mongo("save")
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
            for planet in self.data.planets:
                if planet.is_clicked(self.planets_base_x, self.planets_base_y, pos):
                    config.logger.info(f"Card dropped on planet {planet}")
                    if self.dragging_card == 0:
                        if planet.color == self.data.current_turn_color and planet.value > config.SATELLITE_COST and planet.satellite_upgrade < 6:
                            planet.satellite_upgrade += 1
                            planet.value -= config.SATELLITE_COST
                            logger.info(f"Upgraded Satellite on planet {planet}, new value: {planet.satellite_upgrade}")
                    if self.dragging_card == 1:
                        if planet.color == self.data.current_turn_color and planet.value > config.ROCKET_COST and planet.rocket_upgrade < 4:
                            planet.rocket_upgrade += 1
                            planet.value -= config.ROCKET_COST
                            logger.info(f"Upgraded Rocket on planet {planet}, new value: {planet.rocket_upgrade}")
                    break

            for planet in self.data.planets:
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

    def handle_keydown(self, event):
        if event.key == pygame.K_s:
            self.data.save_json('save.json')
            self.data.save_xml('save.xml')
            self.data.save_to_mongo("save")
        return False
