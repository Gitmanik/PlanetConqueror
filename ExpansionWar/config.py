import logging

ENABLE_PYGAME_LOG = False
TURN_TIME = 10 * 1000


# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 1400


#UI and PLANET
GAME_INFO_BAR_HEIGHT = 100
CARDS_BAR_HEIGHT = 240
PLANET_RADIUS = 60

GAME_SCENE_WIDTH = SCREEN_WIDTH
GAME_SCENE_HEIGHT = SCREEN_HEIGHT - GAME_INFO_BAR_HEIGHT - CARDS_BAR_HEIGHT



# Colors
PLAYER_COLOR = (0, 0x78, 0x48)
PLAYER2_COLOR = (0x78, 0, 0)
NO_OWNER_COLOR = (0x81, 0x83, 0x80)
SATELLITE_RAY_COLOR = (255, 235, 42)


#Upgrade costs
ROCKET_COST = 5
SATELLITE_COST = 10


#Save system
SAVES_FOLDER = "saves"
LOCAL_STORAGE = "saves"


#MongoDB
MONGO_CONNECTION_URI = "mongodb://localhost:27017/"
MONGO_DB = "test"
MONGO_COLLECTION = "planet"


# Assets
assets = None
FONT_NAME = "Kenney Future Narrow.ttf"


#Scene management
current_scene = None
def set_scene(new_scene):
    global current_scene

    logger = logging.getLogger(__name__)
    logger.info(f"Setting scene to {new_scene}")
    current_scene = new_scene

def lerp(x1: float, x2: float, y1: float, y2: float, x: float):
    return ((y2 - y1) * x + x2 * y1 - x1 * y2) / (x2 - x1)