import logging

import pygame

import config
from entities.card import Card
from managers.game_manager import GameManager, GameMode

logger = logging.getLogger(__name__)

class GameScene:
    def __init__(self, manager : GameManager):

        self.manager = manager

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

    def draw(self, surface):
        self.manager.tick()

        if self.manager.data is None:
            return

        surface.blit(self.info_bar_surface, (0,0))
        if self.manager.data.current_turn_color in (self.manager.data.p1color, self.manager.data.p2color):
            surface.blit(self.cards_surface, (0, self.planets_base_y + config.GAME_SCENE_HEIGHT))

        self.draw_info(surface)
        self.draw_cards(surface)

        if self.manager.game_mode == GameMode.LOCAL_TWO_PLAYER and (
            self.manager.data.current_turn_color not in (self.manager.data.p1color, self.manager.data.p2color)
        ) or self.manager.data.current_turn_color != self.manager.data.p1color:
            surface.blit(self.cards_surface, (0, self.planets_base_y + config.GAME_SCENE_HEIGHT))

        self.draw_turn(surface)

        for connection in self.manager.data.connections:
            connection.draw(self.planets_base_x, self.planets_base_y, surface, self.manager.data.current_ticks)

        for planet in self.manager.data.planets:
            planet.draw(surface, self.planets_base_x, self.planets_base_y, self.manager.data.current_ticks)

        if self.dragging_card is not None:
            self.cards[self.dragging_card].draw(surface, self.dragging_card_pos[0], self.dragging_card_pos[1])

    def draw_info(self, surface):
        y = (config.GAME_INFO_BAR_HEIGHT - self.info_bar_font.get_linesize()) / 2

        stage_text = self.info_bar_font.render(f"Level {self.manager.data.level}", True, (255, 255, 255))
        stage_x = 20

        year_text = self.info_bar_font.render(f"Year {self.manager.data.year}", True, (255,255,255))
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
        x = config.lerp(0, config.TURN_TIME, config.SCREEN_WIDTH, 0, self.manager.data.current_ticks - self.manager.data.current_turn_start)
        pygame.draw.rect(surface, self.manager.data.current_turn_color, (self.planets_base_x, self.planets_base_y, x, 10))

    def handle_click(self, pos):
        for planet in self.manager.data.planets:
            if planet.is_clicked(self.planets_base_x, self.planets_base_y, pos):
                logger.debug(f"Planet {planet} clicked")
                if self.selected_planet is None:
                    if self.manager.game_mode == GameMode.SINGLE_PLAYER:
                        if planet.color != self.manager.data.p1color:
                            logger.debug("SP: Enemy planet clicked")
                            return True
                    elif self.manager.game_mode == GameMode.LOCAL_TWO_PLAYER:
                        if planet.color not in (self.manager.data.p1color, self.manager.data.p2color) or self.manager.data.current_turn_color != planet.color:
                            logger.debug("L2P: Enemy planet clicked")
                            return True
                    elif self.manager.game_mode in (GameMode.HOST, GameMode.CLIENT):
                        if planet.color != self.manager.data.p1color:
                            logger.debug("MP: Enemy player's planet clicked")
                            return True

                    if planet.value < 1:
                        logger.warning("Planet has value less than 1")
                        return True

                    self.selected_planet = planet
                    planet.selected = True
                    return True
                elif self.selected_planet != planet:
                    if planet in [connection.other_planet for connection in self.manager.data.connections if connection.planet == self.selected_planet]:
                        logger.warning("Planets already connected!")
                    else:
                        logger.info("Connected planets")
                        self.manager.connection_created(self.selected_planet, planet)

                    self.selected_planet.selected = False
                    self.selected_planet = None
                    return True
                else:
                    planet.selected = False
                    self.selected_planet = None
                    return True

        for connection in self.manager.data.connections:
            if connection.is_clicked(self.planets_base_x, self.planets_base_y, pos):
                logger.debug(f"Connection {connection} clicked")
                if self.manager.game_mode == GameMode.LOCAL_TWO_PLAYER:
                    if connection.planet.color in (self.manager.data.p1color, self.manager.data.p2color) and self.manager.data.current_turn_color != connection.planet.color:
                        logger.debug("Enemy connection clicked")
                        logger.debug("Connection removed")
                        return True

                if connection.planet.color != self.manager.data.p1color:
                    logger.debug("Enemy player's connection clicked")
                    return True

                self.manager.connection_deleted(connection)
                return True

        if (self.manager.game_mode == GameMode.LOCAL_TWO_PLAYER and (
            self.manager.data.current_turn_color in (self.manager.data.p1color, self.manager.data.p2color))) or (
            self.manager.data.current_turn_color == self.manager.data.p1color):
                for i, rect in enumerate(self.get_card_rects()):
                    if rect.collidepoint(pos):
                        logger.debug(f"Card {i} clicked")
                        self.dragging_card = i
                        self.dragging_card_offset = (pos[0] - rect.x, pos[1] - rect.y)
                        self.dragging_card_pos = (rect.x, rect.y)
                        return True

        if self.save_btn_rect.collidepoint(pos):
            self.manager.data.save_json('save.json')
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
            for planet in self.manager.data.planets:
                if planet.is_clicked(self.planets_base_x, self.planets_base_y, pos):
                    self.manager.card_dropped(self.dragging_card, planet)

            for planet in self.manager.data.planets:
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
            self.manager.data.save_json('save.json')
        return False
