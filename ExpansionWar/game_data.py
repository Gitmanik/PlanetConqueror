import json
import logging
import math
import os
import random
import xml.etree.ElementTree as ET

import pygame
import pymongo
from pymongo.errors import ConnectionFailure

import config
from connection import Connection
from planet import Planet

logger = logging.getLogger(__name__)

class GameData:
    def __init__(self):
        self.p1color = None
        self.p2color = None
        self.planets = None
        self.rockets = None
        self.connections = None
        self.year = None
        self.year_start = None
        self.level = None

        self.current_turn_color = None
        self.current_turn_start = None

    @staticmethod
    def new_game(p1color, p2color, level = 1, year = 2100, year_start = None):
        data = GameData()

        data.p1color = p1color
        data.p2color = p2color
        data.planets = []
        data.rockets = []
        data.connections = []
        data.year = year
        if year_start is not None:
            data.year_start = year_start
        else:
            data.year_start = year
        data.level = level

        data.current_turn_color = p1color
        data.current_turn_start = pygame.time.get_ticks()

        data.generate_planets()

        return data

    def next_level(self):
        data = GameData()
        data.p1color = self.p1color
        data.p2color = self.p2color
        data.planets = []
        data.rockets = []
        data.connections = []
        data.year = self.year
        data.year_start = self.year_start
        data.level = self.level + 1

        data.current_turn_color = self.p1color
        data.current_turn_start = pygame.time.get_ticks()

        data.generate_planets()

        return data

    def to_dict(self):
        return {
            'p1color': self.p1color,
            'p2color': self.p2color,
            'year': self.year,
            'year_start': self.year_start,
            'level': self.level,
            'current_turn_color': self.current_turn_color,
            'current_turn_start': self.current_turn_start,
            'planets': [planet.to_dict() for planet in self.planets],
            'connections': [conn.to_dict(self.planets) for conn in self.connections],
        }

    # ── JSON Support ──

    def save_json(self, filename):
        logger.info(f"Saving GameData to {filename}")
        with open(os.path.join(config.SAVES_FOLDER, filename), 'w') as f:
            json.dump(self.to_dict(), f)

    @staticmethod
    def load_json(filename):
        logger.info(f"Loading GameData from {filename}")
        with open(filename, 'r') as f:
            data = json.load(f)
        return GameData.from_dict(data)

    @staticmethod
    def from_dict(data):
        game = GameData()
        game.p1color = tuple(data['p1color'])
        game.p2color = tuple(data['p2color']) if data['p2color'] is not None else None
        game.year = int(data['year'])
        game.year_start = int(data['year_start'])
        game.level = int(data['level'])
        game.current_turn_color = tuple(data['current_turn_color'])
        game.current_turn_start = int(data['current_turn_start'])
        game.planets = [Planet.from_dict(pd) for pd in data['planets']]
        game.connections = [Connection.from_dict(cd, game.planets) for cd in (data.get('connections') or [])]
        return game

    # ── MongoDB Support ──
    def save_to_mongo(self, filename):
        logger.info(f"Saving GameData to MongoDB: {filename}")
        client = pymongo.MongoClient(config.MONGO_CONNECTION_URI, serverSelectionTimeoutMS=100)
        try:
            db = client[config.MONGO_DB]
            collection = db[config.MONGO_COLLECTION]
            data = self.to_dict()
            data["mongo_name"] = filename
            collection.insert_one(data)
            client.close()
        except ConnectionFailure:
            print("Server not available")

    @classmethod
    def load_from_mongo(cls, filename):
        logger.info(f"Loading GameData from MongoDB: {filename}")
        client = pymongo.MongoClient(config.MONGO_CONNECTION_URI, serverSelectionTimeoutMS=100)
        try:
            db = client[config.MONGO_DB]
            collection = db[config.MONGO_COLLECTION]
            data = collection.find_one({"mongo_name": filename})
            client.close()
            if data is not None:
                return GameData.from_dict(data)
            else:
                return None
        except ConnectionFailure:
            print("Server not available")
            return None
    # ── XML Support ──
    def to_xml(self):
        data_dict = self.to_dict()
        root = dict_to_xml("GameData", data_dict)
        return root

    def save_xml(self, filename):
        logger.info(f"Saving GameData to {filename}")
        root = self.to_xml()
        tree = ET.ElementTree(root)
        tree.write(os.path.join(config.SAVES_FOLDER, filename), encoding='utf-8', xml_declaration=True)

    @staticmethod
    def load_xml(filename):
        logger.info(f"Loading GameData from {filename}")
        tree = ET.parse(filename)
        root = tree.getroot()
        data_dict = xml_to_dict(root)

        def parse_color(val):
            if val is None or val == "None":
                return None
            val = val.strip("()")
            return tuple(int(float(x.strip())) for x in val.split(','))

        def parse_int(val):
            try:
                return int(float(val))
            except (ValueError, TypeError):
                return 0

        def parse_float(val):
            try:
                return float(val)
            except (ValueError, TypeError):
                return 0.0

        # Convert top-level fields.
        if 'p1color' in data_dict:
            data_dict['p1color'] = parse_color(data_dict['p1color'])
        if 'p2color' in data_dict:
            data_dict['p2color'] = parse_color(data_dict['p2color'])
        if 'year' in data_dict:
            data_dict['year'] = parse_int(data_dict['year'])
        if 'year_start' in data_dict:
            data_dict['year_start'] = parse_int(data_dict['year_start'])
        if 'level' in data_dict:
            data_dict['level'] = parse_int(data_dict['level'])
        if 'current_turn_color' in data_dict:
            data_dict['current_turn_color'] = parse_color(data_dict['current_turn_color'])
        if 'current_turn_start' in data_dict:
            data_dict['current_turn_start'] = parse_int(data_dict['current_turn_start'])

        # Ensure 'planets' is a list.
        if 'planets' in data_dict:
            if not isinstance(data_dict['planets'], list):
                data_dict['planets'] = [data_dict['planets']]
        else:
            data_dict['planets'] = []

        # Ensure 'connections' is a list.
        if 'connections' in data_dict:
            if not isinstance(data_dict['connections'], list):
                # Sometimes an empty <connections /> element becomes an empty string or dict.
                if data_dict['connections'] in (None, "", {}):
                    data_dict['connections'] = []
                else:
                    data_dict['connections'] = [data_dict['connections']]
        else:
            data_dict['connections'] = []

        return GameData.from_dict(data_dict)

    def generate_planets(self):
        enemy_ct = round(1.5 ** self.level - 0.5)
        enemy_planets = round(1.5 ** self.level - 0.5)

        logger.info(f"Generating planets: level: {self.level}, enemy_ct: {enemy_ct}, enemy_planets: {enemy_planets}")

        for i in range(-2, enemy_ct):
            if i == -1:
                color = self.p1color
            elif i == -2:
                color = config.NO_OWNER_COLOR
            elif self.p2color is not None and i == 0:
                color = self.p2color
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

                    for planet in self.planets:
                        dx = candidate_center[0] - planet.center_x
                        dy = candidate_center[1] - planet.center_y
                        distance = math.hypot(dx, dy)

                        if distance < 2 * config.PLANET_RADIUS:
                            ok = False
                            break

                    if ok:
                        break

                self.planets.append(Planet(x, y, color))

def dict_to_xml(tag, d):
    elem = ET.Element(tag)
    for key, val in d.items():
        child = ET.SubElement(elem, key)
        if isinstance(val, dict):
            child.append(dict_to_xml(key, val))
        elif isinstance(val, list):
            for item in val:
                if isinstance(item, dict):
                    item_elem = dict_to_xml("item", item)
                    child.append(item_elem)
                else:
                    item_elem = ET.Element("item")
                    item_elem.text = str(item)
                    child.append(item_elem)
        else:
            child.text = str(val)
    return elem

def xml_to_dict(elem):
    d = {}
    for child in elem:
        if list(child):
            # If all subelements are named "item", treat as a list.
            if all(sub.tag == "item" for sub in child):
                d[child.tag] = [xml_to_dict(sub) if list(sub) else sub.text for sub in child]
            else:
                d[child.tag] = xml_to_dict(child)
        else:
            d[child.tag] = child.text
    return d