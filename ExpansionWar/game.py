import pygame
import sys

from config import *
from game_scene import GameScene

import logging
logger = logging.getLogger(__name__)
from pygame_logger import PygameHandler


pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Planet Conqueror")
clock = pygame.time.Clock()

def main():
    grid = GameScene(1)

    running = True
    while running:
        screen.blit(background, (0, 0), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    grid.handle_click(event.pos)

        grid.draw(screen)
        pygame_handler.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


pygame_handler = None
def setup_logger():
    global pygame_handler
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    pygame_handler = PygameHandler(10)
    pygame_handler.setLevel(logging.DEBUG)
    pygame_handler.setFormatter(formatter)
    logger.addHandler(pygame_handler)

if __name__ == "__main__":
    setup_logger()
    load_assets()
    main()
