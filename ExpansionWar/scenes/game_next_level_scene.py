import config


class NextLevelScene:
    def __init__(self):
        pass

    def draw(self, surface):
        config.gm.next_level()

    def handle_click(self, pos):
        return False

    def handle_mouse_motion(self, pos):
        return False

    def handle_mouse_up(self, pos):
        return False

    def handle_keydown(self, event):
        return False
