import logging
import math
import os
import random
import socket
import threading
import json
import time
from enum import Enum

import pygame

import config
from data.game_data import GameData
from entities.connection import Connection
from entities.planet import Planet
from scenes.info_scene import InfoScene

logger = logging.getLogger(__name__)

class GameMode(Enum):
    SINGLE_PLAYER = 1
    LOCAL_TWO_PLAYER = 2
    HOST = 3
    CLIENT = 4


class GameManager:
    def __init__(self):
        logger.info("Initializing GameManager")
        self.data : GameData = None
        self.ticks = 0

        self.enemy_ai_done = False

        self.game_mode : GameMode = None

        # Networking
        self.socket : socket = None
        self.conn : socket = None
        self.network_thread = None
        self.last_tick_sync = 0

    def new_game(self, mode: GameMode , ip: str = None, port: str = None):
        from scenes.game_scene import GameScene

        self.game_mode = mode

        logger.info(f"Creating new game {mode}, ip={ip}, port={port}")

        if self.game_mode == GameMode.SINGLE_PLAYER:
            self.data = GameData(config.PLAYER_COLOR, None, 2100, 2100, 1)
            self.generate_planets()
        elif self.game_mode == GameMode.LOCAL_TWO_PLAYER:
            self.data = GameData(config.PLAYER_COLOR, config.PLAYER2_COLOR, 2100, 2100, 1)
            self.generate_planets()
        elif self.game_mode == GameMode.HOST:
            self.data = GameData(config.PLAYER_COLOR, config.PLAYER2_COLOR, 2100, 2100, 1)
            self.generate_planets()
            self.start_network_server(ip, int(port))
        elif self.game_mode == GameMode.CLIENT:
            self.connect_to_network_server(ip, int(port))
        else:
            raise ValueError(f"Wrong game mode: {self.game_mode}")

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

    def tick(self):
        if self.game_mode == GameMode.HOST and self.conn is None:
            self.ticks = pygame.time.get_ticks()
            return
        elif self.game_mode == GameMode.CLIENT and self.data is None:
            self.ticks = pygame.time.get_ticks()
            return

        self.data.current_ticks += pygame.time.get_ticks() - self.ticks
        self.ticks = pygame.time.get_ticks()

        if self.game_mode == GameMode.HOST and self.data.current_ticks - self.last_tick_sync > 1000:
            self.last_tick_sync = self.data.current_ticks
            self.sync_ticks()

        all_colors = sorted(set(planet.color for planet in self.data.planets))
        all_playing_colors = sorted(
            set(planet.color for planet in self.data.planets if planet.color != config.NO_OWNER_COLOR))

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


        # Enemy AI
        if self.game_mode not in (GameMode.HOST, GameMode.CLIENT):
            if self.data.current_turn_color not in (self.data.p1color, self.data.p2color) and not self.enemy_ai_done:
                self.run_enemy_ai_turn()

            for color in sorted(set(planet.color for planet in self.data.planets if
                                    planet.color != config.NO_OWNER_COLOR and planet.color not in (
                                    self.data.p1color, self.data.p2color))):
                self.run_enemy_ai_continous(color)


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

    def card_dropped(self, card : int, planet : Planet):
        logger.info(f"Card dropped on planet {planet}")

        if self.game_mode == GameMode.CLIENT:
            message = {
                "action": "card_dropped",
                "planet_index": self.data.planets.index(planet),
                "card": card,
                "request": True
            }
            self.send_network_message(message)
            return

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

        if self.game_mode == GameMode.HOST:
            update_message = {
                "action": "card_dropped",
                "planet_index": self.data.planets.index(planet),
                "card": card
            }
            self.send_network_message(update_message)

    def connection_created(self, planet: Planet, other_planet: Planet):
        if self.game_mode == GameMode.CLIENT:
            message = {
                "action": "connection_created",
                "source_index": self.data.planets.index(planet),
                "target_index": self.data.planets.index(other_planet),
                "request": True
            }
            self.send_network_message(message)
            return

        self.data.connections.append(Connection(planet, other_planet))
        logger.info(f"Connection created between {planet} and {other_planet}")

        if self.game_mode == GameMode.HOST:
            update_message = {
                "action": "connection_created",
                "source_index": self.data.planets.index(planet),
                "target_index": self.data.planets.index(other_planet)
            }
            self.send_network_message(update_message)

    def connection_deleted(self, connection: Connection):
        if self.game_mode == GameMode.CLIENT:
            message = {
                "action": "connection_deleted",
                "connection_index": self.data.connections.index(connection),
                "request": True
            }
            self.send_network_message(message)
            return
        elif self.game_mode == GameMode.HOST:
            update_message = {
                "action": "connection_deleted",
                "connection_index": self.data.connections.index(connection),
            }
            self.send_network_message(update_message)

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

    # Networking

    def start_network_server(self, ip: str, port: int):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((ip, port))
        self.socket.listen(1)
        logger.info(f"Server listening on {ip}:{port}")

        def accept_client():
            if self.conn is not None:
                logger.warning(f"Client tried to connect from, but other is already connected")
                return
            self.conn, addr = self.socket.accept()
            logger.info(f"Client connected from {addr}")
            self.start_network_thread()
            self.send_full_data()

        self.network_thread = threading.Thread(target=accept_client, daemon=True)
        self.network_thread.start()

    def connect_to_network_server(self, ip: str, port: int):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, port))
        logger.info(f"Connected to server at {ip}:{port}")
        self.start_network_thread()
        self.ticks = 0

    def start_network_thread(self):
        self.network_thread = threading.Thread(target=self.network_receive_thread, daemon=True)
        self.network_thread.start()

    def send_network_message(self, message: dict):
        try:
            data_str = json.dumps(message) + "\n"
            if self.game_mode == GameMode.HOST and self.conn:
                self.conn.sendall(data_str.encode("utf-8"))
            elif self.game_mode == GameMode.CLIENT and self.socket:
                self.socket.sendall(data_str.encode("utf-8"))
        except Exception as e:
            logger.error("Failed to send network message: " + str(e))

    def network_receive_thread(self):
        try:
            if self.game_mode == GameMode.HOST:
                sock = self.conn
            else:
                sock = self.socket
            file_obj = sock.makefile("r")
            while True:
                line = file_obj.readline()
                if not line:
                    break
                try:
                    message = json.loads(line.strip())
                    self.process_network_message(message)
                except Exception as e:
                    logger.error("Error processing network message: " + str(e))
        except Exception as e:
            logger.error("Network receive error: " + str(e))

    def process_network_message(self, message: dict):
        action = message.get("action")
        if self.game_mode == GameMode.HOST and message.get("request"):
            if action == "card_dropped":
                planet_index = message.get("planet_index")
                card = message.get("card")
                planet = self.data.planets[planet_index]
                # Validate and apply move on the host.
                if card == 0:
                    if planet.value > config.SATELLITE_COST and planet.satellite_upgrade < 6:
                        planet.satellite_upgrade += 1
                        planet.value -= config.SATELLITE_COST
                elif card == 1:
                    if planet.value > config.ROCKET_COST and planet.rocket_upgrade < 4:
                        planet.rocket_upgrade += 1
                        planet.value -= config.ROCKET_COST
                # Broadcast update.
                update_message = {
                    "action": "card_dropped",
                    "planet_index": planet_index,
                    "card": card
                }
                self.send_network_message(update_message)
            elif action == "connection_created":
                source_index = message.get("source_index")
                target_index = message.get("target_index")
                source = self.data.planets[source_index]
                target = self.data.planets[target_index]
                self.data.connections.append(Connection(source, target))
                update_message = {
                    "action": "connection_created",
                    "source_index": source_index,
                    "target_index": target_index
                }
                self.send_network_message(update_message)
            elif action == "connection_deleted":
                try:
                    connection_index = message.get("connection_index")
                    if 0 <= connection_index < len(self.data.connections):
                        self.data.connections.pop(connection_index)

                    update_message = {
                        "action": "connection_deleted",
                        "connection_index": connection_index,
                    }
                    self.send_network_message(update_message)
                except Exception as e:
                    logger.error("Error processing connection deletion request: " + str(e))
            return

        if self.game_mode == GameMode.CLIENT:
            if action == "full_sync":
                game_data_dict = message.get("game_data")
                self.data = GameData.from_dict(game_data_dict)

                logger.info(game_data_dict)

                self.data.p1color = config.PLAYER2_COLOR
                self.data.p2color = config.PLAYER_COLOR

                logger.info("Received full game sync from host")
            elif action == "card_dropped":
                planet_index = message.get("planet_index")
                card = message.get("card")
                planet = self.data.planets[planet_index]
                if card == 0:
                    planet.satellite_upgrade += 1
                    planet.value -= config.SATELLITE_COST
                elif card == 1:
                    planet.rocket_upgrade += 1
                    planet.value -= config.ROCKET_COST
                logger.info("Processed card_dropped update from host")
            elif action == "connection_created":
                source_index = message.get("source_index")
                target_index = message.get("target_index")
                source = self.data.planets[source_index]
                target = self.data.planets[target_index]
                self.data.connections.append(Connection(source, target))
                logger.info("Processed connection_created update from host")
            elif action == "connection_deleted":
                self.data.connections.pop(message.get("connection_index"))
            elif action == "tick_sync":
                new_ticks = int(message.get("ticks"))
                send_timestamp = int(message.get("send_timestamp"))
                client_receive = int(time.time() * 1000)
                offset = client_receive - send_timestamp
                logger.debug(f"Host synced ticks: old={self.data.current_ticks}, new={new_ticks}, offset={offset}")
                self.data.current_ticks = new_ticks + offset

    def send_full_data(self):
        if self.game_mode == GameMode.HOST and self.conn:
            message = {
                "action": "full_sync",
                "game_data": self.data.to_dict()
            }
            self.send_network_message(message)

    def sync_ticks(self):
        if self.game_mode == GameMode.HOST and self.conn:
            message = {
                "action": "tick_sync",
                "send_timestamp": int(time.time() * 1000),
                "ticks": self.data.current_ticks
            }
            self.send_network_message(message)