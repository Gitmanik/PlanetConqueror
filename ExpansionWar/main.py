import asyncio

import pygame

import config
from scenes.menu_scene import MenuScene

import logging
logger = logging.getLogger(__name__)
from managers.pygame_log_manager import PygameLogManager


pygame.init()

screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
pygame.display.set_caption("Planet Conqueror")
clock = pygame.time.Clock()

async def main():
    config.current_scene = MenuScene()

    running = True
    while running:
        screen.blit(config.background, (0, 0), (0, 0, config.SCREEN_WIDTH, config.SCREEN_HEIGHT))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    config.current_scene.handle_click(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    config.current_scene.handle_mouse_up(event.pos)
            elif event.type == pygame.MOUSEMOTION:
                config.current_scene.handle_mouse_motion(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKQUOTE:
                    config.ENABLE_PYGAME_LOG = not config.ENABLE_PYGAME_LOG
                config.current_scene.handle_keydown(event)

        config.current_scene.draw(screen)
        if config.ENABLE_PYGAME_LOG:
            PygameLogManager.Instance.draw(screen)

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

if __name__ == "__main__":
    PygameLogManager.setup()
    config.load_assets()
    SaveManager.setup()
    asyncio.run(main())
