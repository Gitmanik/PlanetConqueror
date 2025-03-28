import random

import pygame
import sys

from config import *
from game_scene import GameScene
from planet import Planet

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Planet Conqueror")
clock = pygame.time.Clock()

def main():
    grid = GameScene(1)

    for i in range(1,6):
        print("Creating new planet")

        while True:
            ok = True
            x = random.uniform(PLANET_RADIUS * 2, GAME_SCENE_WIDTH - PLANET_RADIUS * 2)
            y = random.uniform(PLANET_RADIUS * 2, GAME_SCENE_HEIGHT - PLANET_RADIUS * 2)

            for planet in grid.planets:
                if planet.is_clicked(0, 0, (x+PLANET_RADIUS, y+PLANET_RADIUS)):
                    ok = False
            if ok:
                break

        grid.add_planet(Planet(x,y))

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

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    load_assets()
    main()
