import pygame
import config
from planet import Planet
from scenes.game_scene import GameScene
from scenes.how_to_play import HowToPlayScene

class MenuScene:
    def __init__(self):
        self.title_font = pygame.font.Font(config.assets[config.FONT_NAME], 100)
        self.button_font = pygame.font.Font(config.assets[config.FONT_NAME], 60)
        self.link_font = pygame.font.Font(config.assets[config.FONT_NAME], 40)

        # Render texts.
        self.title_text = self.title_font.render("Planet", True, (255, 255, 255))
        self.title2_text = self.title_font.render("Conqueror", True, (255, 255, 255))
        self.start_text = self.button_font.render("Start", True, (0, 0, 0))
        self.how_to_play_text = self.link_font.render("How to Play", True, (0, 0, 0))  # new button text
        self.github_text = self.link_font.render("GitHub: @gitmanik", True, (0, 255, 0))

        self.start_button_rect = None
        self.how_to_play_button_rect = None
        self.github_rect = None

        self.planet = Planet(config.SCREEN_WIDTH/4, config.SCREEN_HEIGHT/3, config.PLAYER_COLOR, 1000, False)

    def draw(self, surface):
        screen_width, screen_height = surface.get_size()

        self.planet.draw(surface, 0, 0)

        title_rect = self.title_text.get_rect(midtop=(screen_width // 2, 50))
        surface.blit(self.title_text, title_rect)
        title2_rect = self.title2_text.get_rect(midtop=(screen_width // 2, 50 + title_rect.height - 40))
        surface.blit(self.title2_text, title2_rect)

        button_width, button_height = 350, 90
        gap = 20

        total_buttons_height = button_height * 2 + gap
        start_y = (screen_height - total_buttons_height) // 2

        # Center both buttons horizontally
        self.start_button_rect = pygame.Rect(
            (screen_width - button_width) // 2,
            start_y,
            button_width,
            button_height
        )
        self.how_to_play_button_rect = pygame.Rect(
            (screen_width - button_width) // 2,
            start_y + button_height + gap,
            button_width,
            button_height
        )

        # Start button
        pygame.draw.rect(surface, (255, 255, 255), self.start_button_rect)
        pygame.draw.rect(surface, (0, 0, 0), self.start_button_rect, 2)
        start_text_rect = self.start_text.get_rect(center=self.start_button_rect.center)
        surface.blit(self.start_text, start_text_rect)

        # How to Play button
        pygame.draw.rect(surface, (255, 255, 255), self.how_to_play_button_rect)
        pygame.draw.rect(surface, (0, 0, 0), self.how_to_play_button_rect, 2)
        how_to_play_text_rect = self.how_to_play_text.get_rect(center=self.how_to_play_button_rect.center)
        surface.blit(self.how_to_play_text, how_to_play_text_rect)

        self.github_rect = self.github_text.get_rect(midbottom=(screen_width // 2, screen_height - 20))
        surface.blit(self.github_text, self.github_rect)

    def handle_click(self, pos):
        if self.start_button_rect and self.start_button_rect.collidepoint(pos):
            config.set_scene(GameScene(1, 2100))
            return True

        if self.how_to_play_button_rect and self.how_to_play_button_rect.collidepoint(pos):
            config.set_scene(HowToPlayScene())
            return True

        if self.github_rect and self.github_rect.collidepoint(pos):
            import webbrowser
            webbrowser.open("https://gitmanik.dev")
            return True

        return False

    def handle_mouse_motion(self, pos):
        return False

    def handle_mouse_up(self, pos):
        return False
