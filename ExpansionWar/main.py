import asyncio
import sys

import pygame

import config
from managers.asset_manager import AssetManager
from managers.game_manager import GameManager
from managers.pygbagnet_manager import PygbagnetManager
from managers.save_manager import SaveManager
from pygbagnet import pygbag_net
from scenes.menu_scene import MenuScene

import logging
logger = logging.getLogger(__name__)
from managers.pygame_log_manager import PygameLogManager


pygame.init()

screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
pygame.display.set_caption("Planet Conqueror")
clock = pygame.time.Clock()

async def main():

    config.pgnm = PygbagnetManager(pygbag_net.Node(gid="PlanetConqueror"))

    background = pygame.image.load(config.assets["Background.png"])
    background = pygame.transform.scale(background, [config.SCREEN_WIDTH, config.SCREEN_HEIGHT])

    config.current_scene = MenuScene()

    running = True
    while running:
        screen.blit(background, (0, 0), (0, 0, config.SCREEN_WIDTH, config.SCREEN_HEIGHT))

        await config.pgnm.tick()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    if hasattr(config.current_scene, "handle_click"):
                        config.current_scene.handle_click(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if hasattr(config.current_scene, "handle_mouse_up"):
                        config.current_scene.handle_mouse_up(event.pos)
            elif event.type == pygame.MOUSEMOTION:
                if hasattr(config.current_scene, "handle_mouse_motion"):
                    config.current_scene.handle_mouse_motion(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKQUOTE:
                    config.ENABLE_PYGAME_LOG = not config.ENABLE_PYGAME_LOG
                if hasattr(config.current_scene, "handle_keydown"):
                    config.current_scene.handle_keydown(event)

        config.current_scene.draw(screen)
        if config.ENABLE_PYGAME_LOG:
            PygameLogManager.Instance.draw(screen)

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

if __name__ == "__main__":
    if sys.platform == "emscripten":
        import platform
        platform.document.body.style.background = "#000000"
    PygameLogManager.setup()
    SaveManager.setup()
    config.assets = AssetManager("assets.zip")
    config.gm = GameManager()
    asyncio.run(main())
