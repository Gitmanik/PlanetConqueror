import pygame
import logging

import config


class PygameLogManager(logging.Handler):

    Instance = None

    def __init__(self):
        super().__init__()

        self.font = pygame.font.Font(None, 20)
        self.log_lines = []
        self.max_lines = config.SCREEN_HEIGHT // self.font.get_linesize()

    def emit(self, record):
        try:
            msg = self.format(record)
            self.log_lines.append(msg)
            if len(self.log_lines) > self.max_lines:
                self.log_lines.pop(0)
        except Exception:
            self.handleError(record)

    def draw(self, surface):
        y = 0
        for line in self.log_lines:
            text_surface = self.font.render(line, True, (255, 235, 42))
            surface.blit(text_surface, (10, y))
            y += self.font.get_linesize()

    @staticmethod
    def setup():
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        pygame_handler = PygameLogManager()
        pygame_handler.setLevel(logging.DEBUG)
        pygame_handler.setFormatter(formatter)
        logger.addHandler(pygame_handler)

        PygameLogManager.Instance = pygame_handler