import json
import logging
import math
import random
from datetime import datetime

import pygame

import config
from connection import Connection
from planet import Planet
from rocket import Rocket

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

    def save(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f)

    @staticmethod
    def load(filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        game = GameData()
        game.p1color = tuple(data['p1color'])
        game.p2color = tuple(data['p2color']) if data['p2color'] is not None else None
        game.year = data['year']
        game.year_start = data['year_start']
        game.level = data['level']
        game.current_turn_color = tuple(data['current_turn_color'])
        game.current_turn_start = data['current_turn_start']
        game.planets = [Planet.from_dict(pd) for pd in data['planets']]
        game.connections = [Connection.from_dict(cd, game.planets) for cd in data.get('connections', [])]
        return game

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