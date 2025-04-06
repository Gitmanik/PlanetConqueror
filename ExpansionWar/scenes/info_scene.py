import pygame

import config


class InfoScene:
    def __init__(self, text, display_seconds, next_scene):
        self.lines = text.split('\n')  # Split input text into lines
        self.duration = display_seconds * 1000
        self.next_scene = next_scene
        self.start_time = pygame.time.get_ticks()

        # Background setup
        self.background = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        self.background.fill((0, 0, 0))
        self.background.set_alpha(200)

        self.font = pygame.font.Font(config.assets[config.FONT_NAME], 72)
        self.text_surfaces = []
        for line in self.lines:
            surface = self.font.render(line.strip() or ' ', True, (255, 255, 255))
            self.text_surfaces.append(surface)

    def draw(self, surface):
        # Draw background
        surface.blit(self.background, (0, 0))

        # Calculate vertical positioning
        total_text_height = sum(surf.get_height() for surf in self.text_surfaces)
        current_y = (config.SCREEN_HEIGHT - total_text_height) // 2

        # Draw each line centered horizontally
        for surf in self.text_surfaces:
            text_x = (config.SCREEN_WIDTH - surf.get_width()) // 2
            surface.blit(surf, (text_x, current_y))
            current_y += surf.get_height()  # Move down for next line

        # Progress bar and timing logic
        elapsed = pygame.time.get_ticks() - self.start_time
        progress_width = config.lerp(0, self.duration,
                                     config.SCREEN_WIDTH, 0,
                                     elapsed)
        pygame.draw.rect(surface, (255, 255, 255),
                         (0, 0, progress_width, 8))

        if elapsed > self.duration:
            config.set_scene(self.next_scene)

    def handle_click(self, pos):
        return False

    def handle_mouse_motion(self, pos):
        return False

    def handle_mouse_up(self, pos):
        return False

    def handle_keydown(self, event):
        return False
