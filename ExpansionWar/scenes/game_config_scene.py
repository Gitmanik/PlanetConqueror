import logging

import pygame

import config
from managers.game_manager import GameMode

logger = logging.getLogger(__name__)
class GameConfigScene:
    SettingsFile = "menu.json"

    def __init__(self):
        self.active_input = None

        self.mode = "1player"
        self.new_lobby_text = "New lobby"

        # Main surface setup
        self.background = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        self.background.fill((0, 0, 0))
        self.background.set_alpha(200)

        # Font setup
        self.title_font = pygame.font.Font(config.assets[config.FONT_NAME], 65)
        self.ui_font = pygame.font.Font(config.assets[config.FONT_NAME], 60)

        # Mode selection buttons
        self.mode_buttons = [
            {
                "rect": pygame.Rect(0, 150, 500, 70),
                "label": "1 Player",
                "value": "1player",
            },
            {
                "rect": pygame.Rect(0, 150 + (70 + 20) * 1, 500, 70),
                "label": "2P Local",
                "value": "2local",
            },
            {
                "rect": pygame.Rect(0, 150 + (70 + 20) * 2, 500, 70),
                "label": "Network Game",
                "value": "network",
            }
        ]
        for btn in self.mode_buttons:
            btn["rect"].centerx = config.SCREEN_WIDTH // 2

        self.lobbies = []
        self.selected_lobby = None

        # Start button
        self.start_btn = pygame.Rect(
            0, config.SCREEN_HEIGHT - 350 / 2,
            350, 90
        )
        self.start_btn.centerx = config.SCREEN_WIDTH // 2

    def draw(self, surface):
        surface.blit(self.background, (0, 0))

        self.lobbies = []
        for lobby in config.pgnm.offers.values():
            self.lobbies.append(lobby)

        self.lobbies.append({"id": "NEW_GAME", "lobby_name": self.new_lobby_text})

        # Title
        title_surf = self.title_font.render("Game Configuration", True, (255, 255, 255))
        title_x = (config.SCREEN_WIDTH - title_surf.get_width()) // 2
        surface.blit(title_surf, (title_x, 50))

        # Mode buttons
        for btn in self.mode_buttons:
            is_selected = btn["value"] == self.mode
            bg_color = (0, 150, 0) if is_selected else (50, 50, 50)
            border_color = (0, 200, 0) if is_selected else (100, 100, 100)

            pygame.draw.rect(surface, bg_color, btn["rect"])
            pygame.draw.rect(surface, border_color, btn["rect"], 3)

            text_color = (255, 255, 255) if is_selected else (150, 150, 150)
            label_surf = self.ui_font.render(btn["label"], True, text_color)
            label_rect = label_surf.get_rect(center=btn["rect"].center)
            surface.blit(label_surf, label_rect)

        # Lobby list for network mode
        if self.mode == "network":
            lobby_y = 150 + (70 + 20) * 3
            lobby_h = 70
            lobby_w = 500
            for idx, lobby in enumerate(self.lobbies):
                rect = pygame.Rect(0, lobby_y + idx * (lobby_h + 10), lobby_w, lobby_h)
                rect.centerx = config.SCREEN_WIDTH // 2
                is_selected = self.selected_lobby['id'] == lobby['id'] if self.selected_lobby else False
                bg_color = (0, 150, 200) if is_selected else (60, 60, 60)
                border_color = (0, 200, 220) if is_selected else (120, 120, 120)
                pygame.draw.rect(surface, bg_color, rect)
                pygame.draw.rect(surface, border_color, rect, 3)
                label_text = f"{lobby['lobby_name']}"
                label_surf = self.ui_font.render(label_text, True, (255, 255, 255))
                label_rect = label_surf.get_rect(center=rect.center)
                surface.blit(label_surf, label_rect)
                lobby['rect'] = rect  # for hit detection

        pygame.draw.rect(surface, (255, 255, 255), self.start_btn)
        start_label = self.ui_font.render("Start", True, (0, 0, 0))
        label_rect = start_label.get_rect(center=self.start_btn.center)
        surface.blit(start_label, label_rect)

    def handle_click(self, pos):
        for btn in self.mode_buttons:
            if btn["rect"].collidepoint(pos):
                self.mode = btn["value"]
                self.selected_lobby = None
                return True

        if self.mode == "network":
            for idx, lobby in enumerate(self.lobbies):
                if 'rect' in lobby and lobby['rect'].collidepoint(pos):
                    self.selected_lobby = lobby
                    return True

        if self.start_btn.collidepoint(pos):
            self.start_game()
            return True
        return False

    def start_game(self):
        if self.mode == "network":
            if self.selected_lobby is None:
                logger.error("No lobby selected!")
                return

        mode = self.mode

        if mode == "network":
            if self.selected_lobby['id'] == "NEW_GAME":
                mode = "host"
            else:
                mode = "client"

        match mode:
            case "client":
                mode = GameMode.CLIENT
            case "host":
                mode = GameMode.HOST
            case "1player":
                mode = GameMode.SINGLE_PLAYER
            case "2local":
                mode = GameMode.LOCAL_TWO_PLAYER

        logger.info(f"Starting {mode} game in {self.mode} mode")
        config.gm.new_game(mode, self.selected_lobby)

    def handle_keydown(self, event):
        return False

    def handle_mouse_motion(self, pos):
        return False

    def handle_mouse_up(self, pos):
        return False
