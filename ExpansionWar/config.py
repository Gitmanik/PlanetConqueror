import pygame
import logging
from assetreader import AssetReader

logger = logging.getLogger(__name__)

def scale(val, src, dst):
    return ((val - src[0]) / (src[1]-src[0])) * (dst[1]-dst[0]) + dst[0]

def lerp(x1: float, x2: float, y1: float, y2: float, x: float):
    return ((y2 - y1) * x + x2 * y1 - x1 * y2) / (x2 - x1)

ENABLE_PYGAME_LOG = False
PYGAME_LOG_LIMIT = 100

TURN_TIME = 10 * 1000

# Screen dimensions
BASE_WIDTH = 400
BASE_HEIGHT = 700

#UI and PLANET
GAME_INFO_BAR_HEIGHT = 50
CARDS_BAR_HEIGHT = 120
PLANET_RADIUS = 30
PLANET_TEXT_SIZE = 24

# Colors
PLAYER_COLOR = (0, 0x78, 0x48)
PLAYER2_COLOR = (0x78, 0, 0)
NO_OWNER_COLOR = (0x81, 0x83, 0x80)
BACKGROUND_COLOR = (40, 40, 60)
CONNECTION_COLOR = (0x81, 0x83, 0x80)
SATELLITE_RAY_COLOR = (255, 235, 42)

#Upgrade costs
ROCKET_COST = 5
SATELLITE_COST = 10

#Scaled dimensions
SCREEN_WIDTH = 400*2
SCREEN_HEIGHT = 700*2

GAME_INFO_BAR_HEIGHT = int(scale(GAME_INFO_BAR_HEIGHT, (0, BASE_HEIGHT), (0, SCREEN_HEIGHT)))
CARDS_BAR_HEIGHT = int(scale(CARDS_BAR_HEIGHT, (0, BASE_HEIGHT), (0, SCREEN_HEIGHT)))
PLANET_RADIUS = scale(PLANET_RADIUS, (0, BASE_HEIGHT), (0, SCREEN_HEIGHT))
PLANET_TEXT_SIZE = int(scale(PLANET_TEXT_SIZE, (0, BASE_HEIGHT), (0, SCREEN_HEIGHT)))

GAME_SCENE_WIDTH = SCREEN_WIDTH
GAME_SCENE_HEIGHT = SCREEN_HEIGHT - GAME_INFO_BAR_HEIGHT - CARDS_BAR_HEIGHT

assets = None
background = None
planet_assets = dict()
rocket_assets = dict()
FONT_NAME = "Kenney Future Narrow.ttf"

def load_assets():
    global assets
    global background

    logger.info("Loading assets...")

    assets = AssetReader("assets.zip")

    for file in assets.find("PlanetParts"):
        if not file.endswith(".png"):
            continue
        filename = file.split(".")[0]
        planet_assets[filename] = pygame.image.load(assets[f"PlanetParts/{file}"])

    for file in assets.find("Rockets"):
        if not file.endswith(".png"):
            continue
        filename = file.split(".")[0]
        rocket_assets[filename] = pygame.image.load(assets[f"Rockets/{file}"])

    background = pygame.image.load(assets["Background.png"])
    background = pygame.transform.scale(background, [SCREEN_WIDTH, SCREEN_HEIGHT])

current_scene = None
def set_scene(new_scene):
    global current_scene

    logger.info(f"Setting scene to {new_scene}")
    current_scene = new_scene
