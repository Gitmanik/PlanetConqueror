import json
import logging
import sys
import xml.etree.ElementTree as ET

from managers.save_manager import SaveManager

import config
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

    # ── XML Support ──
    def to_xml(self):
        data_dict = self.to_dict()
        root = dict_to_xml("GameData", data_dict)
        return root

    def save_xml(self, filename):
        root = self.to_xml()
        xml_str = ET.tostring(root, encoding='utf-8', method='xml').decode('utf-8')
        SaveManager.save_file(filename, xml_str)

    @staticmethod
    def load_xml(filename):
        def parse_color(val):
            if val is None or val == "None":
                return None
            val = val.strip("()")
            return tuple(int(float(x.strip())) for x in val.split(','))

        str = SaveManager.read_file(filename)
        root = ET.fromstring(str)

        data_dict = xml_to_dict(root)

        data_dict['p1color'] = parse_color(data_dict['p1color'])
        data_dict['p2color'] = parse_color(data_dict['p2color'])
        data_dict['current_turn_color'] = parse_color(data_dict['current_turn_color'])

        return GameData.from_dict(data_dict)

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