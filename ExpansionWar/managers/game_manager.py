import logging
import math
import os
import random

import pygame

import config
from data.game_data import GameData
from entities.connection import Connection
from entities.planet import Planet
from scenes.game_config_scene import GameConfigScene
from scenes.info_scene import InfoScene

logger = logging.getLogger(__name__)


class GameManager:
    def __init__(self):
        logger.info(f"Initializing GameManager")
        self.data = None
        self.ticks = 0

        # Flag to ensure the enemy AI only acts once per enemy turn.
        self.enemy_ai_done = False

    def new_game(self, mode : str, ip : str = None, port : str = None):
        from scenes.game_scene import GameScene
        if mode == "1player":
            self.data = GameData(config.PLAYER_COLOR, None, 2100, 2100, 1)
            self.generate_planets()
            pass
        elif mode == "2local":
            self.data = GameData(config.PLAYER_COLOR, config.PLAYER2_COLOR, 2100, 2100, 1)
            self.generate_planets()
            pass
        elif mode == "network_host":
            config.set_scene(InfoScene("Not available yet\nsorry.", 2.5, GameConfigScene()))
            pass
        elif mode == "network_client":
            config.set_scene(InfoScene("Not available yet\nsorry.", 2.5, GameConfigScene()))
            pass

        config.set_scene(GameScene(self))

    def next_level(self):
        from scenes.game_scene import GameScene
        self.data = GameData(self.data.p1color, self.data.p2color, self.data.year, self.data.year_start, self.data.level + 1)
        self.generate_planets()

        config.set_scene(GameScene(self))


    def load_game(self, selected_file : str):
        from scenes.game_scene import GameScene
        try:
            logger.info(f"Loading game from {selected_file}")
            ext = os.path.splitext(selected_file)[1]
            if ext == ".json":
                self.data = GameData.load_json(selected_file)
            elif ext == ".xml":
                self.data = GameData.load_xml(selected_file)
            elif ext == ".mongo":
                self.data = GameData.load_from_mongo(selected_file)

            config.set_scene(GameScene(self))

        except Exception as e:
            logger.error(f"Load failed: {str(e)}")
            from scenes.info_scene import InfoScene
            config.set_scene(InfoScene(f"Load failed!\n{str(e)}", 3, self))

    def sync(self):
        pass

    def tick(self):
        self.data.current_ticks += pygame.time.get_ticks() - self.ticks
        self.ticks = pygame.time.get_ticks()

        # Enemy AI
        if self.data.current_turn_color not in (self.data.p1color, self.data.p2color) and not self.enemy_ai_done:
            self.run_enemy_ai_turn()

        for color in sorted(set(planet.color for planet in self.data.planets if
                                planet.color != config.NO_OWNER_COLOR and planet.color not in (
                                self.data.p1color, self.data.p2color))):
            self.run_enemy_ai_continous(color)

        all_colors = sorted(set(planet.color for planet in self.data.planets))
        all_playing_colors = sorted(
            set(planet.color for planet in self.data.planets if planet.color != config.NO_OWNER_COLOR))

        # Update black surface
        for planet in self.data.planets:
            if config.current_scene.dragging_card == 0:
                planet.apply_black_surface = not (
                        planet.color == self.data.current_turn_color and planet.value > config.SATELLITE_COST)
            elif config.current_scene.dragging_card == 1:
                planet.apply_black_surface = not (
                        planet.color == self.data.current_turn_color and planet.value > config.ROCKET_COST)

        # End condition
        if len(all_colors) == 1:
            from scenes.menu_scene import MenuScene
            if all_colors.pop() in (self.data.p1color, self.data.p2color):
                logger.info("win")
                self.data.level += 1
                # config.set_scene(InfoScene("Mission\nSuccessful!", 2.5, GameScene(self.data.next_level())))
                config.set_scene(InfoScene("Mission\nSuccessful!.", 2.5, MenuScene()))
            else:
                logger.info("lose")
                config.set_scene(InfoScene("Mission\nfailed.", 2.5, MenuScene()))
            return

        # Turn time
        if self.data.current_ticks - self.data.current_turn_start > config.TURN_TIME or self.data.current_turn_color not in all_playing_colors:
            idx = all_playing_colors.index(
                self.data.current_turn_color) + 1 if self.data.current_turn_color in all_playing_colors else 0
            if idx >= len(all_playing_colors):
                self.data.year += 1

            config.current_scene.dragging_card = None
            self.data.current_turn_color = all_playing_colors[idx % len(all_playing_colors)]
            self.data.current_turn_start = self.data.current_ticks

            if self.data.current_turn_color not in (self.data.p1color, self.data.p2color):
                self.enemy_ai_done = False

    def card_dropped(self, card : int, planet : Planet):
        logger.info(f"Card dropped on planet {planet}")
        if card == 0:
            if planet.color == self.data.current_turn_color and planet.value > config.SATELLITE_COST and planet.satellite_upgrade < 6:
                planet.satellite_upgrade += 1
                planet.value -= config.SATELLITE_COST
                logger.info(f"Upgraded Satellite on planet {planet}, new value: {planet.satellite_upgrade}")
        elif card == 1:
            if planet.color == self.data.current_turn_color and planet.value > config.ROCKET_COST and planet.rocket_upgrade < 4:
                planet.rocket_upgrade += 1
                planet.value -= config.ROCKET_COST
                logger.info(f"Upgraded Rocket on planet {planet}, new value: {planet.rocket_upgrade}")
        else:
            logger.error(f"Wrong card type: {card}")

    def connection_created(self, planet : Planet, other_planet : Planet):
        self.data.connections.append(Connection(planet, other_planet))

    def connection_deleted(self, connection : Connection):
        self.data.connections.remove(connection)
    # Enemy AI

    def run_enemy_ai_turn(self):
        enemy_planets = [planet for planet in self.data.planets if planet.color == self.data.current_turn_color]
        if not enemy_planets:
            self.enemy_ai_done = True
            return

        # Try to use a card upgrade.
        if random.random() < 0.9:
            chosen = random.choice(enemy_planets)
            if chosen.value > config.SATELLITE_COST and chosen.satellite_upgrade < 6:
                chosen.satellite_upgrade += 1
                chosen.value -= config.SATELLITE_COST
                logger.info(
                    f"Enemy {self.data.current_turn_color} {chosen} upgraded Satellite, new upgrade: {chosen.satellite_upgrade}")
            elif chosen.value > config.ROCKET_COST and chosen.rocket_upgrade < 4:
                chosen.rocket_upgrade += 1
                chosen.value -= config.ROCKET_COST
                logger.info(
                    f"Enemy {self.data.current_turn_color} {chosen} upgraded Rocket, new upgrade: {chosen.rocket_upgrade}")
        self.enemy_ai_done = True

    def run_enemy_ai_continous(self, color : (int, int, int)):
        # Try to make a new connection.
        if random.random() > 0.005:
            return

        enemy_planets = [planet for planet in self.data.planets if planet.color == color]
        source = random.choice(enemy_planets)
        candidates = []
        for candidate in self.data.planets:
            if candidate != source:
                # Check if there is already a connection between source and candidate.
                already_connected = False
                for connection in self.data.connections:
                    if (connection.planet == source and connection.other_planet == candidate) or \
                            (connection.planet == candidate and connection.other_planet == source):
                        already_connected = True
                        break
                if not already_connected:
                    candidates.append(candidate)
        if candidates:
            target = random.choice(candidates)
            self.data.connections.append(Connection(source, target))
            logger.info(f"Enemy connection made between {source} and {target}")

        self.enemy_ai_done = True


    def generate_planets(self):
        enemy_ct = round(1.5 ** self.data.level - 0.5)
        enemy_planets = round(1.5 ** self.data.level - 0.5)

        logger.info(f"Generating planets: level: {self.data.level}, enemy_ct: {enemy_ct}, enemy_planets: {enemy_planets}")

        for i in range(-2, enemy_ct):
            if i == -1:
                color = self.data.p1color
            elif i == -2:
                color = config.NO_OWNER_COLOR
            elif self.data.p2color is not None and i == 0:
                color = self.data.p2color
            else:
                color = (
                    random.randint(50, 255),
                    random.randint(50, 255),
                    random.randint(50, 255)
                )

            for _ in range(0, enemy_planets):
                while True:
                    ok = True
                    x = random.uniform(config.PLANET_RADIUS * 2, config.GAME_SCENE_WIDTH - config.PLANET_RADIUS * 2)
                    y = random.uniform(config.PLANET_RADIUS * 2, config.GAME_SCENE_HEIGHT - config.PLANET_RADIUS * 2)

                    candidate_center = (x + config.PLANET_RADIUS, y + config.PLANET_RADIUS)

                    for planet in self.data.planets:
                        dx = candidate_center[0] - planet.center_x
                        dy = candidate_center[1] - planet.center_y
                        distance = math.hypot(dx, dy)

                        if distance < 2 * config.PLANET_RADIUS:
                            ok = False
                            break

                    if ok:
                        break

                self.data.planets.append(Planet(x, y, color))

