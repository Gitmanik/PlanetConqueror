import json
import logging

from managers.save_manager import SaveManager

logger = logging.getLogger(__name__)

class MenuData:
    def __init__(self, mode : str, ip : str, port : str):
        self.mode = mode
        self.ip = ip
        self.port = port

    def to_dict(self):
        return {
            'mode': self.mode,
            'ip': self.ip,
            'port': self.port,
        }

    @staticmethod
    def from_dict(data):
        return MenuData(data['mode'],
                        data['ip'],
                        data['port'])

    # ── JSON Support ──

    def save_json(self, filename):
        SaveManager.save_file(filename, json.dumps(self.to_dict()))

    @staticmethod
    def load_json(filename):
        str = SaveManager.read_file(filename)
        return MenuData.from_dict(json.loads(str))
