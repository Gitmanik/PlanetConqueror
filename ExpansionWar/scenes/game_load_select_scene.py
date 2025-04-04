import logging
import os
import sys
import json

import pygame
if sys.platform != "emscripten":
    import pymongo
    from pymongo.errors import ConnectionFailure

import config
from game_data import GameData
from scenes.game_scene import GameScene

logger = logging.getLogger(__name__)

class GameLoadSelectScene:
    def __init__(self):
        self.file_entries = []

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

        # Load files
        self.refresh_file_list()

    def refresh_file_list(self):
        """Scan saves directory for loadable files"""
        self.file_entries = []
        if sys.platform == "emscripten":
            from platform import window
            stored = window.localStorage.getItem(config.LOCAL_STORAGE)
            try:
                files_data = json.loads(stored) if stored else {"json": {}, "xml": {}}
            except Exception:
                files_data = {"json": {}, "xml": {}}
            # List JSON entries
            for fname in files_data["json"]:
                entry = {
                    "filename": fname,
                    "rect": pygame.Rect(0, 0, 0, 0),  # Will be updated in draw()
                    "full_path": fname
                }
                self.file_entries.append(entry)
            for fname in files_data["xml"]:
                entry = {
                    "filename": fname,
                    "rect": pygame.Rect(0, 0, 0, 0),
                    "full_path": fname
                }
                self.file_entries.append(entry)
        else:
            # Native platforms: list files in the saves folder
            for fname in os.listdir(config.SAVES_FOLDER):
                if fname.endswith((".json", ".xml")):
                    entry = {
                        "filename": fname,
                        "rect": pygame.Rect(0, 0, 0, 0),  # Updated in draw()
                        "full_path": os.path.join("saves", fname)
                    }
                    self.file_entries.append(entry)
            # Also add MongoDB entries if available
            client = pymongo.MongoClient(config.MONGO_CONNECTION_URI, serverSelectionTimeoutMS=100)
            try:
                client.admin.command('ping')
                db = client[config.MONGO_DB]
                collection = db[config.MONGO_COLLECTION]
                data = collection.find()
                for x in data:
                    entry = {
                        "filename": x["mongo_name"] + ".mongo",
                        "rect": pygame.Rect(0, 0, 0, 0),  # Updated in draw()
                        "full_path": os.path.join("saves", x["mongo_name"])
                    }
                    self.file_entries.append(entry)
                client.close()
            except:
                logger.error("Server not available")

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
                self.load_game(entry["full_path"])
                return True

        if self.back_button_rect.collidepoint(pos):
            from scenes.menu_scene import MenuScene
            config.set_scene(MenuScene())
            return True

        return False

    def load_game(self, selected_file):
        try:
            if sys.platform == "emscripten":
                config.logger.info(f"Loading game from localStorage: {selected_file}")
                ext = os.path.splitext(selected_file)[1]
                if ext == ".json":
                    config.set_scene(GameScene(GameData.load_json(selected_file)))
                elif ext == ".xml":
                    config.set_scene(GameScene(GameData.load_xml(selected_file)))
            else:
                config.logger.info(f"Loading game from {selected_file}")
                ext = os.path.splitext(selected_file)[1]
                if ext == ".json":
                    config.set_scene(GameScene(GameData.load_json(selected_file)))
                elif ext == ".xml":
                    config.set_scene(GameScene(GameData.load_xml(selected_file)))
                elif ext == ".mongo":
                    config.set_scene(GameScene(GameData.load_from_mongo(os.path.splitext(selected_file)[0])))
        except Exception as e:
            config.logger.error(f"Load failed: {str(e)}")
            from scenes.info_scene import InfoScene
            config.set_scene(InfoScene(f"Load failed!\n{str(e)}", 3, self))

    def handle_keydown(self, event):
        return False

    def handle_mouse_motion(self, pos):
        return False

    def handle_mouse_up(self, pos):
        return False