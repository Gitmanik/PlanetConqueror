from config import *
import pygame


class GameScene:
    def __init__(self, level):
        self.planets = []
        self.selected_planet = None
        self.level = level
        self.info_bar_height = GAME_INFO_BAR_HEIGHT

    def add_planet(self, planet):
        self.planets.append(planet)

    def draw(self, surface):
        for planet in self.planets:
            for connected_cell in planet.connected_cells:
                pygame.draw.line(surface, CONNECTION_COLOR,
                                 (planet.center_x, planet.center_y),
                                 (connected_cell.center_x, connected_cell.center_y), 5)

        self.draw_ui(surface)

        # Draw all cells
        for planet in self.planets:
            planet.draw(surface, 0, self.info_bar_height)

    def draw_ui(self, surface):
        # Draw stage info
        font = pygame.font.SysFont('Arial', PLANET_TEXT_SIZE)
        stage_text = font.render(f"Level {self.level}", True, (255, 255, 255))
        surface.blit(stage_text, (20, 20))


    def handle_click(self, pos):
        for planet in self.planets:
            if planet.is_clicked(0, self.info_bar_height, pos):
                print(f"Clicked planet {planet}")
                if self.selected_planet is None:
                    self.selected_planet = planet
                    planet.selected = True
                    return True
                elif self.selected_planet != planet:
                    self.selected_planet.selected = False
                    self.selected_planet = None
                    return True
                else:
                    planet.selected = False
                    self.selected_planet = None
                    return True
        return False