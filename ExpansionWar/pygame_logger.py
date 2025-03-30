import pygame
import logging

import config


class PygameHandler(logging.Handler):
    def __init__(self, max_lines=10):
        super().__init__()
        self.max_lines = max_lines
        self.log_lines = []
        self.font = pygame.font.Font(None, 20)

    def emit(self, record):
        try:
            msg = self.format(record)
            self.log_lines.append(msg)
            if len(self.log_lines) > self.max_lines:
                self.log_lines.pop(0)
        except Exception:
            self.handleError(record)

    def draw(self, surface):
        y = 10
        for line in self.log_lines:
            text_surface = self.font.render(line, True, (255, 235, 42))
            surface.blit(text_surface, (10, y))
            y += self.font.get_linesize()