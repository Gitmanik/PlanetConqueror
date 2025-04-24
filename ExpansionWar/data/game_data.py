import json
import logging

from managers.save_manager import SaveManager

from entities.connection import Connection
from entities.planet import Planet

logger = logging.getLogger(__name__)

class GameData:
    def __init__(self, p1color : (int, int, int), p2color : (int, int, int), year : int, year_start : int, level : int):
        self.p1color : (int, int, int) = p1color
        self.p2color : (int, int, int) = p2color
        self.planets : [Planet] = []
        self.connections : [Connection] = []
        self.year : int = year
        self.year_start : int = year_start
        self.level : int = level

        self.current_turn_color : (int, int, int) = p1color

        self.current_turn_start : int = 0
        self.current_ticks : int = 0

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
            'current_ticks': self.current_ticks,
        }

    @staticmethod
    def from_dict(data):
        game = GameData(tuple(data['p1color']),
                        tuple(data['p2color']) if data['p2color'] is not None else None,
                        int(data['year']),
                        int(data['year_start']),
                        int(data['level'])
                        )
        game.current_turn_color = tuple(data['current_turn_color'])
        game.current_turn_start = int(data['current_turn_start'])
        game.planets = [Planet.from_dict(pd) for pd in data['planets']]
        game.connections = [Connection.from_dict(cd, game.planets) for cd in (data.get('connections') or [])]
        game.current_ticks = int(data['current_ticks'])
        return game

    # ── JSON Support ──

    def save_json(self, filename):
        SaveManager.save_file(filename, json.dumps(self.to_dict()))

    @staticmethod
    def load_json(filename):
        str = SaveManager.read_file(filename)
        return GameData.from_dict(json.loads(str))
