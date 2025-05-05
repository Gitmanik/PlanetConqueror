import logging
import sys

import pygame

import config
from managers.game_manager import GameMode

logger = logging.getLogger(__name__)
class GameConfigScene:
    SettingsFile = "menu.json"

    def __init__(self):
        self.active_input = None

        self.ip = "localhost"
        self.port = "5000"
        self.mode = "1player"
        self.network_mode = "client"

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

        # Network mode buttons (Client / Host)
        self.network_buttons = [
            {
                "rect": pygame.Rect(0, 150 + (70 + 20) * 3, 350, 70),
                "label": "Client",
                "value": "client",
            },
            {
                "rect": pygame.Rect(0, 150 + (70 + 20) * 4, 350, 70),
                "label": "Host",
                "value": "host",
            }
        ]
        for btn in self.network_buttons:
            btn["rect"].centerx = config.SCREEN_WIDTH // 2

        # Network configuration
        input_width = int(config.SCREEN_WIDTH * 0.8)
        self.ip_input = {
            "rect": pygame.Rect(0, 150 + (70 + 20) * 4 + 100, input_width, 70),
            "text": self.ip,
            "active": False,
            "hint": "IP Address"
        }
        self.ip_input["rect"].centerx = config.SCREEN_WIDTH // 2

        self.port_input = {
            "rect": pygame.Rect(0, 150 + (70 + 20) * 4 + 100 + 90, 200, 70),
            "text": self.port,
            "active": False,
            "hint": "Port"
        }
        self.port_input["rect"].centerx = config.SCREEN_WIDTH // 2

        # Start button
        self.start_btn = pygame.Rect(
            0, config.SCREEN_HEIGHT - 350 / 2,
            350, 90
        )
        self.start_btn.centerx = config.SCREEN_WIDTH // 2

    def draw(self, surface):
        surface.blit(self.background, (0, 0))

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

        # Network buttons (Client / Host)
        if self.mode == "network":
            for btn in self.network_buttons:
                is_selected = btn["value"] == self.network_mode
                bg_color = (0, 150, 0) if is_selected else (50, 50, 50)
                border_color = (0, 200, 0) if is_selected else (100, 100, 100)

                pygame.draw.rect(surface, bg_color, btn["rect"])
                pygame.draw.rect(surface, border_color, btn["rect"], 3)

                text_color = (255, 255, 255) if is_selected else (150, 150, 150)
                label_surf = self.ui_font.render(btn["label"], True, text_color)
                label_rect = label_surf.get_rect(center=btn["rect"].center)
                surface.blit(label_surf, label_rect)

            # Show IP and Port input fields only if "Client" is selected
            if self.network_mode == "client":
                self.draw_input(surface, self.ip_input, (0, 255, 0) if self.validate_ip() else (255, 0, 0))
                self.draw_input(surface, self.port_input, (0, 255, 0) if self.validate_port() else (255, 0, 0))

        # Start button
        pygame.draw.rect(surface, (255, 255, 255), self.start_btn)
        start_label = self.ui_font.render("Start", True, (0, 0, 0))
        label_rect = start_label.get_rect(center=self.start_btn.center)
        surface.blit(start_label, label_rect)

    def draw_input(self, surface, input_data, col):
        border_color = col if input_data["active"] else (100, 100, 100)
        pygame.draw.rect(surface, border_color, input_data["rect"], 2)

        text = input_data["text"] or input_data["hint"]
        text_color = (200, 200, 200) if not input_data["text"] else (255, 255, 255)
        text_surf = self.ui_font.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=input_data["rect"].center)
        surface.blit(text_surf, text_rect)

    def handle_click(self, pos):
        # Mode selection

        for btn in self.mode_buttons:
            if btn["rect"].collidepoint(pos):
                self.mode = btn["value"]
                if self.mode != "network":
                    self.network_mode = None  # Reset network mode when not in network mode
                return True

        # Network mode selection (Client/Host)
        if self.mode == "network":
            for btn in self.network_buttons:
                if btn["rect"].collidepoint(pos):
                    self.network_mode = btn["value"]
                    return True

        # Network inputs
        if self.network_mode == "client":
            self.ip_input["active"] = self.ip_input["rect"].collidepoint(pos)
            self.port_input["active"] = self.port_input["rect"].collidepoint(pos)

        # Start button
        if self.start_btn.collidepoint(pos):
            self.start_game()
            return True

        return False

    def handle_keydown(self, event):
        if self.network_mode == "client":
            current_input = None
            if self.ip_input["active"]:
                current_input = self.ip_input
            elif self.port_input["active"]:
                current_input = self.port_input

            if current_input:
                if event.key == pygame.K_BACKSPACE:
                    current_input["text"] = current_input["text"][:-1]
                else:
                    char = event.unicode
                    if current_input == self.port_input and not char.isdigit():
                        return
                    if current_input == self.ip_input and not (char.isdigit() or char in ['.', '']):
                        return

                    current_input["text"] += char
                    self.ip = self.ip_input["text"]
                    self.port = self.port_input["text"]
                return True
        return False

    def start_game(self):
        if self.mode == "network":
            if self.network_mode == "client":
                if not self.validate_ip():
                    logger.error("Invalid IP address")
                    return
                if not self.validate_port():
                    logger.error("Invalid port number")
                    return

        mode = self.mode

        if mode == "network" and sys.platform == "emscripten":
            from scenes.menu_scene import MenuScene
            from scenes.info_scene import InfoScene
            config.set_scene(InfoScene("Multiplayer\nnot supported\non web, sorry.", 2.5, MenuScene()))
            return

        if mode == "network":
            if self.network_mode == "client":
                mode = "client"
            else:
                mode = "host"

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
        config.gm.new_game(mode, self.ip_input["text"], self.port_input["text"])

    def validate_ip(self):
        octets = self.ip_input["text"].split('.')
        if len(octets) != 4:
            return False
        for octet in octets:
            if not octet.isdigit() or not 0 <= int(octet) <= 255:
                return False
        return True

    def validate_port(self):
        return self.port_input["text"].isdigit() and 1 <= int(self.port_input["text"]) <= 65535

    def handle_mouse_motion(self, pos):
        return False

    def handle_mouse_up(self, pos):
        return False
