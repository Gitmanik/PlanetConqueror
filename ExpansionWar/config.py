import os
import pygame

def scale(val, src, dst):
    return ((val - src[0]) / (src[1]-src[0])) * (dst[1]-dst[0]) + dst[0]

ASSETS_FOLDER = "assets"


# Screen dimensions

BASE_WIDTH = 400
BASE_HEIGHT = 700

SCREEN_WIDTH = 400*2
SCREEN_HEIGHT = 700*2

#UI
GAME_INFO_BAR_HEIGHT = 50
PLANET_RADIUS = 30
PLANET_TEXT_SIZE = 24

GAME_INFO_BAR_HEIGHT = scale(GAME_INFO_BAR_HEIGHT, (0, BASE_HEIGHT), (0, SCREEN_HEIGHT))
PLANET_RADIUS = scale(PLANET_RADIUS, (0, BASE_HEIGHT), (0, SCREEN_HEIGHT))
PLANET_TEXT_SIZE = int(scale(PLANET_TEXT_SIZE, (0, BASE_HEIGHT), (0, SCREEN_HEIGHT)))


GAME_SCENE_WIDTH = SCREEN_WIDTH
GAME_SCENE_HEIGHT = SCREEN_HEIGHT - GAME_INFO_BAR_HEIGHT


# Colors
BACKGROUND_COLOR = (40, 40, 60)
GRID_COLOR = (60, 60, 80)
CONNECTION_COLOR = (180, 100, 200)

background = pygame.image.load(os.path.join(ASSETS_FOLDER, "GSFC_20171208_Archive_e000012~medium.jpg"))
background = pygame.transform.scale(background, [SCREEN_WIDTH,SCREEN_HEIGHT])

planet_assets = dict()
def load_assets():
    print("Loading assets...")
    for file in os.listdir(os.path.join(ASSETS_FOLDER, "PlanetParts")):
        if not file.endswith(".png"):
            continue
        filename = file.split(".")[0]
        planet_assets[filename] = pygame.image.load(os.path.join(ASSETS_FOLDER, "PlanetParts", file))
