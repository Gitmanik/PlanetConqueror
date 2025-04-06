import pygame

import config

# Colors
GOLD = (212, 175, 55)      # Border color
WHEAT = (0xF0, 0xC5, 0x63)    # Inner background color
BLACK = (0, 0, 0)

class Card:
    def __init__(self, width, height, texture, points):
        self.card_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        border_thickness = 5

        pygame.draw.rect(self.card_surface, GOLD, (0, 0, width, height), border_radius=15)
        pygame.draw.rect(
            self.card_surface,
            WHEAT,
            (border_thickness, border_thickness, width - 2 * border_thickness,
             height - 2 * border_thickness),
            border_radius=10,
        )

        padding_x = 40
        padding_y = 80

        texture_width = width - padding_x
        texture_height = height - padding_y
        texture = self.auto_scale_texture(texture, texture_width, texture_height)

        texture_rect = texture.get_rect()
        texture_rect.center = (width // 2, height // 2 - 10)
        self.card_surface.blit(texture, texture_rect)

        font_points = pygame.font.Font(config.assets[config.FONT_NAME], 35)

        points_text = font_points.render(str(points), True, BLACK)
        text_rect = points_text.get_rect(center=(width // 2, height - 30))
        self.card_surface.blit(points_text, text_rect)

    def draw(self, surface, x, y):
        surface.blit(self.card_surface, (x, y))

    def auto_scale_texture(self, texture, max_width, max_height):
        orig_width, orig_height = texture.get_size()
        scale = min(max_width / orig_width, max_height / orig_height)
        new_width = int(orig_width * scale)
        new_height = int(orig_height * scale)
        return pygame.transform.scale(texture, (new_width, new_height))