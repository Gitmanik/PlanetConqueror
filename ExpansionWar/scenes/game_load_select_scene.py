import logging
import os

import pygame

from managers.save_manager import SaveManager

import config
from data.game_data import GameData
from scenes.game_scene import GameScene

logger = logging.getLogger(__name__)

class GameLoadSelectScene:
    def __init__(self):
        # Background setup
        self.background = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        self.background.fill((0, 0, 0))
        self.background.set_alpha(200)

        # Font setup
        self.title_font = pygame.font.Font(config.assets[config.FONT_NAME], 100)
        self.file_font = pygame.font.Font(config.assets[config.FONT_NAME], 50)

        self.back_text = self.file_font.render("Back", True, (0, 0, 0))
        button_width, button_height = 350, 90
        self.back_button_rect = pygame.Rect(
            (config.SCREEN_WIDTH - button_width) // 2,
            (config.SCREEN_HEIGHT - button_height - 80),
            button_width,
            button_height
        )

        self.file_entries = []
        files = SaveManager.list_files()
        for file in files:
            if file.endswith((".json", ".xml")):
                entry = {
                    "filename": file,
                    "rect": pygame.Rect(0, 0, 0, 0),
                }
                self.file_entries.append(entry)

    def draw(self, surface):
        surface.blit(self.background, (0, 0))

        # Draw title
        title_surf = self.title_font.render("Load Game", True, (255, 255, 255))
        title_rect = title_surf.get_rect(midtop=(config.SCREEN_WIDTH // 2, 50))
        surface.blit(title_surf, title_rect)

        # Calculate list dimensions
        entry_height = 70
        spacing = 20
        visible_entries = min(len(self.file_entries), 10)
        total_height = visible_entries * (entry_height + spacing) - spacing

        # Vertical centering
        start_y = (config.SCREEN_HEIGHT - total_height) // 2

        # Draw file list
        for i in range(min(visible_entries, len(self.file_entries))):
            entry = self.file_entries[i]
            entry_rect = pygame.Rect(
                0,
                start_y + i * (entry_height + spacing),
                500,
                entry_height
            )
            entry_rect.centerx = config.SCREEN_WIDTH // 2
            entry["rect"] = entry_rect

            is_selected = entry_rect.collidepoint(pygame.mouse.get_pos())
            bg_color = (0, 150, 0) if is_selected else (50, 50, 50)
            border_color = (0, 200, 0) if is_selected else (100, 100, 100)

            pygame.draw.rect(surface, bg_color, entry_rect)
            pygame.draw.rect(surface, border_color, entry_rect, 3)

            # Centered text
            text_surf = self.file_font.render(entry["filename"], True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=entry_rect.center)
            surface.blit(text_surf, text_rect)

        if not self.file_entries:
            empty_text = self.file_font.render("No save files found", True, (150, 150, 150))
            empty_rect = empty_text.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2))
            surface.blit(empty_text, empty_rect)

        # Draw the back button
        pygame.draw.rect(surface, (255, 255, 255), self.back_button_rect)
        pygame.draw.rect(surface, (0, 0, 0), self.back_button_rect, 2)
        back_text_rect = self.back_text.get_rect(center=self.back_button_rect.center)
        surface.blit(self.back_text, back_text_rect)

    def handle_click(self, pos):
        for entry in self.file_entries:
            if entry["rect"].collidepoint(pos):
                config.gm.load_game(entry["filename"])
                return True

        if self.back_button_rect.collidepoint(pos):
            from scenes.menu_scene import MenuScene
            config.set_scene(MenuScene())
            return True

        return False

    def handle_keydown(self, event):
        return False

    def handle_mouse_motion(self, pos):
        return False

    def handle_mouse_up(self, pos):
        return False